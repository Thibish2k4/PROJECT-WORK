"""
Honeytoken Generator Module
Generates realistic GitHub-style tokens and honeytokens for detection purposes.
"""

import secrets
import string
import hashlib
import json
import os
from datetime import datetime
from typing import Dict, List


class HoneytokenGenerator:
    """Generate various types of honeytokens that mimic real tokens."""
    
    # Token prefixes used by GitHub and other services
    TOKEN_PREFIXES = {
        'github_pat': 'ghp_',
        'github_oauth': 'gho_',
        'github_app': 'ghs_',
        'github_refresh': 'ghr_',
        'github_fine_grained': 'github_pat_',
        'aws_access': 'AKIA',
        'slack': 'xoxb-',
        'stripe': 'sk_live_',
    }
    
    def __init__(self, storage_file: str = 'honeytokens.json'):
        """Initialize the generator with a storage file."""
        self.storage_file = storage_file
        self.honeytokens = self._load_tokens()
    
    def _load_tokens(self) -> Dict:
        """Load existing honeytokens from storage."""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {'tokens': []}
        return {'tokens': []}
    
    def _save_tokens(self):
        """Save honeytokens to storage."""
        with open(self.storage_file, 'w') as f:
            json.dump(self.honeytokens, f, indent=2)
    
    def generate_random_string(self, length: int, charset: str = None) -> str:
        """Generate a cryptographically secure random string."""
        if charset is None:
            charset = string.ascii_letters + string.digits
        return ''.join(secrets.choice(charset) for _ in range(length))
    
    def generate_github_pat(self) -> str:
        """Generate a realistic GitHub Personal Access Token."""
        # GitHub PAT format: ghp_<36 alphanumeric characters>
        token_body = self.generate_random_string(36)
        return f"{self.TOKEN_PREFIXES['github_pat']}{token_body}"
    
    def generate_github_oauth(self) -> str:
        """Generate a realistic GitHub OAuth token."""
        # GitHub OAuth format: gho_<36 alphanumeric characters>
        token_body = self.generate_random_string(36)
        return f"{self.TOKEN_PREFIXES['github_oauth']}{token_body}"
    
    def generate_github_fine_grained(self) -> str:
        """Generate a realistic GitHub Fine-Grained PAT."""
        # Format: github_pat_<22 chars>_<59 chars>
        part1 = self.generate_random_string(22)
        part2 = self.generate_random_string(59)
        return f"{self.TOKEN_PREFIXES['github_fine_grained']}{part1}_{part2}"
    
    def generate_aws_access_key(self) -> str:
        """Generate a realistic AWS Access Key."""
        # AWS format: AKIA + 16 uppercase alphanumeric
        key_body = self.generate_random_string(16, string.ascii_uppercase + string.digits)
        return f"{self.TOKEN_PREFIXES['aws_access']}{key_body}"
    
    def generate_slack_token(self) -> str:
        """Generate a realistic Slack bot token."""
        # Slack format: xoxb-<numbers>-<numbers>-<alphanumeric>
        part1 = self.generate_random_string(11, string.digits)
        part2 = self.generate_random_string(11, string.digits)
        part3 = self.generate_random_string(24)
        return f"{self.TOKEN_PREFIXES['slack']}{part1}-{part2}-{part3}"
    
    def generate_stripe_key(self) -> str:
        """Generate a realistic Stripe secret key."""
        # Stripe format: sk_live_<24 alphanumeric>
        key_body = self.generate_random_string(24)
        return f"{self.TOKEN_PREFIXES['stripe']}{key_body}"
    
    def generate_honeytoken(self, token_type: str = 'github_pat', 
                           metadata: Dict = None) -> Dict:
        """Generate a complete honeytoken with metadata."""
        token_generators = {
            'github_pat': self.generate_github_pat,
            'github_oauth': self.generate_github_oauth,
            'github_fine_grained': self.generate_github_fine_grained,
            'aws_access': self.generate_aws_access_key,
            'slack': self.generate_slack_token,
            'stripe': self.generate_stripe_key,
        }
        
        if token_type not in token_generators:
            raise ValueError(f"Unknown token type: {token_type}")
        
        token_value = token_generators[token_type]()
        token_hash = hashlib.sha256(token_value.encode()).hexdigest()
        
        honeytoken = {
            'token_id': token_hash[:16],
            'token_type': token_type,
            'token_value': token_value,
            'token_hash': token_hash,
            'created_at': datetime.utcnow().isoformat(),
            'metadata': metadata or {},
            'detected': False,
            'detection_count': 0,
            'last_detected': None
        }
        
        self.honeytokens['tokens'].append(honeytoken)
        self._save_tokens()
        
        return honeytoken
    
    def generate_batch(self, token_types: List[str] = None, 
                       count: int = 5) -> List[Dict]:
        """Generate multiple honeytokens."""
        if token_types is None:
            token_types = ['github_pat', 'github_oauth', 'aws_access']
        
        generated = []
        for token_type in token_types:
            for i in range(count):
                metadata = {
                    'purpose': 'detection',
                    'environment': 'test',
                    'batch_id': datetime.utcnow().strftime('%Y%m%d%H%M%S'),
                    'index': i
                }
                token = self.generate_honeytoken(token_type, metadata)
                generated.append(token)
        
        return generated
    
    def get_token_by_value(self, token_value: str) -> Dict:
        """Retrieve a honeytoken by its value."""
        for token in self.honeytokens['tokens']:
            if token['token_value'] == token_value:
                return token
        return None
    
    def get_token_by_hash(self, token_hash: str) -> Dict:
        """Retrieve a honeytoken by its hash."""
        for token in self.honeytokens['tokens']:
            if token['token_hash'] == token_hash:
                return token
        return None
    
    def mark_as_detected(self, token_value: str, detection_info: Dict = None):
        """Mark a honeytoken as detected."""
        for token in self.honeytokens['tokens']:
            if token['token_value'] == token_value:
                token['detected'] = True
                token['detection_count'] += 1
                token['last_detected'] = datetime.utcnow().isoformat()
                if detection_info:
                    if 'detections' not in token:
                        token['detections'] = []
                    token['detections'].append({
                        'timestamp': datetime.utcnow().isoformat(),
                        'info': detection_info
                    })
                self._save_tokens()
                return True
        return False
    
    def list_all_tokens(self, detected_only: bool = False) -> List[Dict]:
        """List all honeytokens."""
        tokens = self.honeytokens['tokens']
        if detected_only:
            return [t for t in tokens if t['detected']]
        return tokens
    
    def get_statistics(self) -> Dict:
        """Get statistics about honeytokens."""
        tokens = self.honeytokens['tokens']
        detected = [t for t in tokens if t['detected']]
        
        return {
            'total_tokens': len(tokens),
            'detected_tokens': len(detected),
            'undetected_tokens': len(tokens) - len(detected),
            'detection_rate': len(detected) / len(tokens) if tokens else 0,
            'total_detections': sum(t['detection_count'] for t in tokens)
        }


