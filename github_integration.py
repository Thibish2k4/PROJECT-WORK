"""
GitHub Integration Module
Handles GitHub API interactions for repository management and scanning.
"""

import os
import json
import requests
from typing import List, Dict, Optional
from datetime import datetime
import base64


class GitHubIntegration:
    """GitHub API integration for token management and scanning."""
    
    def __init__(self, token: str = None):
        """Initialize with GitHub API token."""
        self.token = token or os.getenv('GITHUB_TOKEN')
        if not self.token:
            raise ValueError("GitHub token required. Set GITHUB_TOKEN env var.")
        
        self.base_url = 'https://api.github.com'
        self.headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        }
    
    def test_connection(self) -> Dict:
        """Test GitHub API connection."""
        try:
            response = requests.get(f'{self.base_url}/user', headers=self.headers)
            response.raise_for_status()
            user_data = response.json()
            return {
                'success': True,
                'user': user_data.get('login'),
                'name': user_data.get('name'),
                'type': user_data.get('type')
            }
        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': str(e)}
    
    def list_repositories(self, user: str = None, org: str = None) -> List[Dict]:
        """List repositories for a user or organization."""
        if org:
            url = f'{self.base_url}/orgs/{org}/repos'
        elif user:
            url = f'{self.base_url}/users/{user}/repos'
        else:
            url = f'{self.base_url}/user/repos'
        
        try:
            repos = []
            page = 1
            while True:
                response = requests.get(
                    url,
                    headers=self.headers,
                    params={'page': page, 'per_page': 100}
                )
                response.raise_for_status()
                page_repos = response.json()
                
                if not page_repos:
                    break
                
                repos.extend([{
                    'name': repo['name'],
                    'full_name': repo['full_name'],
                    'private': repo['private'],
                    'html_url': repo['html_url'],
                    'default_branch': repo['default_branch']
                } for repo in page_repos])
                
                page += 1
                if len(page_repos) < 100:
                    break
            
            return repos
        except requests.exceptions.RequestException as e:
            print(f"Error listing repositories: {e}")
            return []
    
    def get_repository_contents(self, owner: str, repo: str, 
                                path: str = '', branch: str = None) -> List[Dict]:
        """Get contents of a repository path."""
        url = f'{self.base_url}/repos/{owner}/{repo}/contents/{path}'
        params = {}
        if branch:
            params['ref'] = branch
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting repository contents: {e}")
            return []
    
    def get_file_content(self, owner: str, repo: str, file_path: str, 
                        branch: str = None) -> Optional[str]:
        """Get content of a specific file."""
        url = f'{self.base_url}/repos/{owner}/{repo}/contents/{file_path}'
        params = {}
        if branch:
            params['ref'] = branch
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            content_data = response.json()
            
            if content_data.get('encoding') == 'base64':
                content = base64.b64decode(content_data['content']).decode('utf-8')
                return content
            
            return None
        except requests.exceptions.RequestException as e:
            print(f"Error getting file content: {e}")
            return None
    
    def scan_repository_for_tokens(self, owner: str, repo: str, 
                                   scanner) -> Dict:
        """Scan a GitHub repository for tokens."""
        findings = []
        scanned_files = []
        errors = []
        
        def scan_directory(path: str = ''):
            """Recursively scan directory."""
            contents = self.get_repository_contents(owner, repo, path)
            
            for item in contents:
                if item['type'] == 'file':
                    # Check if file should be scanned
                    if scanner.should_scan_file(item['name']):
                        try:
                            content = self.get_file_content(owner, repo, item['path'])
                            if content:
                                file_findings = scanner.scan_text(
                                    content, 
                                    source=f"{owner}/{repo}/{item['path']}"
                                )
                                if file_findings:
                                    findings.extend(file_findings)
                                scanned_files.append(item['path'])
                        except Exception as e:
                            errors.append({
                                'file': item['path'],
                                'error': str(e)
                            })
                
                elif item['type'] == 'dir':
                    scan_directory(item['path'])
        
        try:
            scan_directory()
        except Exception as e:
            errors.append({'error': f"Repository scan failed: {str(e)}"})
        
        return {
            'scan_id': datetime.utcnow().strftime('%Y%m%d%H%M%S'),
            'repository': f"{owner}/{repo}",
            'scanned_at': datetime.utcnow().isoformat(),
            'files_scanned': len(scanned_files),
            'total_findings': len(findings),
            'honeytokens_found': sum(1 for f in findings if f.get('is_honeytoken')),
            'findings': findings,
            'errors': errors
        }
    
    def create_repository_secret(self, owner: str, repo: str, 
                                 secret_name: str, secret_value: str) -> bool:
        """Create or update a repository secret (requires admin access)."""
        # First, get the repository public key
        url = f'{self.base_url}/repos/{owner}/{repo}/actions/secrets/public-key'
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            public_key_data = response.json()
            
            # Encrypt the secret (requires PyNaCl library)
            try:
                from nacl import encoding, public
                
                public_key = public.PublicKey(
                    public_key_data['key'].encode('utf-8'),
                    encoding.Base64Encoder()
                )
                sealed_box = public.SealedBox(public_key)
                encrypted = sealed_box.encrypt(secret_value.encode('utf-8'))
                encrypted_value = base64.b64encode(encrypted).decode('utf-8')
            except ImportError:
                print("PyNaCl library required for secret encryption")
                return False
            
            # Create/update the secret
            url = f'{self.base_url}/repos/{owner}/{repo}/actions/secrets/{secret_name}'
            data = {
                'encrypted_value': encrypted_value,
                'key_id': public_key_data['key_id']
            }
            
            response = requests.put(url, headers=self.headers, json=data)
            response.raise_for_status()
            return True
        
        except requests.exceptions.RequestException as e:
            print(f"Error creating repository secret: {e}")
            return False
    
    def list_repository_secrets(self, owner: str, repo: str) -> List[str]:
        """List repository secret names."""
        url = f'{self.base_url}/repos/{owner}/{repo}/actions/secrets'
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            secrets_data = response.json()
            return [secret['name'] for secret in secrets_data.get('secrets', [])]
        except requests.exceptions.RequestException as e:
            print(f"Error listing repository secrets: {e}")
            return []
    
    def create_issue(self, owner: str, repo: str, title: str, 
                    body: str, labels: List[str] = None) -> Optional[Dict]:
        """Create an issue in a repository."""
        url = f'{self.base_url}/repos/{owner}/{repo}/issues'
        
        data = {
            'title': title,
            'body': body
        }
        
        if labels:
            data['labels'] = labels
        
        try:
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            issue = response.json()
            return {
                'number': issue['number'],
                'html_url': issue['html_url'],
                'state': issue['state']
            }
        except requests.exceptions.RequestException as e:
            print(f"Error creating issue: {e}")
            return None
    
    def create_honeytoken_detection_issue(self, owner: str, repo: str, 
                                         detection: Dict) -> Optional[Dict]:
        """Create an issue for honeytoken detection."""
        title = f"🚨 Honeytoken Detected: {detection.get('token_type', 'Unknown')}"
        
        body = f"""# Honeytoken Detection Alert
        
**Detection Time:** {detection.get('detected_at', 'Unknown')}
**Token Type:** {detection.get('token_type', 'Unknown')}
**Token ID:** {detection.get('honeytoken_id', 'Unknown')}
**Source:** {detection.get('source', 'Unknown')}
**Line Number:** {detection.get('line_number', 'N/A')}

## What is a Honeytoken?
A honeytoken is a deliberately planted credential designed to detect unauthorized access or data leaks.

## Recommended Actions:
1. Investigate how this token was exposed
2. Review access logs for any unauthorized usage
3. Check for other potential leaks
4. Update security protocols if needed

**This is an automated alert from the Honeytoken Detection System.**
"""
        
        return self.create_issue(
            owner, repo, title, body, 
            labels=['security', 'honeytoken', 'alert']
        )
    
    def search_code(self, query: str, owner: str = None, 
                   repo: str = None) -> List[Dict]:
        """Search for code in GitHub."""
        search_query = query
        if owner and repo:
            search_query += f" repo:{owner}/{repo}"
        elif owner:
            search_query += f" user:{owner}"
        
        url = f'{self.base_url}/search/code'
        
        try:
            response = requests.get(
                url,
                headers=self.headers,
                params={'q': search_query, 'per_page': 100}
            )
            response.raise_for_status()
            results = response.json()
            
            return [{
                'name': item['name'],
                'path': item['path'],
                'repository': item['repository']['full_name'],
                'html_url': item['html_url']
            } for item in results.get('items', [])]
        
        except requests.exceptions.RequestException as e:
            print(f"Error searching code: {e}")
            return []


