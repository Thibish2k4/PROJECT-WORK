"""
Test Suite for Honeytoken System
Unit tests for core functionality.
"""

import unittest
import os
import json
import tempfile
import shutil
from datetime import datetime


class TestHoneytokenGenerator(unittest.TestCase):
    """Test honeytoken generator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.storage_file = os.path.join(self.temp_dir, 'test_honeytokens.json')
        
        from honeytoken_generator import HoneytokenGenerator
        self.generator = HoneytokenGenerator(storage_file=self.storage_file)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_generate_github_pat(self):
        """Test GitHub PAT generation."""
        token = self.generator.generate_github_pat()
        self.assertTrue(token.startswith('ghp_'))
        self.assertEqual(len(token), 40)  # ghp_ + 36 chars
    
    def test_generate_github_oauth(self):
        """Test GitHub OAuth token generation."""
        token = self.generator.generate_github_oauth()
        self.assertTrue(token.startswith('gho_'))
        self.assertEqual(len(token), 40)
    
    def test_generate_aws_access_key(self):
        """Test AWS access key generation."""
        key = self.generator.generate_aws_access_key()
        self.assertTrue(key.startswith('AKIA'))
        self.assertEqual(len(key), 20)
    
    def test_generate_honeytoken_with_metadata(self):
        """Test honeytoken generation with metadata."""
        metadata = {'purpose': 'test', 'environment': 'dev'}
        token = self.generator.generate_honeytoken('github_pat', metadata)
        
        self.assertIn('token_id', token)
        self.assertIn('token_value', token)
        self.assertIn('token_hash', token)
        self.assertEqual(token['metadata'], metadata)
        self.assertFalse(token['detected'])
    
    def test_mark_as_detected(self):
        """Test marking token as detected."""
        token = self.generator.generate_honeytoken('github_pat')
        token_value = token['token_value']
        
        success = self.generator.mark_as_detected(token_value)
        self.assertTrue(success)
        
        retrieved = self.generator.get_token_by_value(token_value)
        self.assertTrue(retrieved['detected'])
        self.assertEqual(retrieved['detection_count'], 1)
    
    def test_token_persistence(self):
        """Test token storage and retrieval."""
        token = self.generator.generate_honeytoken('github_pat')
        token_value = token['token_value']
        
        # Create new generator instance
        from honeytoken_generator import HoneytokenGenerator
        new_generator = HoneytokenGenerator(storage_file=self.storage_file)
        
        retrieved = new_generator.get_token_by_value(token_value)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved['token_value'], token_value)
    
    def test_batch_generation(self):
        """Test batch generation."""
        tokens = self.generator.generate_batch(['github_pat', 'aws_access'], count=3)
        self.assertEqual(len(tokens), 6)  # 3 of each type


class TestTokenScanner(unittest.TestCase):
    """Test token scanner."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
        from token_scanner import TokenScanner
        self.scanner = TokenScanner()
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_scan_text_github_pat(self):
        """Test scanning text for GitHub PAT."""
        text = "Here is a token: ghp_1234567890abcdefghijklmnopqrstuvwxyz"
        findings = self.scanner.scan_text(text, 'test')
        
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]['token_type'], 'github_pat')
    
    def test_scan_text_aws_key(self):
        """Test scanning text for AWS key."""
        text = "AWS_ACCESS_KEY=AKIAIOSFODNN7EXAMPLE"
        findings = self.scanner.scan_text(text, 'test')
        
        self.assertGreater(len(findings), 0)
        found_aws = any(f['token_type'] == 'aws_access_key' for f in findings)
        self.assertTrue(found_aws)
    
    def test_scan_file(self):
        """Test scanning a file."""
        test_file = os.path.join(self.temp_dir, 'test.py')
        # Use a properly formatted GitHub PAT (ghp_ + exactly 36 alphanumeric chars)
        with open(test_file, 'w') as f:
            f.write('# GitHub token\n')
            f.write('TOKEN = "ghp_1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZabcd"\n')
        
        findings, metadata = self.scanner.scan_file(test_file)
        
        # Should find at least one token
        self.assertGreaterEqual(len(findings), 1)
        # Check that a github_pat token was found
        if findings:
            github_pat_found = any(f['token_type'] == 'github_pat' for f in findings)
            self.assertTrue(github_pat_found)
    
    def test_should_scan_file(self):
        """Test file scanning filter."""
        # Use full paths for testing
        test_py = os.path.join(self.temp_dir, 'test.py')
        config_yml = os.path.join(self.temp_dir, 'config.yml')
        node_test = os.path.join(self.temp_dir, 'node_modules', 'test.js')
        test_exe = os.path.join(self.temp_dir, 'test.exe')
        
        # Create the files so they exist
        open(test_py, 'w').close()
        open(config_yml, 'w').close()
        os.makedirs(os.path.dirname(node_test), exist_ok=True)
        open(node_test, 'w').close()
        open(test_exe, 'w').close()
        
        self.assertTrue(self.scanner.should_scan_file(test_py))
        self.assertTrue(self.scanner.should_scan_file(config_yml))
        self.assertFalse(self.scanner.should_scan_file(node_test))
        self.assertFalse(self.scanner.should_scan_file(test_exe))
    
    def test_scan_directory(self):
        """Test scanning a directory."""
        # Create test files
        test_file1 = os.path.join(self.temp_dir, 'file1.py')
        test_file2 = os.path.join(self.temp_dir, 'file2.js')
        
        with open(test_file1, 'w') as f:
            f.write('token = "ghp_1234567890abcdefghijklmnopqrstuvwxyz"\n')
        
        with open(test_file2, 'w') as f:
            f.write('const token = "gho_1234567890abcdefghijklmnopqrstuvwxyz";\n')
        
        result = self.scanner.scan_directory(self.temp_dir, recursive=False)
        
        self.assertGreaterEqual(result['total_files_scanned'], 2)
        self.assertEqual(result['total_findings'], 2)


