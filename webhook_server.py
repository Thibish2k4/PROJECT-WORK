"""
Webhook Server Module
HTTP server that receives callbacks when honeytokens are used.
"""

import json
import os
from datetime import datetime
from typing import Dict
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import threading


class WebhookHandler(BaseHTTPRequestHandler):
    """Handle incoming webhook requests."""
    
    # Shared storage for webhook events
    events = []
    events_file = 'webhook_events.json'
    
    def _set_headers(self, status_code=200, content_type='application/json'):
        """Set response headers."""
        self.send_response(status_code)
        self.send_header('Content-Type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def _save_events(self):
        """Save events to file."""
        try:
            with open(self.events_file, 'w') as f:
                json.dump({'events': self.events}, f, indent=2)
        except Exception as e:
            print(f"Error saving events: {e}")
    
    def _load_events(self):
        """Load events from file."""
        if os.path.exists(self.events_file):
            try:
                with open(self.events_file, 'r') as f:
                    data = json.load(f)
                    self.events = data.get('events', [])
            except json.JSONDecodeError:
                self.events = []
    
    def do_OPTIONS(self):
        """Handle OPTIONS request (CORS preflight)."""
        self._set_headers(204)
    
    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/':
            # Root endpoint - show server info
            self._set_headers(200, 'text/html')
            response = """
            <html>
            <head>
                <title>Honeytoken Webhook Server</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; }
                    .status { color: green; font-weight: bold; }
                    .endpoint { background: #f0f0f0; padding: 10px; margin: 10px 0; }
                </style>
            </head>
            <body>
                <h1>🍯 Honeytoken Webhook Server</h1>
                <p class="status">Status: Running</p>
                
                <h2>Available Endpoints:</h2>
                <div class="endpoint">
                    <strong>POST /webhook</strong> - Receive honeytoken usage callbacks
                </div>
                <div class="endpoint">
                    <strong>GET /events</strong> - List recent webhook events
                </div>
                <div class="endpoint">
                    <strong>GET /health</strong> - Health check
                </div>
                <div class="endpoint">
                    <strong>POST /callback/:token_id</strong> - Token-specific callback
                </div>
                
                <h2>Usage:</h2>
                <pre>
curl -X POST http://localhost:8080/webhook \\
  -H "Content-Type: application/json" \\
  -d '{"token_id": "abc123", "event": "token_used"}'
                </pre>
            </body>
            </html>
            """
            self.wfile.write(response.encode())
        
        elif parsed_path.path == '/health':
            # Health check endpoint
            self._set_headers(200)
            response = {
                'status': 'healthy',
                'service': 'honeytoken-webhook-server',
                'timestamp': datetime.utcnow().isoformat(),
                'total_events': len(self.events)
            }
            self.wfile.write(json.dumps(response).encode())
        
        elif parsed_path.path == '/events':
            # List recent events
            self._load_events()
            query_params = parse_qs(parsed_path.query)
            limit = int(query_params.get('limit', [50])[0])
            
            self._set_headers(200)
            response = {
                'total_events': len(self.events),
                'events': self.events[-limit:]
            }
            self.wfile.write(json.dumps(response, indent=2).encode())
        
        else:
            # 404 Not Found
            self._set_headers(404)
            response = {'error': 'Endpoint not found'}
            self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        """Handle POST requests."""
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        parsed_path = urlparse(self.path)
        
        try:
            payload = json.loads(post_data.decode('utf-8'))
        except json.JSONDecodeError:
            self._set_headers(400)
            response = {'error': 'Invalid JSON payload'}
            self.wfile.write(json.dumps(response).encode())
            return
        
        # Process webhook based on path
        if parsed_path.path == '/webhook':
            self._handle_webhook(payload)
        elif parsed_path.path.startswith('/callback/'):
            token_id = parsed_path.path.split('/')[-1]
            self._handle_callback(token_id, payload)
        else:
            self._set_headers(404)
            response = {'error': 'Endpoint not found'}
            self.wfile.write(json.dumps(response).encode())
    
    def _handle_webhook(self, payload: Dict):
        """Handle general webhook."""
        event = {
            'event_id': datetime.utcnow().strftime('%Y%m%d%H%M%S%f'),
            'received_at': datetime.utcnow().isoformat(),
            'type': 'webhook',
            'payload': payload,
            'source_ip': self.client_address[0],
            'user_agent': self.headers.get('User-Agent', 'Unknown')
        }
        
        self.events.append(event)
        self._save_events()
        
        # Check if this is a honeytoken usage
        if payload.get('event') == 'token_used' or 'token_id' in payload:
            print(f"\n🚨 HONEYTOKEN DETECTED!")
            print(f"   Token ID: {payload.get('token_id', 'Unknown')}")
            print(f"   Time: {event['received_at']}")
            print(f"   Source: {event['source_ip']}")
            
            # Trigger alerts
            try:
                from alert_system import AlertSystem
                alert_system = AlertSystem()
                
                detection = {
                    'detected_at': event['received_at'],
                    'token_type': payload.get('token_type', 'unknown'),
                    'honeytoken_id': payload.get('token_id', 'unknown'),
                    'source': f"webhook from {event['source_ip']}",
                    'is_honeytoken': True
                }
                
                alert_system.send_all_alerts(detection)
            except Exception as e:
                print(f"   Error sending alerts: {e}")
        
        self._set_headers(200)
        response = {
            'success': True,
            'event_id': event['event_id'],
            'message': 'Webhook received successfully'
        }
        self.wfile.write(json.dumps(response).encode())
    
    def _handle_callback(self, token_id: str, payload: Dict):
        """Handle token-specific callback."""
        event = {
            'event_id': datetime.utcnow().strftime('%Y%m%d%H%M%S%f'),
            'received_at': datetime.utcnow().isoformat(),
            'type': 'callback',
            'token_id': token_id,
            'payload': payload,
            'source_ip': self.client_address[0],
            'user_agent': self.headers.get('User-Agent', 'Unknown')
        }
        
        self.events.append(event)
        self._save_events()
        
        print(f"\n🚨 HONEYTOKEN CALLBACK!")
        print(f"   Token ID: {token_id}")
        print(f"   Time: {event['received_at']}")
        print(f"   Source: {event['source_ip']}")
        
        # Trigger alerts
        try:
            from alert_system import AlertSystem
            alert_system = AlertSystem()
            
            detection = {
                'detected_at': event['received_at'],
                'token_type': payload.get('token_type', 'unknown'),
                'honeytoken_id': token_id,
                'source': f"callback from {event['source_ip']}",
                'is_honeytoken': True
            }
            
            alert_system.send_all_alerts(detection)
        except Exception as e:
            print(f"   Error sending alerts: {e}")
        
        self._set_headers(200)
        response = {
            'success': True,
            'event_id': event['event_id'],
            'token_id': token_id,
            'message': 'Callback received successfully'
        }
        self.wfile.write(json.dumps(response).encode())
    
    def log_message(self, format, *args):
        """Custom log message format."""
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        message = f"[{timestamp}] {self.address_string()} - {format % args}"
        print(message)


class WebhookServer:
    """Webhook server manager."""
    
    def __init__(self, host: str = '0.0.0.0', port: int = 8080):
        """Initialize webhook server."""
        self.host = host
        self.port = port
        self.server = None
        self.server_thread = None
    
    def start(self, background: bool = False):
        """Start the webhook server."""
        self.server = HTTPServer((self.host, self.port), WebhookHandler)
        
        print(f"\n🍯 Honeytoken Webhook Server")
        print(f"   Listening on http://{self.host}:{self.port}")
        print(f"   Press Ctrl+C to stop\n")
        
        if background:
            self.server_thread = threading.Thread(target=self.server.serve_forever)
            self.server_thread.daemon = True
            self.server_thread.start()
        else:
            try:
                self.server.serve_forever()
            except KeyboardInterrupt:
                print("\n\nShutting down webhook server...")
                self.stop()
    
    def stop(self):
        """Stop the webhook server."""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            print("Webhook server stopped")
    
    def is_running(self) -> bool:
        """Check if server is running."""
        return self.server is not None and (
            self.server_thread is None or self.server_thread.is_alive()
        )


def main():
    """CLI interface for webhook server."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Honeytoken Webhook Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8080, help='Port to bind to')
    parser.add_argument('--test', action='store_true', help='Send test webhook')
    parser.add_argument('--events', action='store_true', help='List recent events')
    
    args = parser.parse_args()
    
    if args.test:
        # Send test webhook
        import requests
        
        test_payload = {
            'event': 'token_used',
            'token_id': 'test_token_123',
            'token_type': 'github_pat',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        url = f'http://localhost:{args.port}/webhook'
        print(f"\nSending test webhook to {url}...")
        
        try:
            response = requests.post(url, json=test_payload, timeout=5)
            print(f"Response: {response.status_code}")
            print(f"Body: {response.text}")
        except Exception as e:
            print(f"Error: {e}")
    
    elif args.events:
        # List events
        events_file = 'webhook_events.json'
        if os.path.exists(events_file):
            with open(events_file, 'r') as f:
                data = json.load(f)
                events = data.get('events', [])
                print(f"\n=== Recent Webhook Events ({len(events)}) ===")
                for event in events[-10:]:
                    print(f"\nEvent ID: {event['event_id']}")
                    print(f"Type: {event['type']}")
                    print(f"Time: {event['received_at']}")
                    print(f"Source: {event['source_ip']}")
        else:
            print("No events found")
    
    else:
        # Start server
        server = WebhookServer(host=args.host, port=args.port)
        server.start()


if __name__ == '__main__':
    main()