def main():
    """CLI interface for the honeytoken generator."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate honeytokens')
    parser.add_argument('--type', choices=['github_pat', 'github_oauth', 
                                           'github_fine_grained', 'aws_access', 
                                           'slack', 'stripe'],
                       default='github_pat', help='Token type to generate')
    parser.add_argument('--count', type=int, default=1, help='Number of tokens')
    parser.add_argument('--batch', action='store_true', 
                       help='Generate batch of multiple types')
    parser.add_argument('--list', action='store_true', help='List all tokens')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    
    args = parser.parse_args()
    
    generator = HoneytokenGenerator()
    
    if args.stats:
        stats = generator.get_statistics()
        print("\n=== Honeytoken Statistics ===")
        for key, value in stats.items():
            print(f"{key}: {value}")
    elif args.list:
        tokens = generator.list_all_tokens()
        print(f"\n=== All Honeytokens ({len(tokens)}) ===")
        for token in tokens:
            print(f"\nID: {token['token_id']}")
            print(f"Type: {token['token_type']}")
            print(f"Value: {token['token_value'][:20]}...")
            print(f"Detected: {token['detected']} ({token['detection_count']} times)")
    elif args.batch:
        tokens = generator.generate_batch(count=args.count)
        print(f"\n=== Generated {len(tokens)} Honeytokens ===")
        for token in tokens:
            print(f"\n{token['token_type']}: {token['token_value']}")
    else:
        tokens = [generator.generate_honeytoken(args.type) for _ in range(args.count)]
        print(f"\n=== Generated {len(tokens)} {args.type} Token(s) ===")
        for token in tokens:
            print(f"\nToken: {token['token_value']}")
            print(f"ID: {token['token_id']}")
            print(f"Hash: {token['token_hash']}")


if __name__ == '__main__':
    main()
