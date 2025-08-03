#!/usr/bin/env python3
"""Run all tests to verify functionality and security."""

import sys
import os
import unittest

# Add the workspace to the Python path
sys.path.insert(0, '/workspace')

# Import and run the test module
if __name__ == '__main__':
    # Change to the workspace directory
    os.chdir('/workspace')
    
    print("Running all tests...")
    print("=" * 50)
    
    # Discover and run all tests
    loader = unittest.TestLoader()
    suite = loader.discover('tests', pattern='test_*.py')
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("=" * 50)
    if result.wasSuccessful():
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)