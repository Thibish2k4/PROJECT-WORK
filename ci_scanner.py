"""
CI Scanner Module
Integrates with CI/CD pipelines for automated token scanning.
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Optional


class CIScanner:
    """Scanner designed for CI/CD pipeline integration."""
    
    def __init__(self):
        """Initialize CI scanner."""
        from token_scanner import TokenScanner
        from honeytoken_generator import HoneytokenGenerator
        
        self.scanner = TokenScanner()
        self.generator = HoneytokenGenerator()
        self.ci_environment = self._detect_ci_environment()
    
    def _detect_ci_environment(self) -> Dict:
        """Detect which CI/CD environment we're running in."""
        env_info = {
            'platform': 'unknown',
            'is_ci': False,
            'details': {}
        }
        
        # GitHub Actions
        if os.getenv('GITHUB_ACTIONS') == 'true':
            env_info.update({
                'platform': 'github_actions',
                'is_ci': True,
                'details': {
                    'repository': os.getenv('GITHUB_REPOSITORY'),
                    'workflow': os.getenv('GITHUB_WORKFLOW'),
                    'run_id': os.getenv('GITHUB_RUN_ID'),
                    'run_number': os.getenv('GITHUB_RUN_NUMBER'),
                    'actor': os.getenv('GITHUB_ACTOR'),
                    'ref': os.getenv('GITHUB_REF'),
                    'sha': os.getenv('GITHUB_SHA'),
                    'event_name': os.getenv('GITHUB_EVENT_NAME')
                }
            })
        
        # GitLab CI
        elif os.getenv('GITLAB_CI'):
            env_info.update({
                'platform': 'gitlab_ci',
                'is_ci': True,
                'details': {
                    'repository': os.getenv('CI_PROJECT_PATH'),
                    'pipeline_id': os.getenv('CI_PIPELINE_ID'),
                    'job_id': os.getenv('CI_JOB_ID'),
                    'commit_sha': os.getenv('CI_COMMIT_SHA'),
                    'ref': os.getenv('CI_COMMIT_REF_NAME')
                }
            })
        
        # Jenkins
        elif os.getenv('JENKINS_HOME'):
            env_info.update({
                'platform': 'jenkins',
                'is_ci': True,
                'details': {
                    'job_name': os.getenv('JOB_NAME'),
                    'build_number': os.getenv('BUILD_NUMBER'),
                    'build_id': os.getenv('BUILD_ID'),
                    'workspace': os.getenv('WORKSPACE')
                }
            })
        
        # CircleCI
        elif os.getenv('CIRCLECI'):
            env_info.update({
                'platform': 'circleci',
                'is_ci': True,
                'details': {
                    'repository': os.getenv('CIRCLE_PROJECT_REPONAME'),
                    'branch': os.getenv('CIRCLE_BRANCH'),
                    'build_num': os.getenv('CIRCLE_BUILD_NUM'),
                    'sha': os.getenv('CIRCLE_SHA1')
                }
            })
        
        # Travis CI
        elif os.getenv('TRAVIS'):
            env_info.update({
                'platform': 'travis_ci',
                'is_ci': True,
                'details': {
                    'repository': os.getenv('TRAVIS_REPO_SLUG'),
                    'build_number': os.getenv('TRAVIS_BUILD_NUMBER'),
                    'commit': os.getenv('TRAVIS_COMMIT'),
                    'branch': os.getenv('TRAVIS_BRANCH')
                }
            })
        
        return env_info
    
    def scan_workspace(self, workspace_path: str = None) -> Dict:
        """Scan the CI workspace for tokens."""
        if workspace_path is None:
            # Try to detect workspace path
            if self.ci_environment['platform'] == 'github_actions':
                workspace_path = os.getenv('GITHUB_WORKSPACE', '.')
            elif self.ci_environment['platform'] == 'gitlab_ci':
                workspace_path = os.getenv('CI_PROJECT_DIR', '.')
            elif self.ci_environment['platform'] == 'jenkins':
                workspace_path = os.getenv('WORKSPACE', '.')
            else:
                workspace_path = '.'
        
        print(f"\n🔍 Scanning workspace: {workspace_path}")
        print(f"   CI Platform: {self.ci_environment['platform']}")
        
        scan_result = self.scanner.scan_directory(workspace_path, recursive=True)
        
        # Add CI context
        scan_result['ci_environment'] = self.ci_environment
        
        return scan_result
    
    def scan_diff(self, base_ref: str = None, head_ref: str = None) -> Dict:
        """Scan only changed files in a pull request or commit."""
        import subprocess
        
        # Determine refs to compare
        if self.ci_environment['platform'] == 'github_actions':
            if base_ref is None:
                base_ref = os.getenv('GITHUB_BASE_REF') or 'HEAD^'
            if head_ref is None:
                head_ref = os.getenv('GITHUB_SHA') or 'HEAD'
        
        try:
            # Get list of changed files
            result = subprocess.run(
                ['git', 'diff', '--name-only', base_ref, head_ref],
                capture_output=True,
                text=True,
                check=True
            )
            
            changed_files = [f.strip() for f in result.stdout.split('\n') if f.strip()]
            
            print(f"\n🔍 Scanning {len(changed_files)} changed file(s)")
            
            all_findings = []
            scanned_files = []
            errors = []
            
            for file_path in changed_files:
                if not os.path.exists(file_path):
                    continue
                
                if self.scanner.should_scan_file(file_path):
                    findings, metadata = self.scanner.scan_file(file_path)
                    
                    if 'error' in metadata:
                        errors.append({'file': file_path, 'error': metadata['error']})
                    else:
                        scanned_files.append(file_path)
                        if findings:
                            all_findings.extend(findings)
            
            return {
                'scan_type': 'diff',
                'base_ref': base_ref,
                'head_ref': head_ref,
                'changed_files': len(changed_files),
                'scanned_files': len(scanned_files),
                'total_findings': len(all_findings),
                'honeytokens_found': sum(1 for f in all_findings if f['is_honeytoken']),
                'findings': all_findings,
                'errors': errors,
                'ci_environment': self.ci_environment
            }
        
        except subprocess.CalledProcessError as e:
            print(f"Error running git diff: {e}")
            return {
                'scan_type': 'diff',
                'error': str(e),
                'ci_environment': self.ci_environment
            }
    
    def generate_report(self, scan_result: Dict, format: str = 'text') -> str:
        """Generate a scan report in various formats."""
        if format == 'text':
            return self._generate_text_report(scan_result)
        elif format == 'json':
            return json.dumps(scan_result, indent=2)
        elif format == 'markdown':
            return self._generate_markdown_report(scan_result)
        elif format == 'github':
            return self._generate_github_annotations(scan_result)
        else:
            return self._generate_text_report(scan_result)
    
    def _generate_text_report(self, scan_result: Dict) -> str:
        """Generate a text report."""
        lines = [
            "\n" + "="*60,
            "HONEYTOKEN SCAN REPORT",
            "="*60,
            f"Platform: {scan_result.get('ci_environment', {}).get('platform', 'unknown')}",
            f"Scan Type: {scan_result.get('scan_type', 'directory')}",
            f"Timestamp: {datetime.utcnow().isoformat()}",
            "",
            f"Files Scanned: {scan_result.get('total_files_scanned', scan_result.get('scanned_files', 0))}",
            f"Total Findings: {scan_result.get('total_findings', 0)}",
            f"Honeytokens Found: {scan_result.get('honeytokens_found', 0)}",
            ""
        ]
        
        findings = scan_result.get('findings', [])
        if findings:
            lines.append("FINDINGS:")
            lines.append("-" * 60)
            
            for i, finding in enumerate(findings, 1):
                lines.extend([
                    f"\n{i}. {finding['token_type']}",
                    f"   Source: {finding['source']}",
                    f"   Line: {finding.get('line_number', 'N/A')}",
                    f"   Honeytoken: {'YES ⚠️' if finding['is_honeytoken'] else 'No'}",
                    f"   Preview: {finding['token_preview']}"
                ])
        else:
            lines.append("✓ No tokens found")
        
        lines.append("\n" + "="*60)
        
        return "\n".join(lines)
    
    def _generate_markdown_report(self, scan_result: Dict) -> str:
        """Generate a markdown report."""
        lines = [
            "# 🔍 Honeytoken Scan Report",
            "",
            f"**Platform:** {scan_result.get('ci_environment', {}).get('platform', 'unknown')}  ",
            f"**Scan Type:** {scan_result.get('scan_type', 'directory')}  ",
            f"**Timestamp:** {datetime.utcnow().isoformat()}  ",
            "",
            "## Summary",
            "",
            f"- **Files Scanned:** {scan_result.get('total_files_scanned', scan_result.get('scanned_files', 0))}",
            f"- **Total Findings:** {scan_result.get('total_findings', 0)}",
            f"- **Honeytokens Found:** {scan_result.get('honeytokens_found', 0)}",
            ""
        ]
        
        findings = scan_result.get('findings', [])
        if findings:
            lines.extend([
                "## 🚨 Findings",
                "",
                "| # | Type | Source | Line | Honeytoken | Preview |",
                "|---|------|--------|------|------------|---------|"
            ])
            
            for i, finding in enumerate(findings, 1):
                honeytoken_marker = "⚠️ YES" if finding['is_honeytoken'] else "No"
                lines.append(
                    f"| {i} | {finding['token_type']} | `{finding['source']}` | "
                    f"{finding.get('line_number', 'N/A')} | {honeytoken_marker} | "
                    f"`{finding['token_preview']}` |"
                )
        else:
            lines.extend([
                "## ✅ Results",
                "",
                "No tokens found in the scan."
            ])
        
        return "\n".join(lines)
    
    def _generate_github_annotations(self, scan_result: Dict) -> str:
        """Generate GitHub Actions annotations."""
        annotations = []
        
        for finding in scan_result.get('findings', []):
            level = 'error' if finding['is_honeytoken'] else 'warning'
            file_path = finding['source']
            line = finding.get('line_number', 1)
            
            message = f"{finding['token_type']} detected"
            if finding['is_honeytoken']:
                message += " (HONEYTOKEN)"
            
            annotations.append(
                f"::{level} file={file_path},line={line}::{message}"
            )
        
        return "\n".join(annotations)
    
    def set_ci_output(self, scan_result: Dict):
        """Set CI outputs for use in subsequent steps."""
        findings_count = scan_result.get('total_findings', 0)
        honeytokens_count = scan_result.get('honeytokens_found', 0)
        
        if self.ci_environment['platform'] == 'github_actions':
            # Set GitHub Actions outputs
            github_output = os.getenv('GITHUB_OUTPUT')
            if github_output:
                with open(github_output, 'a') as f:
                    f.write(f"findings_count={findings_count}\n")
                    f.write(f"honeytokens_found={honeytokens_count}\n")
                    f.write(f"has_findings={'true' if findings_count > 0 else 'false'}\n")
        
        # Also set as environment variables
        os.environ['SCAN_FINDINGS_COUNT'] = str(findings_count)
        os.environ['SCAN_HONEYTOKENS_FOUND'] = str(honeytokens_count)
    
    def should_fail_build(self, scan_result: Dict, 
                         fail_on_findings: bool = True,
                         fail_on_honeytokens: bool = True) -> bool:
        """Determine if the CI build should fail based on scan results."""
        findings_count = scan_result.get('total_findings', 0)
        honeytokens_count = scan_result.get('honeytokens_found', 0)
        
        if fail_on_honeytokens and honeytokens_count > 0:
            return True
        
        if fail_on_findings and findings_count > 0:
            # Only fail on non-honeytoken findings (real leaks)
            real_leaks = findings_count - honeytokens_count
            return real_leaks > 0
        
        return False


