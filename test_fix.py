#!/usr/bin/env python3
"""
Simple test script to verify the duplicate detection fix works.
"""

import os
import sys
import tempfile

# Add the workspace to the path
sys.path.insert(0, '/workspace')

# Set up test database
test_db_path = '/workspace/test_fix.db'
os.environ['STAMPD_DB_PATH'] = test_db_path

try:
    from db import init_db, Session, Stamp
    from image_utils import is_duplicate, get_file_hash
    from app import save_upload
    
    def create_test_image(content):
        """Create a temporary test image file."""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
        temp_file.write(content)
        temp_file.close()
        return temp_file.name
    
    def test_duplicate_detection():
        print("🧪 Testing duplicate detection fix...")
        
        # Initialize database
        init_db()
        
        # Clean up any existing data
        session = Session()
        session.query(Stamp).delete()
        session.commit()
        session.close()
        
        # Create test images
        image1 = create_test_image(b"test_image_content_1")
        image2 = create_test_image(b"test_image_content_2")
        image3 = create_test_image(b"test_image_content_1")  # Duplicate of image1
        
        try:
            # Test 1: is_duplicate function with hash set
            print("  ✓ Testing is_duplicate function...")
            hash1 = get_file_hash(image1)
            hash2 = get_file_hash(image2)
            
            # Should not be duplicate with empty set
            assert not is_duplicate(image1, set()), "Failed: empty set should not show duplicate"
            
            # Should not be duplicate with different hash
            assert not is_duplicate(image1, {hash2}), "Failed: different hash should not show duplicate"
            
            # Should be duplicate with same hash
            assert is_duplicate(image1, {hash1}), "Failed: same hash should show duplicate"
            
            print("  ✓ is_duplicate function works correctly")
            
            # Test 2: save_upload function
            print("  ✓ Testing save_upload function...")
            
            # First upload
            preview_data1 = [
                [image1, "Country1", "10c", "2020", "Test stamp 1"],
                [image2, "Country2", "20c", "2021", "Test stamp 2"]
            ]
            
            result1 = save_upload(preview_data1)
            assert "successfully" in result1, f"Failed: save_upload returned: {result1}"
            
            # Check stamps were saved
            session = Session()
            stamps = session.query(Stamp).all()
            assert len(stamps) == 2, f"Failed: expected 2 stamps, got {len(stamps)}"
            
            # Check hashes were stored
            for stamp in stamps:
                assert stamp.file_hash is not None, "Failed: file_hash should not be None"
                assert len(stamp.file_hash) == 32, f"Failed: hash length should be 32, got {len(stamp.file_hash)}"
            
            session.close()
            
            # Second upload with duplicate
            image4 = create_test_image(b"test_image_content_4")
            preview_data2 = [
                [image3, "Country1", "10c", "2020", "Duplicate stamp"],  # Should be skipped
                [image4, "Country3", "30c", "2022", "New stamp"]         # Should be saved
            ]
            
            result2 = save_upload(preview_data2)
            assert "successfully" in result2, f"Failed: save_upload returned: {result2}"
            
            # Check only one new stamp was added
            session = Session()
            stamps = session.query(Stamp).all()
            assert len(stamps) == 3, f"Failed: expected 3 stamps (duplicate should be skipped), got {len(stamps)}"
            session.close()
            
            print("  ✓ save_upload function works correctly with duplicate detection")
            
            print("✅ All tests passed! The duplicate detection fix is working correctly.")
            
        finally:
            # Clean up test images
            for img in [image1, image2, image3, image4]:
                if os.path.exists(img):
                    os.remove(img)
    
    if __name__ == "__main__":
        test_duplicate_detection()
        
        # Clean up test database
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
            
except Exception as e:
    print(f"❌ Test failed with error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)