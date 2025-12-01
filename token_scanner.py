"""
Token Scanner Module
Scans files and repositories for leaked tokens using regex patterns.
"""

import re
import os
import json
from datetime import datetime
from typing import List, Dict, Tuple
from pathlib import Path


class TokenScanner:
    """Scanner for detecting tokens using regex patterns (no ML)."""
    
    # Regex patterns for various token types
    PATTERNS = {
        'github_pat': r'ghp_[a-zA-Z0-9]{36}',
        'github_oauth': r'gho_[a-zA-Z0-9]{36}',
        'github_app': r'ghs_[a-zA-Z0-9]{36}',
        'github_refresh': r'ghr_[a-zA-Z0-9]{36}',
        'github_fine_grained': r'github_pat_[a-zA-Z0-9]{22}_[a-zA-Z0-9]{59}',
        'aws_access_key': r'AKIA[0-9A-Z]{16}',
        'aws_secret_key': r'(?i)aws(.{0,20})?[\'"][0-9a-zA-Z/+]{40}[\'"]',
        'slack_token': r'xoxb-[0-9]{11}-[0-9]{11}-[a-zA-Z0-9]{24}',
        'slack_webhook': r'https://hooks\.slack\.com/services/T[a-zA-Z0-9_]{8}/B[a-zA-Z0-9_]{8}/[a-zA-Z0-9_]{24}',
        'stripe_key': r'sk_live_[0-9a-zA-Z]{24}',
        'stripe_restricted': r'rk_live_[0-9a-zA-Z]{24}',
        'google_api': r'AIza[0-9A-Za-z\\-_]{35}',
        'google_oauth': r'ya29\.[0-9A-Za-z\-_]+',
        'private_key': r'-----BEGIN (RSA |EC )?PRIVATE KEY-----',
        'generic_api_key': r'(?i)(api[_-]?key|apikey|access[_-]?token)["\']?\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,})["\']',
        'generic_secret': r'(?i)(secret|password|passwd|pwd)["\']?\s*[:=]\s*["\']([^"\']{8,})["\']',
        'jwt_token': r'eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*',
        'azure_pat': r'[a-z0-9]{52}',
        'npm_token': r'npm_[a-zA-Z0-9]{36}',
        'docker_auth': r'"auth":\s*"[a-zA-Z0-9+/=]{40,}"',
    }
    
    # File extensions to scan
    SCANNABLE_EXTENSIONS = {
        '.py', '.js', '.ts', '.java', '.go', '.rb', '.php', '.sh', '.bash',
        '.env', '.config', '.conf', '.yml', '.yaml', '.json', '.xml',
        '.txt', '.md', '.rst', '.ini', '.cfg', '.properties', '.toml',
        '.c', '.cpp', '.h', '.cs', '.swift', '.kt', '.rs', '.scala'
    }
    
    # Paths to exclude from scanning
    EXCLUDE_PATHS = {
        '.git', 'node_modules', '__pycache__', '.venv', 'venv',
        'env', 'dist', 'build', '.pytest_cache', '.mypy_cache',
        'vendor', 'target', 'bin', 'obj', '.idea', '.vscode'
    }
    
    def __init__(self, honeytokens_file: str = 'honeytokens.json',
                 scan_results_file: str = 'scan_results.json'):
        """Initialize the scanner."""
        self.honeytokens_file = honeytokens_file
        self.scan_results_file = scan_results_file
        self.honeytokens = self._load_honeytokens()
        self.scan_results = self._load_scan_results()
    
    def _load_honeytokens(self) -> Dict:
        """Load honeytokens for comparison."""
        if os.path.exists(self.honeytokens_file):
            try:
                with open(self.honeytokens_file, 'r') as f:
                    data = json.load(f)
                    return {token['token_value']: token for token in data.get('tokens', [])}
            except json.JSONDecodeError:
                return {}
        return {}
    
    def _load_scan_results(self) -> List[Dict]:
        """Load previous scan results."""
        if os.path.exists(self.scan_results_file):
            try:
                with open(self.scan_results_file, 'r') as f:
                    return json.load(f).get('scans', [])
            except json.JSONDecodeError:
                return []
        return []
    
    def _save_scan_results(self):
        """Save scan results to file."""
        with open(self.scan_results_file, 'w') as f:
            json.dump({'scans': self.scan_results}, f, indent=2)
    
    def should_scan_file(self, file_path: str) -> bool:
        """Check if a file should be scanned."""
        path = Path(file_path)
        
        # Check file extension
        if path.suffix.lower() not in self.SCANNABLE_EXTENSIONS and path.suffix != '':
            return False
        
        # Check excluded directories
        for part in path.parts:
            if part in self.EXCLUDE_PATHS:
                return False
        
        # Check file size (skip files larger than 10MB)
        try:
            if os.path.getsize(file_path) > 10 * 1024 * 1024:
                return False
        except OSError:
            return False
        
        return True
    
    def scan_text(self, text: str, source: str = 'unknown') -> List[Dict]:
        """Scan text content for tokens."""
        findings = []
        
        for token_type, pattern in self.PATTERNS.items():
            matches = re.finditer(pattern, text)
            for match in matches:
                token_value = match.group(0)
                
                # Check if it's a honeytoken
                is_honeytoken = token_value in self.honeytokens
                
                finding = {
                    'token_type': token_type,
                    'token_value': token_value,
                    'token_preview': token_value[:20] + '...' if len(token_value) > 20 else token_value,
                    'source': source,
                    'position': match.start(),
                    'line_number': text[:match.start()].count('\n') + 1,
                    'is_honeytoken': is_honeytoken,
                    'honeytoken_id': self.honeytokens[token_value]['token_id'] if is_honeytoken else None,
                    'detected_at': datetime.utcnow().isoformat(),
                }
                
                findings.append(finding)
        
        return findings
    
    def scan_file(self, file_path: str) -> Tuple[List[Dict], Dict]:
        """Scan a single file for tokens."""
        if not self.should_scan_file(file_path):
            return [], {'skipped': True, 'reason': 'File excluded or too large'}
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            return [], {'error': str(e)}
        
        findings = self.scan_text(content, source=file_path)
        
        metadata = {
            'file_path': file_path,
            'file_size': os.path.getsize(file_path),
            'findings_count': len(findings),
            'scanned_at': datetime.utcnow().isoformat()
        }
        
        return findings, metadata
    
    def scan_directory(self, directory: str, recursive: bool = True) -> Dict:
        """Scan an entire directory for tokens."""
        all_findings = []
        scanned_files = []
        skipped_files = []
        errors = []
        
        if recursive:
            file_iterator = Path(directory).rglob('*')
        else:
            file_iterator = Path(directory).glob('*')
        
        for file_path in file_iterator:
            if file_path.is_file():
                file_path_str = str(file_path)
                
                if not self.should_scan_file(file_path_str):
                    skipped_files.append(file_path_str)
                    continue
                
                findings, metadata = self.scan_file(file_path_str)
                
                if 'error' in metadata:
                    errors.append({'file': file_path_str, 'error': metadata['error']})
                elif 'skipped' not in metadata:
                    scanned_files.append(file_path_str)
                    if findings:
                        all_findings.extend(findings)
        
        scan_result = {
            'scan_id': datetime.utcnow().strftime('%Y%m%d%H%M%S'),
            'scan_type': 'directory',
            'target': directory,
            'recursive': recursive,
            'started_at': datetime.utcnow().isoformat(),
            'total_files_scanned': len(scanned_files),
            'total_files_skipped': len(skipped_files),
            'total_findings': len(all_findings),
            'honeytokens_found': sum(1 for f in all_findings if f['is_honeytoken']),
            'findings': all_findings,
            'scanned_files': scanned_files[:100],  # Limit to first 100
            'errors': errors
        }
        
        self.scan_results.append(scan_result)
        self._save_scan_results()
        
        return scan_result
    
    def scan_repository(self, repo_path: str) -> Dict:
        """Scan a Git repository."""
        return self.scan_directory(repo_path, recursive=True)
    
    def scan_string(self, text: str, identifier: str = 'string') -> Dict:
        """Scan a string for tokens."""
        findings = self.scan_text(text, source=identifier)
        
        scan_result = {
            'scan_id': datetime.utcnow().strftime('%Y%m%d%H%M%S'),
            'scan_type': 'string',
            'target': identifier,
            'started_at': datetime.utcnow().isoformat(),
            'total_findings': len(findings),
            'honeytokens_found': sum(1 for f in findings if f['is_honeytoken']),
            'findings': findings
        }
        
        self.scan_results.append(scan_result)
        self._save_scan_results()
        
        return scan_result
    
    def get_scan_history(self, limit: int = 10) -> List[Dict]:
        """Get recent scan history."""
        return self.scan_results[-limit:]
    
    def get_honeytoken_detections(self) -> List[Dict]:
        """Get all detections of honeytokens."""
        detections = []
        for scan in self.scan_results:
            for finding in scan.get('findings', []):
                if finding.get('is_honeytoken'):
                    detections.append({
                        'scan_id': scan['scan_id'],
                        'detected_at': finding['detected_at'],
                        'token_type': finding['token_type'],
                        'honeytoken_id': finding['honeytoken_id'],
                        'source': finding['source'],
                        'line_number': finding.get('line_number')
                    })
        return detections


