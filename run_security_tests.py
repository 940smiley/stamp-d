#!/usr/bin/env python3
"""Run the security tests to verify SQL injection prevention."""

import sys
import os
import unittest

# Add the workspace to the Python path
sys.path.insert(0, '/workspace')

# Import and run the test module
if __name__ == '__main__':
    # Change to the workspace directory
    os.chdir('/workspace')
    
    # Discover and run security tests
    loader = unittest.TestLoader()
    suite = loader.discover('tests', pattern='test_security.py')
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)