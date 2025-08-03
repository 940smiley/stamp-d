"""Tests for gallery functionality and thumbnail generation."""

import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from PIL import Image
from io import BytesIO

# Import the function we want to test
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import load_gallery_data
from db import Session, Stamp


class TestGalleryThumbnails(unittest.TestCase):
    """Test cases for gallery thumbnail generation and error handling."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_session = MagicMock()
        self.test_stamps = []
        
        # Create a temporary valid image file
        self.temp_dir = tempfile.mkdtemp()
        self.valid_image_path = os.path.join(self.temp_dir, "valid_image.jpg")
        self.create_test_image(self.valid_image_path)
        
        # Path to non-existent image
        self.nonexistent_image_path = os.path.join(self.temp_dir, "nonexistent.jpg")
        
        # Path to corrupted image file
        self.corrupted_image_path = os.path.join(self.temp_dir, "corrupted.jpg")
        with open(self.corrupted_image_path, 'w') as f:
            f.write("This is not a valid image file")

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def create_test_image(self, path):
        """Create a valid test image file."""
        img = Image.new('RGB', (100, 100), color='red')
        img.save(path, 'JPEG')

    @patch('app.Session')
    def test_load_gallery_data_with_valid_image(self, mock_session_class):
        """Test thumbnail generation with valid image."""
        # Setup mock
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        mock_stamp = MagicMock()
        mock_stamp.image_path = self.valid_image_path
        mock_stamp.id = 1
        mock_stamp.country = "Test Country"
        mock_stamp.denomination = "10c"
        mock_stamp.year = "2023"
        mock_stamp.notes = "Test notes"
        
        mock_session.query.return_value.all.return_value = [mock_stamp]
        
        # Call function
        result = load_gallery_data()
        
        # Verify result
        self.assertEqual(len(result), 1)
        thumb_html, stamp_id, country, denomination, year, notes = result[0]
        
        # Check that thumbnail HTML was generated (should contain img tag)
        self.assertIn("<img src='data:image/png;base64,", thumb_html)
        self.assertIn("width='50'", thumb_html)
        self.assertEqual(stamp_id, 1)
        self.assertEqual(country, "Test Country")

    @patch('app.Session')
    def test_load_gallery_data_with_nonexistent_image(self, mock_session_class):
        """Test thumbnail generation with non-existent image file."""
        # Setup mock
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        mock_stamp = MagicMock()
        mock_stamp.image_path = self.nonexistent_image_path
        mock_stamp.id = 2
        mock_stamp.country = "Test Country 2"
        mock_stamp.denomination = "20c"
        mock_stamp.year = "2023"
        mock_stamp.notes = "Test notes 2"
        
        mock_session.query.return_value.all.return_value = [mock_stamp]
        
        # Call function
        result = load_gallery_data()
        
        # Verify result
        self.assertEqual(len(result), 1)
        thumb_html, stamp_id, country, denomination, year, notes = result[0]
        
        # Check that thumbnail is empty for non-existent file
        self.assertEqual(thumb_html, "")
        self.assertEqual(stamp_id, 2)
        self.assertEqual(country, "Test Country 2")

    @patch('app.Session')
    def test_load_gallery_data_with_corrupted_image(self, mock_session_class):
        """Test thumbnail generation with corrupted image file."""
        # Setup mock
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        mock_stamp = MagicMock()
        mock_stamp.image_path = self.corrupted_image_path
        mock_stamp.id = 3
        mock_stamp.country = "Test Country 3"
        mock_stamp.denomination = "30c"
        mock_stamp.year = "2023"
        mock_stamp.notes = "Test notes 3"
        
        mock_session.query.return_value.all.return_value = [mock_stamp]
        
        # Call function
        result = load_gallery_data()
        
        # Verify result
        self.assertEqual(len(result), 1)
        thumb_html, stamp_id, country, denomination, year, notes = result[0]
        
        # Check that thumbnail is empty for corrupted file
        self.assertEqual(thumb_html, "")
        self.assertEqual(stamp_id, 3)
        self.assertEqual(country, "Test Country 3")

    @patch('app.Session')
    @patch('app.Image.open')
    def test_load_gallery_data_with_image_open_exception(self, mock_image_open, mock_session_class):
        """Test thumbnail generation when Image.open raises an exception."""
        # Setup mock
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        mock_stamp = MagicMock()
        mock_stamp.image_path = self.valid_image_path  # Valid path but Image.open will fail
        mock_stamp.id = 4
        mock_stamp.country = "Test Country 4"
        mock_stamp.denomination = "40c"
        mock_stamp.year = "2023"
        mock_stamp.notes = "Test notes 4"
        
        mock_session.query.return_value.all.return_value = [mock_stamp]
        
        # Make Image.open raise an IOError
        mock_image_open.side_effect = IOError("Cannot identify image file")
        
        # Call function
        result = load_gallery_data()
        
        # Verify result
        self.assertEqual(len(result), 1)
        thumb_html, stamp_id, country, denomination, year, notes = result[0]
        
        # Check that thumbnail is empty when Image.open fails
        self.assertEqual(thumb_html, "")
        self.assertEqual(stamp_id, 4)
        self.assertEqual(country, "Test Country 4")

    @patch('app.Session')
    @patch('app.Image.open')
    def test_load_gallery_data_with_os_error(self, mock_image_open, mock_session_class):
        """Test thumbnail generation when Image.open raises an OSError."""
        # Setup mock
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        mock_stamp = MagicMock()
        mock_stamp.image_path = self.valid_image_path
        mock_stamp.id = 5
        mock_stamp.country = "Test Country 5"
        mock_stamp.denomination = "50c"
        mock_stamp.year = "2023"
        mock_stamp.notes = "Test notes 5"
        
        mock_session.query.return_value.all.return_value = [mock_stamp]
        
        # Make Image.open raise an OSError
        mock_image_open.side_effect = OSError("Permission denied")
        
        # Call function
        result = load_gallery_data()
        
        # Verify result
        self.assertEqual(len(result), 1)
        thumb_html, stamp_id, country, denomination, year, notes = result[0]
        
        # Check that thumbnail is empty when Image.open fails
        self.assertEqual(thumb_html, "")
        self.assertEqual(stamp_id, 5)
        self.assertEqual(country, "Test Country 5")

    @patch('app.Session')
    def test_load_gallery_data_mixed_scenarios(self, mock_session_class):
        """Test thumbnail generation with mixed valid and invalid images."""
        # Setup mock
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        # Create stamps with different scenarios
        valid_stamp = MagicMock()
        valid_stamp.image_path = self.valid_image_path
        valid_stamp.id = 1
        valid_stamp.country = "Valid"
        valid_stamp.denomination = "10c"
        valid_stamp.year = "2023"
        valid_stamp.notes = "Valid image"
        
        invalid_stamp = MagicMock()
        invalid_stamp.image_path = self.nonexistent_image_path
        invalid_stamp.id = 2
        invalid_stamp.country = "Invalid"
        invalid_stamp.denomination = "20c"
        invalid_stamp.year = "2023"
        invalid_stamp.notes = "Invalid image"
        
        corrupted_stamp = MagicMock()
        corrupted_stamp.image_path = self.corrupted_image_path
        corrupted_stamp.id = 3
        corrupted_stamp.country = "Corrupted"
        corrupted_stamp.denomination = "30c"
        corrupted_stamp.year = "2023"
        corrupted_stamp.notes = "Corrupted image"
        
        mock_session.query.return_value.all.return_value = [valid_stamp, invalid_stamp, corrupted_stamp]
        
        # Call function
        result = load_gallery_data()
        
        # Verify result
        self.assertEqual(len(result), 3)
        
        # Check valid stamp has thumbnail
        valid_thumb, _, _, _, _, _ = result[0]
        self.assertIn("<img src='data:image/png;base64,", valid_thumb)
        
        # Check invalid stamps have empty thumbnails
        invalid_thumb, _, _, _, _, _ = result[1]
        self.assertEqual(invalid_thumb, "")
        
        corrupted_thumb, _, _, _, _, _ = result[2]
        self.assertEqual(corrupted_thumb, "")


if __name__ == '__main__':
    unittest.main()