def main():
    """CLI interface for the token scanner."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Scan for leaked tokens')
    parser.add_argument('target', nargs='?', help='File or directory to scan')
    parser.add_argument('--text', help='Scan text directly')
    parser.add_argument('--history', action='store_true', help='Show scan history')
    parser.add_argument('--detections', action='store_true', help='Show honeytoken detections')
    parser.add_argument('--recursive', action='store_true', default=True,
                       help='Recursively scan directories')
    
    args = parser.parse_args()
    
    scanner = TokenScanner()
    
    if args.history:
        history = scanner.get_scan_history(limit=5)
        print(f"\n=== Recent Scans ({len(history)}) ===")
        for scan in history:
            print(f"\nScan ID: {scan['scan_id']}")
            print(f"Type: {scan['scan_type']}")
            print(f"Target: {scan['target']}")
            print(f"Findings: {scan['total_findings']} (Honeytokens: {scan.get('honeytokens_found', 0)})")
    elif args.detections:
        detections = scanner.get_honeytoken_detections()
        print(f"\n=== Honeytoken Detections ({len(detections)}) ===")
        for detection in detections:
            print(f"\nDetected at: {detection['detected_at']}")
            print(f"Token ID: {detection['honeytoken_id']}")
            print(f"Source: {detection['source']}")
            print(f"Line: {detection.get('line_number', 'N/A')}")
    elif args.text:
        result = scanner.scan_string(args.text)
        print(f"\n=== Scan Results ===")
        print(f"Total findings: {result['total_findings']}")
        print(f"Honeytokens: {result['honeytokens_found']}")
        for finding in result['findings']:
            print(f"\n- Type: {finding['token_type']}")
            print(f"  Value: {finding['token_preview']}")
            print(f"  Honeytoken: {finding['is_honeytoken']}")
    elif args.target:
        if os.path.isfile(args.target):
            findings, metadata = scanner.scan_file(args.target)
            print(f"\n=== File Scan: {args.target} ===")
            print(f"Findings: {len(findings)}")
            for finding in findings:
                print(f"\n- Type: {finding['token_type']}")
                print(f"  Line: {finding['line_number']}")
                print(f"  Value: {finding['token_preview']}")
                print(f"  Honeytoken: {finding['is_honeytoken']}")
        elif os.path.isdir(args.target):
            result = scanner.scan_directory(args.target, args.recursive)
            print(f"\n=== Directory Scan: {args.target} ===")
            print(f"Files scanned: {result['total_files_scanned']}")
            print(f"Files skipped: {result['total_files_skipped']}")
            print(f"Total findings: {result['total_findings']}")
            print(f"Honeytokens found: {result['honeytokens_found']}")
            
            if result['findings']:
                print("\n--- Findings ---")
                for finding in result['findings'][:10]:  # Show first 10
                    print(f"\n- {finding['token_type']} in {finding['source']}")
                    print(f"  Line: {finding['line_number']}")
                    print(f"  Honeytoken: {finding['is_honeytoken']}")
        else:
            print(f"Error: {args.target} is not a valid file or directory")
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
