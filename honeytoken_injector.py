"""
Honeytoken Injector Module
Injects honeytokens into repositories and CI/CD environments.
"""

import os
import json
import random
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path


class HoneytokenInjector:
    """Inject honeytokens into code repositories and CI systems."""
    
    # Common file locations for injecting honeytokens
    INJECTION_TEMPLATES = {
        'env_file': {
            'filename': '.env.example',
            'template': '{key}={value}\n',
            'keys': ['API_KEY', 'SECRET_TOKEN', 'GITHUB_TOKEN', 'AWS_ACCESS_KEY']
        },
        'config_file': {
            'filename': 'config.json',
            'template': '{{\n  "{key}": "{value}"\n}}\n',
            'keys': ['apiKey', 'secretToken', 'accessToken']
        },
        'yaml_config': {
            'filename': 'config.yml',
            'template': '{key}: {value}\n',
            'keys': ['api_key', 'secret_token', 'access_token']
        },
        'readme': {
            'filename': 'README.md',
            'template': '<!-- Example token (DO NOT USE): {value} -->\n',
            'keys': []
        },
        'test_file': {
            'filename': 'test_credentials.py',
            'template': '# Test token: {value}\n',
            'keys': []
        }
    }
    
    def __init__(self, generator=None):
        """Initialize injector with a honeytoken generator."""
        if generator is None:
            from honeytoken_generator import HoneytokenGenerator
            generator = HoneytokenGenerator()
        
        self.generator = generator
        self.injections = []
        self.injection_log_file = 'injection_log.json'
        self._load_injection_log()
    
    def _load_injection_log(self):
        """Load injection history."""
        if os.path.exists(self.injection_log_file):
            try:
                with open(self.injection_log_file, 'r') as f:
                    data = json.load(f)
                    self.injections = data.get('injections', [])
            except json.JSONDecodeError:
                self.injections = []
    
    def _save_injection_log(self):
        """Save injection history."""
        with open(self.injection_log_file, 'w') as f:
            json.dump({'injections': self.injections}, f, indent=2)
    
    def inject_into_file(self, file_path: str, token_value: str, 
                        key_name: str = 'API_KEY',
                        comment: str = None) -> bool:
        """Inject a honeytoken into a file."""
        try:
            # Determine file type and format
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext in ['.env', '.env.example', '.env.sample']:
                line = f"{key_name}={token_value}\n"
            elif file_ext in ['.yml', '.yaml']:
                line = f"{key_name}: {token_value}\n"
            elif file_ext == '.json':
                # For JSON, we need to be more careful
                line = f'  "{key_name}": "{token_value}",\n'
            elif file_ext in ['.py', '.js', '.ts', '.java']:
                comment_char = '#' if file_ext == '.py' else '//'
                line = f"{comment_char} Honeytoken: {token_value}\n"
            elif file_ext == '.md':
                line = f"<!-- Honeytoken (DO NOT USE): {token_value} -->\n"
            else:
                line = f"# {key_name}: {token_value}\n"
            
            # Add custom comment if provided
            if comment:
                comment_char = '#' if file_ext in ['.py', '.yml', '.yaml', '.env'] else '//'
                line = f"{comment_char} {comment}\n{line}"
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path) if os.path.dirname(file_path) else '.', 
                       exist_ok=True)
            
            # Append to file
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write(line)
            
            # Log injection
            injection = {
                'injection_id': datetime.utcnow().strftime('%Y%m%d%H%M%S%f'),
                'timestamp': datetime.utcnow().isoformat(),
                'file_path': file_path,
                'token_value': token_value,
                'key_name': key_name,
                'method': 'file_injection'
            }
            self.injections.append(injection)
            self._save_injection_log()
            
            return True
        
        except Exception as e:
            print(f"Error injecting into file: {e}")
            return False
    
    def create_honeypot_file(self, directory: str, file_type: str = 'env_file',
                            token_count: int = 3) -> Optional[str]:
        """Create a honeypot file with multiple honeytokens."""
        if file_type not in self.INJECTION_TEMPLATES:
            print(f"Unknown file type: {file_type}")
            return None
        
        template_config = self.INJECTION_TEMPLATES[file_type]
        filename = template_config['filename']
        file_path = os.path.join(directory, filename)
        
        try:
            os.makedirs(directory, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                # Add header comment
                f.write("# WARNING: This file contains honeytokens for security monitoring\n")
                f.write("# DO NOT USE these tokens in production\n")
                f.write(f"# Generated: {datetime.utcnow().isoformat()}\n\n")
                
                # Generate and inject tokens
                for i in range(token_count):
                    # Generate a honeytoken
                    token = self.generator.generate_honeytoken(
                        token_type='github_pat',
                        metadata={
                            'injection_method': 'honeypot_file',
                            'file_path': file_path,
                            'purpose': 'detection'
                        }
                    )
                    
                    # Choose a key name
                    if template_config['keys']:
                        key_name = random.choice(template_config['keys'])
                    else:
                        key_name = f"TOKEN_{i+1}"
                    
                    # Write token to file
                    if file_type == 'config_file':
                        # Special handling for JSON
                        if i == 0:
                            f.write("{\n")
                        f.write(f'  "{key_name}": "{token["token_value"]}"')
                        if i < token_count - 1:
                            f.write(",\n")
                        else:
                            f.write("\n}\n")
                    else:
                        line = template_config['template'].format(
                            key=key_name,
                            value=token['token_value']
                        )
                        f.write(line)
                    
                    # Log injection
                    injection = {
                        'injection_id': datetime.utcnow().strftime('%Y%m%d%H%M%S%f'),
                        'timestamp': datetime.utcnow().isoformat(),
                        'file_path': file_path,
                        'token_value': token['token_value'],
                        'token_id': token['token_id'],
                        'key_name': key_name,
                        'method': 'honeypot_file_creation'
                    }
                    self.injections.append(injection)
            
            self._save_injection_log()
            return file_path
        
        except Exception as e:
            print(f"Error creating honeypot file: {e}")
            return None
    
    def inject_into_repository(self, repo_path: str, 
                               file_types: List[str] = None) -> Dict:
        """Inject honeytokens into multiple files in a repository."""
        if file_types is None:
            file_types = ['env_file', 'readme']
        
        created_files = []
        failed_files = []
        
        for file_type in file_types:
            file_path = self.create_honeypot_file(repo_path, file_type)
            if file_path:
                created_files.append(file_path)
            else:
                failed_files.append(file_type)
        
        return {
            'repository': repo_path,
            'injected_at': datetime.utcnow().isoformat(),
            'created_files': created_files,
            'failed_files': failed_files,
            'total_files': len(created_files)
        }
    
    def inject_as_github_secret(self, gh_integration, owner: str, 
                               repo: str, secret_name: str = None) -> bool:
        """Inject honeytoken as a GitHub Actions secret."""
        if secret_name is None:
            secret_name = f"HONEYTOKEN_{datetime.utcnow().strftime('%Y%m%d')}"
        
        # Generate honeytoken
        token = self.generator.generate_honeytoken(
            token_type='github_pat',
            metadata={
                'injection_method': 'github_secret',
                'repository': f"{owner}/{repo}",
                'secret_name': secret_name
            }
        )
        
        # Inject as secret
        success = gh_integration.create_repository_secret(
            owner, repo, secret_name, token['token_value']
        )
        
        if success:
            injection = {
                'injection_id': datetime.utcnow().strftime('%Y%m%d%H%M%S%f'),
                'timestamp': datetime.utcnow().isoformat(),
                'repository': f"{owner}/{repo}",
                'token_value': token['token_value'],
                'token_id': token['token_id'],
                'secret_name': secret_name,
                'method': 'github_secret'
            }
            self.injections.append(injection)
            self._save_injection_log()
        
        return success
    
    def inject_into_ci_config(self, ci_type: str, file_path: str) -> bool:
        """Inject honeytoken into CI configuration file."""
        token = self.generator.generate_honeytoken(
            token_type='github_pat',
            metadata={
                'injection_method': 'ci_config',
                'ci_type': ci_type,
                'file_path': file_path
            }
        )
        
        if ci_type == 'github_actions':
            # Add to GitHub Actions workflow
            comment = "# WARNING: Honeytoken for detection purposes"
            return self.inject_into_file(
                file_path, 
                token['token_value'],
                key_name='HONEYTOKEN',
                comment=comment
            )
        
        elif ci_type == 'gitlab_ci':
            # Add to .gitlab-ci.yml
            line = f"  HONEYTOKEN: {token['token_value']}  # Detection token\n"
            try:
                with open(file_path, 'a', encoding='utf-8') as f:
                    f.write(line)
                return True
            except Exception as e:
                print(f"Error: {e}")
                return False
        
        return False
    
    def get_injection_history(self, limit: int = 50) -> List[Dict]:
        """Get recent injection history."""
        return self.injections[-limit:]
    
    def get_injection_statistics(self) -> Dict:
        """Get injection statistics."""
        return {
            'total_injections': len(self.injections),
            'file_injections': sum(1 for i in self.injections 
                                  if i['method'] == 'file_injection'),
            'honeypot_files': sum(1 for i in self.injections 
                                 if i['method'] == 'honeypot_file_creation'),
            'github_secrets': sum(1 for i in self.injections 
                                 if i['method'] == 'github_secret'),
        }
    
    def cleanup_injections(self, repo_path: str) -> Dict:
        """Remove injected honeypot files from a repository."""
        removed = []
        failed = []
        
        # Get list of files created by this injector
        injected_files = set()
        for injection in self.injections:
            if 'file_path' in injection and injection['file_path'].startswith(repo_path):
                injected_files.add(injection['file_path'])
        
        for file_path in injected_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    removed.append(file_path)
            except Exception as e:
                failed.append({'file': file_path, 'error': str(e)})
        
        return {
            'removed_files': removed,
            'failed_files': failed,
            'total_removed': len(removed)
        }


def main():
    """CLI interface for honeytoken injector."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Honeytoken Injector')
    parser.add_argument('--create-file', nargs=2, metavar=('DIR', 'TYPE'),
                       help='Create honeypot file')
    parser.add_argument('--inject-file', nargs=2, metavar=('FILE', 'TOKEN'),
                       help='Inject token into file')
    parser.add_argument('--inject-repo', metavar='REPO_PATH',
                       help='Inject honeytokens into repository')
    parser.add_argument('--history', action='store_true', help='Show injection history')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    parser.add_argument('--cleanup', metavar='REPO_PATH', help='Remove injected files')
    
    args = parser.parse_args()
    
    injector = HoneytokenInjector()
    
    if args.create_file:
        directory, file_type = args.create_file
        file_path = injector.create_honeypot_file(directory, file_type)
        if file_path:
            print(f"\n✓ Created honeypot file: {file_path}")
        else:
            print("\n✗ Failed to create honeypot file")
    
    elif args.inject_file:
        file_path, token_value = args.inject_file
        success = injector.inject_into_file(file_path, token_value)
        print(f"\n{'✓' if success else '✗'} Token injection: {file_path}")
    
    elif args.inject_repo:
        result = injector.inject_into_repository(args.inject_repo)
        print(f"\n=== Repository Injection ===")
        print(f"Repository: {result['repository']}")
        print(f"Files created: {result['total_files']}")
        for file in result['created_files']:
            print(f"  - {file}")
    
    elif args.history:
        history = injector.get_injection_history(limit=10)
        print(f"\n=== Injection History ({len(history)}) ===")
        for injection in history:
            print(f"\nTime: {injection['timestamp']}")
            print(f"Method: {injection['method']}")
            if 'file_path' in injection:
                print(f"File: {injection['file_path']}")
            print(f"Token ID: {injection.get('token_id', 'N/A')}")
    
    elif args.stats:
        stats = injector.get_injection_statistics()
        print("\n=== Injection Statistics ===")
        for key, value in stats.items():
            print(f"{key}: {value}")
    
    elif args.cleanup:
        result = injector.cleanup_injections(args.cleanup)
        print(f"\n=== Cleanup Results ===")
        print(f"Removed: {result['total_removed']} files")
        for file in result['removed_files']:
            print(f"  ✓ {file}")
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
