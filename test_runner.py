import sys
import os
sys.path.insert(0, '/workspace')

# Try to import and run a simple test
try:
    from tests.test_gallery import TestGalleryThumbnails
    import unittest
    
    # Create a test suite with just one test
    suite = unittest.TestSuite()
    suite.addTest(TestGalleryThumbnails('test_load_gallery_data_with_nonexistent_image'))
    
    # Run the test
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print(f"Test result: {'PASSED' if result.wasSuccessful() else 'FAILED'}")
    if not result.wasSuccessful():
        for failure in result.failures:
            print(f"Failure: {failure[0]} - {failure[1]}")
        for error in result.errors:
            print(f"Error: {error[0]} - {error[1]}")
            
except Exception as e:
    print(f"Error running test: {e}")
    import traceback
    traceback.print_exc()