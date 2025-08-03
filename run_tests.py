#!/usr/bin/env python3
"""Run the gallery tests to verify error handling implementation."""

import sys
import os
import unittest

# Add the workspace to the Python path
sys.path.insert(0, '/workspace')

# Import and run the test module
if __name__ == '__main__':
    # Change to the workspace directory
    os.chdir('/workspace')
    
    # Discover and run tests
    loader = unittest.TestLoader()
    suite = loader.discover('tests', pattern='test_gallery.py')
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)