def main():
    """CLI interface for CI scanner."""
    import argparse
    
    parser = argparse.ArgumentParser(description='CI/CD Token Scanner')
    parser.add_argument('--scan-workspace', action='store_true',
                       help='Scan entire workspace')
    parser.add_argument('--scan-diff', action='store_true',
                       help='Scan only changed files')
    parser.add_argument('--base-ref', help='Base reference for diff')
    parser.add_argument('--head-ref', help='Head reference for diff')
    parser.add_argument('--format', choices=['text', 'json', 'markdown', 'github'],
                       default='text', help='Report format')
    parser.add_argument('--fail-on-findings', action='store_true',
                       help='Exit with error if findings detected')
    parser.add_argument('--fail-on-honeytokens', action='store_true',
                       help='Exit with error if honeytokens detected')
    parser.add_argument('--output-file', help='Write report to file')
    
    args = parser.parse_args()
    
    ci_scanner = CIScanner()
    
    print(f"\n🔍 CI Scanner")
    print(f"   Platform: {ci_scanner.ci_environment['platform']}")
    print(f"   Is CI: {ci_scanner.ci_environment['is_ci']}")
    
    # Perform scan
    if args.scan_diff:
        scan_result = ci_scanner.scan_diff(args.base_ref, args.head_ref)
    else:
        scan_result = ci_scanner.scan_workspace()
    
    # Generate report
    report = ci_scanner.generate_report(scan_result, format=args.format)
    
    # Output report
    if args.output_file:
        with open(args.output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n✓ Report saved to: {args.output_file}")
    else:
        print(report)
    
    # Set CI outputs
    ci_scanner.set_ci_output(scan_result)
    
    # GitHub annotations
    if args.format == 'github':
        print(report)
    
    # Determine if build should fail
    should_fail = ci_scanner.should_fail_build(
        scan_result,
        fail_on_findings=args.fail_on_findings,
        fail_on_honeytokens=args.fail_on_honeytokens
    )
    
    if should_fail:
        print("\n❌ Build failed: Tokens detected")
        sys.exit(1)
    else:
        print("\n✅ Build passed: No issues detected")
        sys.exit(0)


if __name__ == '__main__':
    main()
