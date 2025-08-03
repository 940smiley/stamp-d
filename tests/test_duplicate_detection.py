import os
import sys
import pathlib
import tempfile
import shutil

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

# Use a test database
test_db_path = str(ROOT / "test_duplicate.db")
os.environ["STAMPD_DB_PATH"] = test_db_path

from db import Session, Stamp, init_db, populate_missing_hashes
from app import save_upload
from image_utils import is_duplicate, get_file_hash


def setup_module(module):
    """Set up test database and clean it."""
    init_db()
    session = Session()
    session.query(Stamp).delete()
    session.commit()
    session.close()


def teardown_module(module):
    """Clean up test database."""
    if os.path.exists(test_db_path):
        os.remove(test_db_path)


def create_test_image(content=b"test_image_content"):
    """Create a temporary test image file."""
import os  # Used for file operations, including removing temporary files
import tempfile  # Used for creating temporary files

def create_test_image(content=b"test_image_content"):
    """Create a temporary test image file."""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
    try:
        temp_file.write(content)
        temp_file.close()
        return temp_file.name
    finally:
        os.unlink(temp_file.name)
    temp_file.write(content)
    temp_file.close()
    return temp_file.name


def test_is_duplicate_function():
    """Test that is_duplicate works with hash sets."""
    # Create test images
    image1 = create_test_image(b"image1_content")
    image2 = create_test_image(b"image2_content")
    image3 = create_test_image(b"image1_content")  # Same content as image1
    
    try:
        # Get hashes
        hash1 = get_file_hash(image1)
        hash2 = get_file_hash(image2)
        hash3 = get_file_hash(image3)
        
        # Test with empty hash set
        assert not is_duplicate(image1, set())
        
        # Test with hash set containing different hash
        assert not is_duplicate(image1, {hash2})
        
        # Test with hash set containing same hash
        assert is_duplicate(image1, {hash1})
        
        # Test that identical content produces same hash
        assert hash1 == hash3
        assert is_duplicate(image3, {hash1})
        
    finally:
        # Clean up
        for img in [image1, image2, image3]:
            if os.path.exists(img):
                os.remove(img)


def test_save_upload_duplicate_detection():
    """Test that save_upload correctly detects duplicates using hashes."""
    # Create test images
    image1 = create_test_image(b"unique_image1")
    image2 = create_test_image(b"unique_image2")
    image3 = create_test_image(b"unique_image1")  # Duplicate of image1
    
    try:
        # First upload - should save both unique images
        preview_data1 = [
            [image1, "Country1", "10c", "2020", "Test stamp 1"],
            [image2, "Country2", "20c", "2021", "Test stamp 2"]
        ]
        
        result1 = save_upload(preview_data1)
        assert "successfully" in result1
        
        # Check that both stamps were saved
        session = Session()
        stamps = session.query(Stamp).all()
[image2, "Country2", "20c", "2021", "Test stamp 2"]
        ]
        
        result1 = save_upload(preview_data1)
        assert "successfully" in result1
        
        # Check that both stamps were saved
        try:
            session = Session()
            stamps = session.query(Stamp).all()
            assert len(stamps) == 2
            
            # Verify hashes were stored
            for stamp in stamps:
                assert stamp.file_hash is not None
                assert len(stamp.file_hash) == 32  # MD5 hash length
        except Exception as e:
            print(f"Database operation failed: {str(e)}")
            raise
        finally:
            session.close()
        
        # Second upload - should skip duplicate and save only new one
        image4 = create_test_image(b"unique_image4")
        preview_data2 = [
            [image3, "Country1", "10c", "2020", "Duplicate stamp"],  # Should be skipped
            [image4, "Country3", "30c", "2022", "New stamp"]         # Should be saved
        ]
        
        result2 = save_upload(preview_data2)
        assert "successfully" in result2
        
        # Check that only one new stamp was added (total should be 3, not 4)
        try:
            session = Session()
        
        # Verify hashes were stored
        for stamp in stamps:
            assert stamp.file_hash is not None
            assert len(stamp.file_hash) == 32  # MD5 hash length
        
        session.close()
        
        # Second upload - should skip duplicate and save only new one
        image4 = create_test_image(b"unique_image4")
        preview_data2 = [
            [image3, "Country1", "10c", "2020", "Duplicate stamp"],  # Should be skipped
            [image4, "Country3", "30c", "2022", "New stamp"]         # Should be saved
        ]
        
        result2 = save_upload(preview_data2)
        assert "successfully" in result2
        
        # Check that only one new stamp was added (total should be 3, not 4)
        session = Session()
        stamps = session.query(Stamp).all()
        assert len(stamps) == 3
        session.close()
        
    finally:
        # Clean up
        for img in [image1, image2, image3, image4]:
            if os.path.exists(img):
                os.remove(img)


def test_populate_missing_hashes():
    """Test that populate_missing_hashes works correctly."""
    # Create a test image
    image1 = create_test_image(b"test_content_for_hash")
    
    try:
        # Manually create a stamp without hash
        session = Session()
        stamp = Stamp(
            image_path=image1,
            country="TestCountry",
            denomination="5c",
            year="2023",
            notes="Test without hash"
        )
        session.add(stamp)
        session.commit()
        
        # Verify hash is None
        stamp_id = stamp.id
        session.close()
        
        session = Session()
        stamp = session.query(Stamp).get(stamp_id)
        assert stamp.file_hash is None
        session.close()
        
        # Run populate_missing_hashes
        populate_missing_hashes()
        
        # Verify hash was populated
        session = Session()
        stamp = session.query(Stamp).get(stamp_id)
        assert stamp.file_hash is not None
        assert len(stamp.file_hash) == 32
        session.close()
        
    finally:
        # Clean up
        if os.path.exists(image1):
            os.remove(image1)


if __name__ == "__main__":
    test_is_duplicate_function()
    test_save_upload_duplicate_detection()
    test_populate_missing_hashes()
    print("✅ All duplicate detection tests passed!")