def main():
    """CLI interface for GitHub integration."""
    import argparse
    
    parser = argparse.ArgumentParser(description='GitHub Integration')
    parser.add_argument('--test', action='store_true', help='Test connection')
    parser.add_argument('--list-repos', action='store_true', help='List repositories')
    parser.add_argument('--scan-repo', nargs=2, metavar=('OWNER', 'REPO'),
                       help='Scan a repository')
    parser.add_argument('--list-secrets', nargs=2, metavar=('OWNER', 'REPO'),
                       help='List repository secrets')
    
    args = parser.parse_args()
    
    try:
        gh = GitHubIntegration()
        
        if args.test:
            result = gh.test_connection()
            if result['success']:
                print(f"\n✓ Connected as: {result['user']}")
                print(f"  Name: {result.get('name', 'N/A')}")
                print(f"  Type: {result.get('type', 'N/A')}")
            else:
                print(f"\n✗ Connection failed: {result['error']}")
        
        elif args.list_repos:
            repos = gh.list_repositories()
            print(f"\n=== Repositories ({len(repos)}) ===")
            for repo in repos[:20]:  # Show first 20
                privacy = "🔒" if repo['private'] else "🌐"
                print(f"{privacy} {repo['full_name']}")
        
        elif args.scan_repo:
            from token_scanner import TokenScanner
            scanner = TokenScanner()
            
            owner, repo = args.scan_repo
            print(f"\nScanning {owner}/{repo}...")
            result = gh.scan_repository_for_tokens(owner, repo, scanner)
            
            print(f"\n=== Scan Results ===")
            print(f"Files scanned: {result['files_scanned']}")
            print(f"Total findings: {result['total_findings']}")
            print(f"Honeytokens: {result['honeytokens_found']}")
        
        elif args.list_secrets:
            owner, repo = args.list_secrets
            secrets = gh.list_repository_secrets(owner, repo)
            print(f"\n=== Secrets in {owner}/{repo} ({len(secrets)}) ===")
            for secret in secrets:
                print(f"  - {secret}")
        
        else:
            parser.print_help()
    
    except ValueError as e:
        print(f"Error: {e}")


if __name__ == '__main__':
    main()
