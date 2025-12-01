#!/usr/bin/env python3
"""
Honeytoken System Demo Launcher
Starts all components and opens dashboard for examiner presentation
"""

import subprocess
import time
import webbrowser
import sys
import os
from pathlib import Path

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    CYAN = '\033[96m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header():
    """Print welcome header"""
    print(f"\n{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.GREEN}  🍯 HONEYTOKEN DETECTION SYSTEM - DEMO LAUNCHER{Colors.END}")
    print(f"{Colors.CYAN}{'='*60}{Colors.END}\n")

def check_dependencies():
    """Check if required dependencies are installed"""
    print(f"{Colors.YELLOW}📦 Checking dependencies...{Colors.END}")
    
    try:
        import requests
        print(f"{Colors.GREEN}  ✓ requests installed{Colors.END}")
    except ImportError:
        print(f"{Colors.RED}  ✗ requests not installed{Colors.END}")
        print(f"{Colors.YELLOW}  Installing: pip install requests{Colors.END}")
        subprocess.run([sys.executable, "-m", "pip", "install", "requests"], 
                      capture_output=True)
    
    try:
        from dotenv import load_dotenv
        print(f"{Colors.GREEN}  ✓ python-dotenv installed{Colors.END}")
    except ImportError:
        print(f"{Colors.YELLOW}  ℹ python-dotenv not installed (optional){Colors.END}")
    
    print()

def generate_sample_data():
    """Generate sample honeytokens and scans for demo"""
    print(f"{Colors.YELLOW}🔑 Generating sample honeytokens...{Colors.END}")
    
    # Generate various token types
    commands = [
        [sys.executable, "src/honeytoken_generator.py", "--type", "github_pat", "--count", "10"],
        [sys.executable, "src/honeytoken_generator.py", "--type", "aws_access", "--count", "5"],
        [sys.executable, "src/honeytoken_generator.py", "--type", "slack", "--count", "3"],
    ]
    
    for cmd in commands:
        subprocess.run(cmd, capture_output=True, text=True)
    
    print(f"{Colors.GREEN}  ✓ Generated 18 honeytokens{Colors.END}")
    
    # Show stats
    result = subprocess.run(
        [sys.executable, "src/honeytoken_generator.py", "--stats"],
        capture_output=True,
        text=True
    )
    
    # Parse stats
    for line in result.stdout.split('\n'):
        if 'total_tokens:' in line:
            tokens = line.split(':')[1].strip()
            print(f"{Colors.GREEN}  📊 Total tokens in database: {tokens}{Colors.END}")
    
    print()

def create_demo_repository():
    """Create a demo repository with injected tokens"""
    print(f"{Colors.YELLOW}📁 Creating demo repository...{Colors.END}")
    
    # Remove old demo if exists
    demo_path = Path("demo-presentation")
    if demo_path.exists():
        import shutil
        shutil.rmtree(demo_path)
    
    # Create demo repo
    demo_path.mkdir(exist_ok=True)
    
    # Inject tokens
    subprocess.run(
        [sys.executable, "src/honeytoken_injector.py", "--inject-repo", "./demo-presentation"],
        capture_output=True
    )
    
    print(f"{Colors.GREEN}  ✓ Demo repository created: demo-presentation/{Colors.END}")
    print()

def run_scans():
    """Run scans to populate scan history"""
    print(f"{Colors.YELLOW}🔍 Running security scans...{Colors.END}")
    
    # Scan demo repository
    result = subprocess.run(
        [sys.executable, "src/token_scanner.py", "./demo-presentation"],
        capture_output=True,
        text=True
    )
    
    # Parse results
    for line in result.stdout.split('\n'):
        if 'Total findings:' in line or 'Honeytokens found:' in line:
            print(f"{Colors.GREEN}  {line.strip()}{Colors.END}")
    
    # Run workspace scan
    print(f"{Colors.YELLOW}  Running full workspace scan...{Colors.END}")
    subprocess.run(
        [sys.executable, "src/ci_scanner.py", "--scan-workspace", "--format", "json", 
         "--output-file", "config/latest-scan.json"],
        capture_output=True
    )
    
    print(f"{Colors.GREEN}  ✓ Scans completed{Colors.END}")
    print()

def generate_alerts():
    """Generate sample alert history"""
    print(f"{Colors.YELLOW}🔔 Generating alert history...{Colors.END}")
    
    import json
    from datetime import datetime, timedelta
    
    alerts = {
        'alerts': [
            {
                'alert_id': f'alert_{i}',
                'timestamp': (datetime.now() - timedelta(hours=i*2)).isoformat(),
                'alert_type': ['email', 'slack', 'discord', 'teams'][i % 4],
                'severity': 'critical' if i % 3 == 0 else 'warning',
                'message': f'Honeytoken detection alert #{i+1}',
                'token_type': ['github_pat', 'aws_access', 'slack'][i % 3],
                'success': True
            } for i in range(8)
        ]
    }
    
    with open('config/alert_history.json', 'w') as f:
        json.dump(alerts, f, indent=2)
    
    print(f"{Colors.GREEN}  ✓ Generated 8 sample alerts{Colors.END}")
    print()

