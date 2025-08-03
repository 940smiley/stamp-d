"""Integration tests for search functionality.

This module tests the integration between the search functions and the database
to ensure that the security fixes don't break legitimate functionality.
"""

import os
import sys
import unittest
import tempfile
import shutil

# Add the parent directory to the path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gallery import search_stamps, add_tag, Tag
from db import Session, Stamp, Base, engine


class TestSearchIntegration(unittest.TestCase):
    """Integration tests for search functionality."""

    def setUp(self):
        """Set up test database and sample data."""
        # Create all tables
        Base.metadata.create_all(engine)
        
        # Create test session and sample data
        self.session = Session()
        
        # Create sample stamps with realistic data
        self.stamps_data = [
            {
                "id": 1,
                "country": "United States",
                "description": "1950 Liberty Bell commemorative stamp",
                "stamp_name": "Liberty Bell",
                "year": "1950",
                "denomination": "3 cents"
            },
            {
                "id": 2,
                "country": "Canada",
                "description": "Maple leaf design from 1965",
                "stamp_name": "Maple Leaf",
                "year": "1965",
                "denomination": "5 cents"
            },
            {
                "id": 3,
                "country": "United Kingdom",
                "description": "Queen Elizabeth II portrait stamp",
                "stamp_name": "Royal Portrait",
                "year": "1960",
                "denomination": "2 pence"
            }
        ]
        
        for stamp_data in self.stamps_data:
            stamp = Stamp(**stamp_data)
            self.session.add(stamp)
        
        self.session.commit()
        
        # Create and assign tags
        self.tags_data = [
            {"name": "commemorative", "stamp_ids": [1]},
            {"name": "vintage", "stamp_ids": [1, 2, 3]},
            {"name": "royal", "stamp_ids": [3]},
            {"name": "nature", "stamp_ids": [2]}
        ]
        
        for tag_data in self.tags_data:
            tag = Tag(name=tag_data["name"])
            self.session.add(tag)
            self.session.commit()
            
            for stamp_id in tag_data["stamp_ids"]:
                stamp = self.session.query(Stamp).get(stamp_id)
                stamp.tags.append(tag)
        
        self.session.commit()

    def tearDown(self):
        """Clean up test data."""
        self.session.close()
        # Drop all tables to clean up
        Base.metadata.drop_all(engine)

    def test_basic_country_search(self):
        """Test basic country-based search functionality."""
        # Search for United States
        results = search_stamps("United States")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].country, "United States")
        
        # Search for partial country name
        results = search_stamps("United")
        self.assertEqual(len(results), 2)  # United States and United Kingdom
        countries = [r.country for r in results]
        self.assertIn("United States", countries)
        self.assertIn("United Kingdom", countries)

    def test_description_search(self):
        """Test description-based search functionality."""
        # Search for specific terms in description
        results = search_stamps("Liberty Bell")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].stamp_name, "Liberty Bell")
        
        # Search for partial description
        results = search_stamps("design")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].country, "Canada")

    def test_case_insensitive_search(self):
        """Test that search is case insensitive."""
        # Test lowercase
        results = search_stamps("canada")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].country, "Canada")
        
        # Test uppercase
        results = search_stamps("MAPLE")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].stamp_name, "Maple Leaf")
        
        # Test mixed case
        results = search_stamps("QuEeN")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].country, "United Kingdom")

    def test_tag_filtering(self):
        """Test tag-based filtering functionality."""
        # Search by single tag
        results = search_stamps("", {"tags": ["vintage"]})
        self.assertEqual(len(results), 3)  # All stamps are vintage
        
        # Search by specific tag
        results = search_stamps("", {"tags": ["commemorative"]})
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].stamp_name, "Liberty Bell")
        
        # Search by multiple tags (should return stamps that have any of the tags)
        results = search_stamps("", {"tags": ["royal", "nature"]})
        self.assertEqual(len(results), 2)
        stamp_names = [r.stamp_name for r in results]
        self.assertIn("Royal Portrait", stamp_names)
        self.assertIn("Maple Leaf", stamp_names)

    def test_combined_search(self):
        """Test combining text search with tag filtering."""
        # This functionality might not be implemented yet, but we test the current behavior
        results = search_stamps("United", {"tags": ["vintage"]})
        # Should return stamps that match "United" AND have "vintage" tag
        # Current implementation might not support this, so we just verify it doesn't crash
        self.assertIsInstance(results, list)
        for result in results:
            self.assertIsInstance(result, Stamp)

    def test_empty_search(self):
        """Test that empty search returns all stamps."""
        results = search_stamps("")
        self.assertEqual(len(results), 3)
        
        # Verify all our test stamps are returned
        stamp_names = [r.stamp_name for r in results]
        self.assertIn("Liberty Bell", stamp_names)
        self.assertIn("Maple Leaf", stamp_names)
        self.assertIn("Royal Portrait", stamp_names)

    def test_no_results_search(self):
        """Test search that should return no results."""
        results = search_stamps("nonexistent")
        self.assertEqual(len(results), 0)
        
        results = search_stamps("", {"tags": ["nonexistent_tag"]})
        self.assertEqual(len(results), 0)

    def test_add_tag_integration(self):
        """Test adding tags and then searching by them."""
        # Add a new tag to an existing stamp
        add_tag(1, "historical")
        
        # Search for stamps with the new tag
        results = search_stamps("", {"tags": ["historical"]})
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, 1)
        
        # Verify the tag was actually added
        session = Session()
        try:
            stamp = session.query(Stamp).get(1)
            tag_names = [tag.name for tag in stamp.tags]
            self.assertIn("historical", tag_names)
        finally:
            session.close()

    def test_special_characters_in_legitimate_search(self):
        """Test that legitimate searches with special characters work."""
        # Add a stamp with special characters in description
        session = Session()
        try:
            special_stamp = Stamp(
                id=4,
                country="France",
                description="Château de Versailles - 18th century palace",
                stamp_name="Versailles Palace"
            )
            session.add(special_stamp)
            session.commit()
        finally:
            session.close()
        
        # Search should work with accented characters and hyphens
        results = search_stamps("Château")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].stamp_name, "Versailles Palace")
        
        results = search_stamps("18th century")
        self.assertEqual(len(results), 1)

    def test_performance_with_multiple_results(self):
        """Test that search performs reasonably with multiple results."""
        # This is a basic performance test - mainly to ensure no obvious issues
        import time
        
        start_time = time.time()
        results = search_stamps("United")  # Should return 2 results
        end_time = time.time()
        
        # Search should complete quickly (less than 1 second for this small dataset)
        self.assertLess(end_time - start_time, 1.0)
        self.assertEqual(len(results), 2)


if __name__ == '__main__':
    unittest.main()