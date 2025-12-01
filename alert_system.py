"""
Alert System Module
Handles notifications for honeytoken detections via email and webhooks.
"""

import os
import json
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, List, Optional


class AlertSystem:
    """Send alerts for honeytoken detections."""
    
    def __init__(self, config_file: str = 'alert_config.json'):
        """Initialize alert system with configuration."""
        self.config_file = config_file
        self.config = self._load_config()
        self.alert_history = []
        self.alert_history_file = 'alert_history.json'
        self._load_history()
    
    def _load_config(self) -> Dict:
        """Load alert configuration."""
        default_config = {
            'email': {
                'enabled': False,
                'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
                'smtp_port': int(os.getenv('SMTP_PORT', '587')),
                'username': os.getenv('SMTP_USERNAME', ''),
                'password': os.getenv('SMTP_PASSWORD', ''),
                'from_address': os.getenv('SMTP_FROM', ''),
                'to_addresses': os.getenv('ALERT_EMAIL_TO', '').split(',')
            },
            'webhook': {
                'enabled': False,
                'urls': os.getenv('WEBHOOK_URLS', '').split(',')
            },
            'slack': {
                'enabled': False,
                'webhook_url': os.getenv('SLACK_WEBHOOK_URL', '')
            },
            'discord': {
                'enabled': False,
                'webhook_url': os.getenv('DISCORD_WEBHOOK_URL', '')
            },
            'teams': {
                'enabled': False,
                'webhook_url': os.getenv('TEAMS_WEBHOOK_URL', '')
            }
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults
                    for key in default_config:
                        if key in loaded_config:
                            default_config[key].update(loaded_config[key])
            except json.JSONDecodeError:
                pass
        
        return default_config
    
    def _load_history(self):
        """Load alert history."""
        if os.path.exists(self.alert_history_file):
            try:
                with open(self.alert_history_file, 'r') as f:
                    data = json.load(f)
                    self.alert_history = data.get('alerts', [])
            except json.JSONDecodeError:
                self.alert_history = []
    
    def _save_history(self):
        """Save alert history."""
        with open(self.alert_history_file, 'w') as f:
            json.dump({'alerts': self.alert_history}, f, indent=2)
    
    def _record_alert(self, alert_type: str, recipient: str, 
                     detection: Dict, success: bool, error: str = None):
        """Record an alert in history."""
        alert_record = {
            'timestamp': datetime.utcnow().isoformat(),
            'alert_type': alert_type,
            'recipient': recipient,
            'detection_id': detection.get('honeytoken_id', 'unknown'),
            'success': success,
            'error': error
        }
        self.alert_history.append(alert_record)
        self._save_history()
    
    def send_email_alert(self, detection: Dict) -> bool:
        """Send email alert for honeytoken detection."""
        if not self.config['email']['enabled']:
            return False
        
        config = self.config['email']
        
        # Create email
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"🚨 Honeytoken Detected: {detection.get('token_type', 'Unknown')}"
        msg['From'] = config['from_address']
        msg['To'] = ', '.join([addr.strip() for addr in config['to_addresses'] if addr.strip()])
        
        # Plain text version
        text_body = f"""
HONEYTOKEN DETECTION ALERT

Detection Time: {detection.get('detected_at', 'Unknown')}
Token Type: {detection.get('token_type', 'Unknown')}
Token ID: {detection.get('honeytoken_id', 'Unknown')}
Source: {detection.get('source', 'Unknown')}
Line Number: {detection.get('line_number', 'N/A')}

A honeytoken has been detected in your codebase. This indicates a potential
security breach or unauthorized access to sensitive credentials.

Recommended Actions:
1. Investigate the source of the leak immediately
2. Review access logs for any unauthorized usage
3. Rotate any potentially compromised credentials
4. Review security protocols

This is an automated alert from the Honeytoken Detection System.
"""
        
        # HTML version
        html_body = f"""
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
        .alert-box {{ background-color: #fff3cd; border: 2px solid #ffc107; 
                     padding: 20px; border-radius: 5px; }}
        .critical {{ color: #d32f2f; }}
        .info {{ color: #1976d2; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
        .label {{ font-weight: bold; width: 150px; }}
    </style>
</head>
<body>
    <div class="alert-box">
        <h2 class="critical">🚨 HONEYTOKEN DETECTION ALERT</h2>
        
        <table>
            <tr>
                <td class="label">Detection Time:</td>
                <td>{detection.get('detected_at', 'Unknown')}</td>
            </tr>
            <tr>
                <td class="label">Token Type:</td>
                <td>{detection.get('token_type', 'Unknown')}</td>
            </tr>
            <tr>
                <td class="label">Token ID:</td>
                <td><code>{detection.get('honeytoken_id', 'Unknown')}</code></td>
            </tr>
            <tr>
                <td class="label">Source:</td>
                <td><code>{detection.get('source', 'Unknown')}</code></td>
            </tr>
            <tr>
                <td class="label">Line Number:</td>
                <td>{detection.get('line_number', 'N/A')}</td>
            </tr>
        </table>
        
        <h3 class="info">What is a Honeytoken?</h3>
        <p>A honeytoken is a deliberately planted credential designed to detect 
        unauthorized access or data leaks.</p>
        
        <h3 class="critical">Recommended Actions:</h3>
        <ol>
            <li>Investigate the source of the leak immediately</li>
            <li>Review access logs for any unauthorized usage</li>
            <li>Rotate any potentially compromised credentials</li>
            <li>Review and update security protocols</li>
        </ol>
        
        <p><em>This is an automated alert from the Honeytoken Detection System.</em></p>
    </div>
</body>
</html>
"""
        
        msg.attach(MIMEText(text_body, 'plain'))
        msg.attach(MIMEText(html_body, 'html'))
        
        # Send email
        try:
            with smtplib.SMTP(config['smtp_server'], config['smtp_port']) as server:
                server.starttls()
                server.login(config['username'], config['password'])
                server.send_message(msg)
            
            self._record_alert('email', msg['To'], detection, True)
            return True
        
        except Exception as e:
            self._record_alert('email', msg['To'], detection, False, str(e))
            print(f"Error sending email alert: {e}")
            return False
    
    def send_webhook_alert(self, detection: Dict) -> List[bool]:
        """Send webhook alerts."""
        if not self.config['webhook']['enabled']:
            return []
        
        urls = [url.strip() for url in self.config['webhook']['urls'] if url.strip()]
        results = []
        
        payload = {
            'event': 'honeytoken_detected',
            'timestamp': datetime.utcnow().isoformat(),
            'detection': detection
        }
        
        for url in urls:
            try:
                response = requests.post(
                    url,
                    json=payload,
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )
                success = response.status_code in [200, 201, 202, 204]
                results.append(success)
                self._record_alert('webhook', url, detection, success, 
                                 None if success else f"HTTP {response.status_code}")
            except Exception as e:
                results.append(False)
                self._record_alert('webhook', url, detection, False, str(e))
                print(f"Error sending webhook to {url}: {e}")
        
        return results
    
    def send_slack_alert(self, detection: Dict) -> bool:
        """Send Slack notification."""
        if not self.config['slack']['enabled']:
            return False
        
        webhook_url = self.config['slack']['webhook_url']
        
        payload = {
            'text': '🚨 *HONEYTOKEN DETECTION ALERT*',
            'blocks': [
                {
                    'type': 'header',
                    'text': {
                        'type': 'plain_text',
                        'text': '🚨 Honeytoken Detected'
                    }
                },
                {
                    'type': 'section',
                    'fields': [
                        {
                            'type': 'mrkdwn',
                            'text': f"*Token Type:*\n{detection.get('token_type', 'Unknown')}"
                        },
                        {
                            'type': 'mrkdwn',
                            'text': f"*Token ID:*\n`{detection.get('honeytoken_id', 'Unknown')}`"
                        },
                        {
                            'type': 'mrkdwn',
                            'text': f"*Source:*\n`{detection.get('source', 'Unknown')}`"
                        },
                        {
                            'type': 'mrkdwn',
                            'text': f"*Line:*\n{detection.get('line_number', 'N/A')}"
                        }
                    ]
                },
                {
                    'type': 'context',
                    'elements': [
                        {
                            'type': 'mrkdwn',
                            'text': f"Detected at {detection.get('detected_at', 'Unknown')}"
                        }
                    ]
                }
            ]
        }
        
        try:
            response = requests.post(webhook_url, json=payload, timeout=10)
            success = response.status_code == 200
            self._record_alert('slack', webhook_url, detection, success, 
                             None if success else f"HTTP {response.status_code}")
            return success
        except Exception as e:
            self._record_alert('slack', webhook_url, detection, False, str(e))
            print(f"Error sending Slack alert: {e}")
            return False
    
    def send_discord_alert(self, detection: Dict) -> bool:
        """Send Discord notification."""
        if not self.config['discord']['enabled']:
            return False
        
        webhook_url = self.config['discord']['webhook_url']
        
        payload = {
            'embeds': [{
                'title': '🚨 Honeytoken Detected',
                'color': 16711680,  # Red
                'fields': [
                    {
                        'name': 'Token Type',
                        'value': detection.get('token_type', 'Unknown'),
                        'inline': True
                    },
                    {
                        'name': 'Token ID',
                        'value': f"`{detection.get('honeytoken_id', 'Unknown')}`",
                        'inline': True
                    },
                    {
                        'name': 'Source',
                        'value': f"`{detection.get('source', 'Unknown')}`",
                        'inline': False
                    },
                    {
                        'name': 'Line Number',
                        'value': str(detection.get('line_number', 'N/A')),
                        'inline': True
                    }
                ],
                'footer': {
                    'text': f"Detected at {detection.get('detected_at', 'Unknown')}"
                }
            }]
        }
        
        try:
            response = requests.post(webhook_url, json=payload, timeout=10)
            success = response.status_code in [200, 204]
            self._record_alert('discord', webhook_url, detection, success, 
                             None if success else f"HTTP {response.status_code}")
            return success
        except Exception as e:
            self._record_alert('discord', webhook_url, detection, False, str(e))
            print(f"Error sending Discord alert: {e}")
            return False
    
    def send_teams_alert(self, detection: Dict) -> bool:
        """Send Microsoft Teams notification."""
        if not self.config['teams']['enabled']:
            return False
        
        webhook_url = self.config['teams']['webhook_url']
        
        payload = {
            '@type': 'MessageCard',
            '@context': 'http://schema.org/extensions',
            'themeColor': 'FF0000',
            'summary': 'Honeytoken Detected',
            'sections': [{
                'activityTitle': '🚨 Honeytoken Detection Alert',
                'facts': [
                    {
                        'name': 'Token Type:',
                        'value': detection.get('token_type', 'Unknown')
                    },
                    {
                        'name': 'Token ID:',
                        'value': detection.get('honeytoken_id', 'Unknown')
                    },
                    {
                        'name': 'Source:',
                        'value': detection.get('source', 'Unknown')
                    },
                    {
                        'name': 'Line:',
                        'value': str(detection.get('line_number', 'N/A'))
                    },
                    {
                        'name': 'Detected At:',
                        'value': detection.get('detected_at', 'Unknown')
                    }
                ],
                'markdown': True
            }]
        }
        
        try:
            response = requests.post(webhook_url, json=payload, timeout=10)
            success = response.status_code == 200
            self._record_alert('teams', webhook_url, detection, success, 
                             None if success else f"HTTP {response.status_code}")
            return success
        except Exception as e:
            self._record_alert('teams', webhook_url, detection, False, str(e))
            print(f"Error sending Teams alert: {e}")
            return False
    
    def send_all_alerts(self, detection: Dict) -> Dict[str, bool]:
        """Send alerts through all enabled channels."""
        results = {
            'email': False,
            'webhook': False,
            'slack': False,
            'discord': False,
            'teams': False
        }
        
        if self.config['email']['enabled']:
            results['email'] = self.send_email_alert(detection)
        
        if self.config['webhook']['enabled']:
            webhook_results = self.send_webhook_alert(detection)
            results['webhook'] = any(webhook_results) if webhook_results else False
        
        if self.config['slack']['enabled']:
            results['slack'] = self.send_slack_alert(detection)
        
        if self.config['discord']['enabled']:
            results['discord'] = self.send_discord_alert(detection)
        
        if self.config['teams']['enabled']:
            results['teams'] = self.send_teams_alert(detection)
        
        return results
    
    def get_alert_history(self, limit: int = 50) -> List[Dict]:
        """Get recent alert history."""
        return self.alert_history[-limit:]
    
    def get_alert_statistics(self) -> Dict:
        """Get alert statistics."""
        total = len(self.alert_history)
        if total == 0:
            return {
                'total_alerts': 0,
                'successful_alerts': 0,
                'failed_alerts': 0,
                'success_rate': 0
            }
        
        successful = sum(1 for alert in self.alert_history if alert['success'])
        
        return {
            'total_alerts': total,
            'successful_alerts': successful,
            'failed_alerts': total - successful,
            'success_rate': successful / total if total > 0 else 0
        }


def main():
    """CLI interface for alert system."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Alert System')
    parser.add_argument('--test-email', action='store_true', help='Send test email')
    parser.add_argument('--test-slack', action='store_true', help='Send test Slack')
    parser.add_argument('--test-discord', action='store_true', help='Send test Discord')
    parser.add_argument('--test-webhook', action='store_true', help='Send test webhook')
    parser.add_argument('--history', action='store_true', help='Show alert history')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    
    args = parser.parse_args()
    
    alert_system = AlertSystem()
    
    # Test detection payload
    test_detection = {
        'detected_at': datetime.utcnow().isoformat(),
        'token_type': 'github_pat',
        'honeytoken_id': 'test_honeytoken_123',
        'source': 'test_file.py',
        'line_number': 42,
        'is_honeytoken': True
    }
    
    if args.test_email:
        print("\nSending test email alert...")
        success = alert_system.send_email_alert(test_detection)
        print(f"Email sent: {success}")
    
    elif args.test_slack:
        print("\nSending test Slack alert...")
        success = alert_system.send_slack_alert(test_detection)
        print(f"Slack alert sent: {success}")
    
    elif args.test_discord:
        print("\nSending test Discord alert...")
        success = alert_system.send_discord_alert(test_detection)
        print(f"Discord alert sent: {success}")
    
    elif args.test_webhook:
        print("\nSending test webhook alert...")
        results = alert_system.send_webhook_alert(test_detection)
        print(f"Webhook results: {results}")
    
    elif args.history:
        history = alert_system.get_alert_history(limit=10)
        print(f"\n=== Alert History ({len(history)}) ===")
        for alert in history:
            status = "✓" if alert['success'] else "✗"
            print(f"\n{status} {alert['timestamp']}")
            print(f"  Type: {alert['alert_type']}")
            print(f"  Recipient: {alert['recipient']}")
            if alert.get('error'):
                print(f"  Error: {alert['error']}")
    
    elif args.stats:
        stats = alert_system.get_alert_statistics()
        print("\n=== Alert Statistics ===")
        for key, value in stats.items():
            print(f"{key}: {value}")
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