def start_http_server():
    """Start HTTP server in background"""
    print(f"{Colors.YELLOW}🌐 Starting HTTP server...{Colors.END}")
    
    # Start server on port 8000
    server_process = subprocess.Popen(
        [sys.executable, "-m", "http.server", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for server to start
    time.sleep(2)
    
    print(f"{Colors.GREEN}  ✓ HTTP server running on http://localhost:8000{Colors.END}")
    print()
    
    return server_process

def open_dashboard():
    """Open dashboard in default browser"""
    print(f"{Colors.YELLOW}🎨 Opening dashboard...{Colors.END}")
    
    dashboard_url = "http://localhost:8000/web/dashboard.html"
    
    try:
        webbrowser.open(dashboard_url)
        print(f"{Colors.GREEN}  ✓ Dashboard opened in browser{Colors.END}")
        print(f"{Colors.CYAN}  🔗 {dashboard_url}{Colors.END}")
    except Exception as e:
        print(f"{Colors.RED}  ✗ Could not open browser automatically{Colors.END}")
        print(f"{Colors.YELLOW}  Please open: {dashboard_url}{Colors.END}")
    
    print()

def show_summary():
    """Show final summary"""
    print(f"\n{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.GREEN}  ✅ DEMO ENVIRONMENT READY!{Colors.END}")
    print(f"{Colors.CYAN}{'='*60}{Colors.END}\n")
    
    print(f"{Colors.BOLD}📊 System Status:{Colors.END}")
    
    # Read stats
    import json
    
    try:
        with open('config/honeytokens.json', 'r') as f:
            tokens_data = json.load(f)
            total_tokens = len(tokens_data.get('tokens', []))
            detected = len([t for t in tokens_data.get('tokens', []) if t.get('detected', False)])
        
        with open('config/scan_results.json', 'r') as f:
            scans_data = json.load(f)
            total_scans = len(scans_data.get('scans', []))
        
        with open('config/alert_history.json', 'r') as f:
            alerts_data = json.load(f)
            total_alerts = len(alerts_data.get('alerts', []))
        
        print(f"  🔑 Total Honeytokens: {Colors.GREEN}{total_tokens}{Colors.END}")
        print(f"  🚨 Detections: {Colors.RED if detected > 0 else Colors.GREEN}{detected}{Colors.END}")
        print(f"  🔍 Scans Completed: {Colors.YELLOW}{total_scans}{Colors.END}")
        print(f"  🔔 Alerts Generated: {Colors.GREEN}{total_alerts}{Colors.END}")
        
    except Exception as e:
        print(f"  {Colors.YELLOW}(Loading stats...){Colors.END}")
    
    print(f"\n{Colors.BOLD}🌐 Dashboard:{Colors.END}")
    print(f"  URL: {Colors.CYAN}http://localhost:8000/web/dashboard.html{Colors.END}")
    print(f"  Status: {Colors.GREEN}● LIVE{Colors.END}")
    
    print(f"\n{Colors.BOLD}🎓 For Examiner Demo:{Colors.END}")
    print(f"  1. Dashboard is now open in your browser")
    print(f"  2. Hover over stat cards to see animations")
    print(f"  3. Scroll through scan history and timeline")
    print(f"  4. Dashboard auto-refreshes every 30 seconds")
    print(f"  5. Press {Colors.YELLOW}Ctrl+C{Colors.END} when done to stop server")
    
    print(f"\n{Colors.BOLD}📝 Quick Commands:{Colors.END}")
    print(f"  python src/honeytoken_generator.py --stats")
    print(f"  python src/token_scanner.py --history")
    print(f"  python tests/test_suite.py")
    
    print(f"\n{Colors.CYAN}{'='*60}{Colors.END}\n")

def main():
    """Main demo launcher"""
    try:
        print_header()
        
        # Check dependencies
        check_dependencies()
        
        # Generate data
        generate_sample_data()
        create_demo_repository()
        run_scans()
        generate_alerts()
        
        # Start server
        server_process = start_http_server()
        
        # Open dashboard
        open_dashboard()
        
        # Show summary
        show_summary()
        
        # Keep server running
        print(f"{Colors.YELLOW}⏳ Server is running... Press Ctrl+C to stop{Colors.END}\n")
        
        try:
            server_process.wait()
        except KeyboardInterrupt:
            print(f"\n\n{Colors.YELLOW}🛑 Stopping server...{Colors.END}")
            server_process.terminate()
            server_process.wait()
            print(f"{Colors.GREEN}✓ Server stopped{Colors.END}")
            print(f"\n{Colors.CYAN}Thank you for using Honeytoken Detection System!{Colors.END}\n")
    
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}🛑 Demo cancelled{Colors.END}\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}❌ Error: {e}{Colors.END}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