class TestHoneytokenInjector(unittest.TestCase):
    """Test honeytoken injector."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
        from honeytoken_injector import HoneytokenInjector
        self.injector = HoneytokenInjector()
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_inject_into_file(self):
        """Test injecting token into a file."""
        test_file = os.path.join(self.temp_dir, 'test.env')
        token_value = 'ghp_test1234567890abcdefghijklmnopqrstuvwxyz'
        
        success = self.injector.inject_into_file(test_file, token_value, 'TEST_TOKEN')
        self.assertTrue(success)
        self.assertTrue(os.path.exists(test_file))
        
        with open(test_file, 'r') as f:
            content = f.read()
            self.assertIn(token_value, content)
    
    def test_create_honeypot_file(self):
        """Test creating a honeypot file."""
        file_path = self.injector.create_honeypot_file(
            self.temp_dir, 
            'env_file', 
            token_count=2
        )
        
        self.assertIsNotNone(file_path)
        self.assertTrue(os.path.exists(file_path))
        
        with open(file_path, 'r') as f:
            content = f.read()
            self.assertIn('WARNING', content)
    
    def test_cleanup_injections(self):
        """Test cleaning up injected files."""
        # Create a honeypot file
        file_path = self.injector.create_honeypot_file(
            self.temp_dir, 
            'env_file'
        )
        
        self.assertTrue(os.path.exists(file_path))
        
        # Clean up
        result = self.injector.cleanup_injections(self.temp_dir)
        
        self.assertGreater(result['total_removed'], 0)


class TestAlertSystem(unittest.TestCase):
    """Test alert system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        config_file = os.path.join(self.temp_dir, 'alert_config.json')
        history_file = os.path.join(self.temp_dir, 'alert_history.json')
        
        from alert_system import AlertSystem
        self.alert_system = AlertSystem(config_file=config_file)
        # Override history file path
        self.alert_system.alert_history_file = history_file
        self.alert_system.alert_history = []  # Start with empty history
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_alert_configuration(self):
        """Test alert configuration loading."""
        self.assertIn('email', self.alert_system.config)
        self.assertIn('webhook', self.alert_system.config)
        self.assertIn('slack', self.alert_system.config)
    
    def test_record_alert(self):
        """Test recording an alert."""
        detection = {
            'honeytoken_id': 'test123',
            'token_type': 'github_pat'
        }
        
        # Start with empty history
        initial_count = len(self.alert_system.alert_history)
        
        self.alert_system._record_alert(
            'test', 
            'test@example.com', 
            detection, 
            True
        )
        
        # Should have exactly one more alert
        self.assertEqual(len(self.alert_system.alert_history), initial_count + 1)
        self.assertTrue(self.alert_system.alert_history[-1]['success'])
    
    def test_get_statistics(self):
        """Test getting alert statistics."""
        detection = {'honeytoken_id': 'test123'}
        
        self.alert_system._record_alert('test', 'recipient', detection, True)
        self.alert_system._record_alert('test', 'recipient', detection, False)
        
        stats = self.alert_system.get_alert_statistics()
        
        self.assertEqual(stats['total_alerts'], 2)
        self.assertEqual(stats['successful_alerts'], 1)
        self.assertEqual(stats['failed_alerts'], 1)


