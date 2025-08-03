#!/usr/bin/env python3
"""Simple test to verify the thumbnail error handling works."""

import sys
import os
import tempfile
from unittest.mock import MagicMock, patch

# Add workspace to path
sys.path.insert(0, '/workspace')

def test_thumbnail_error_handling():
    """Test that thumbnail generation handles errors gracefully."""
    print("Testing thumbnail error handling...")
    
    try:
        # Import the function
        from app import load_gallery_data
        print("✓ Successfully imported load_gallery_data")
        
        # Create a temporary directory and files for testing
        temp_dir = tempfile.mkdtemp()
        print(f"✓ Created temp directory: {temp_dir}")
        
        # Create a corrupted image file
        corrupted_path = os.path.join(temp_dir, "corrupted.jpg")
        with open(corrupted_path, 'w') as f:
            f.write("This is not a valid image")
        print("✓ Created corrupted image file")
        
        # Mock the database session and stamp
        with patch('app.Session') as mock_session_class:
            mock_session = MagicMock()
            mock_session_class.return_value = mock_session
            
            # Create a mock stamp with corrupted image path
            mock_stamp = MagicMock()
            mock_stamp.image_path = corrupted_path
            mock_stamp.id = 1
            mock_stamp.country = "Test"
            mock_stamp.denomination = "10c"
            mock_stamp.year = "2023"
            mock_stamp.notes = "Test"
            
            mock_session.query.return_value.all.return_value = [mock_stamp]
            
            # Call the function - this should not crash
            result = load_gallery_data()
            print("✓ Function executed without crashing")
            
            # Verify the result
            assert len(result) == 1, f"Expected 1 result, got {len(result)}"
            thumb_html, stamp_id, country, denomination, year, notes = result[0]
            
            # The thumbnail should be empty due to the corrupted image
            assert thumb_html == "", f"Expected empty thumbnail, got: {thumb_html}"
            assert stamp_id == 1, f"Expected stamp_id 1, got {stamp_id}"
            print("✓ Corrupted image handled gracefully - thumbnail is empty")
            
        # Test with non-existent file
        nonexistent_path = os.path.join(temp_dir, "nonexistent.jpg")
        
        with patch('app.Session') as mock_session_class:
            mock_session = MagicMock()
            mock_session_class.return_value = mock_session
            
            mock_stamp = MagicMock()
            mock_stamp.image_path = nonexistent_path
            mock_stamp.id = 2
            mock_stamp.country = "Test2"
            mock_stamp.denomination = "20c"
            mock_stamp.year = "2023"
            mock_stamp.notes = "Test2"
            
            mock_session.query.return_value.all.return_value = [mock_stamp]
            
            result = load_gallery_data()
            print("✓ Function executed with non-existent file")
            
            assert len(result) == 1
            thumb_html, stamp_id, country, denomination, year, notes = result[0]
            assert thumb_html == "", f"Expected empty thumbnail for non-existent file, got: {thumb_html}"
            print("✓ Non-existent file handled gracefully - thumbnail is empty")
            
        # Clean up
        import shutil
        shutil.rmtree(temp_dir)
        print("✓ Cleaned up temp directory")
        
        print("\n🎉 ALL TESTS PASSED! Error handling is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_thumbnail_error_handling()
    sys.exit(0 if success else 1)