class TestCIScanner(unittest.TestCase):
    """Test CI scanner."""
    
    def setUp(self):
        """Set up test fixtures."""
        from ci_scanner import CIScanner
        self.ci_scanner = CIScanner()
    
    def test_detect_ci_environment(self):
        """Test CI environment detection."""
        env_info = self.ci_scanner.ci_environment
        
        self.assertIn('platform', env_info)
        self.assertIn('is_ci', env_info)
        self.assertIn('details', env_info)
    
    def test_generate_text_report(self):
        """Test text report generation."""
        scan_result = {
            'scan_type': 'test',
            'total_findings': 2,
            'honeytokens_found': 1,
            'findings': [
                {
                    'token_type': 'github_pat',
                    'source': 'test.py',
                    'line_number': 10,
                    'is_honeytoken': True,
                    'token_preview': 'ghp_test...'
                }
            ],
            'ci_environment': {'platform': 'test'}
        }
        
        report = self.ci_scanner.generate_report(scan_result, format='text')
        
        self.assertIn('HONEYTOKEN SCAN REPORT', report)
        self.assertIn('github_pat', report)
    
    def test_generate_markdown_report(self):
        """Test markdown report generation."""
        scan_result = {
            'scan_type': 'test',
            'total_findings': 1,
            'honeytokens_found': 0,
            'findings': [],
            'ci_environment': {'platform': 'test'}
        }
        
        report = self.ci_scanner.generate_report(scan_result, format='markdown')
        
        self.assertIn('# 🔍 Honeytoken Scan Report', report)
        self.assertIn('## Summary', report)
    
    def test_should_fail_build(self):
        """Test build failure logic."""
        scan_result_clean = {
            'total_findings': 0,
            'honeytokens_found': 0
        }
        
        scan_result_honeytoken = {
            'total_findings': 1,
            'honeytokens_found': 1
        }
        
        scan_result_real_leak = {
            'total_findings': 2,
            'honeytokens_found': 1
        }
        
        # Clean scan should not fail
        self.assertFalse(
            self.ci_scanner.should_fail_build(scan_result_clean, True, True)
        )
        
        # Honeytoken should fail if configured
        self.assertTrue(
            self.ci_scanner.should_fail_build(scan_result_honeytoken, True, True)
        )
        
        # Real leak should fail
        self.assertTrue(
            self.ci_scanner.should_fail_build(scan_result_real_leak, True, False)
        )


def run_tests():
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestHoneytokenGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestTokenScanner))
    suite.addTests(loader.loadTestsFromTestCase(TestHoneytokenInjector))
    suite.addTests(loader.loadTestsFromTestCase(TestAlertSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestCIScanner))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    print("\n" + "="*60)
    print("  Honeytoken System Test Suite")
    print("="*60 + "\n")
    
    success = run_tests()
    
    if success:
        print("\n✅ All tests passed!")
        exit(0)
    else:
        print("\n❌ Some tests failed")
        exit(1)
