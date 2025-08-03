"""Security tests for Stamp'd application.

This module contains tests to verify that the application is protected against
SQL injection and other security vulnerabilities.
"""

import os
import sys
import unittest
import tempfile
import shutil
from unittest.mock import patch, MagicMock

# Add the parent directory to the path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gallery import search_stamps, add_tag, Tag
from db import Session, Stamp, Base, engine


class TestSQLInjectionPrevention(unittest.TestCase):
    """Test cases to verify SQL injection vulnerabilities are prevented."""

    def setUp(self):
        """Set up test database and sample data."""
        # Create all tables
        Base.metadata.create_all(engine)
        
        # Create test session and sample data
        self.session = Session()
        
        # Create sample stamps
        self.stamp1 = Stamp(
            id=1,
            country="United States",
            description="Beautiful stamp from 1950",
            stamp_name="Test Stamp 1"
        )
        self.stamp2 = Stamp(
            id=2,
            country="Canada",
            description="Vintage maple leaf design",
            stamp_name="Test Stamp 2"
        )
        
        self.session.add(self.stamp1)
        self.session.add(self.stamp2)
        self.session.commit()
        
        # Create sample tags
        self.tag1 = Tag(name="vintage")
        self.tag2 = Tag(name="rare")
        self.session.add(self.tag1)
        self.session.add(self.tag2)
        self.session.commit()
        
        # Associate tags with stamps
        self.stamp1.tags.append(self.tag1)
        self.stamp2.tags.append(self.tag2)
        self.session.commit()

    def tearDown(self):
        """Clean up test data."""
        self.session.close()
        # Drop all tables to clean up
        Base.metadata.drop_all(engine)

    def test_search_stamps_legitimate_query(self):
        """Test that legitimate search queries work correctly."""
        # Test basic country search
        results = search_stamps("United States")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].country, "United States")
        
        # Test partial match
        results = search_stamps("United")
        self.assertEqual(len(results), 1)
        
        # Test description search
        results = search_stamps("Beautiful")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].description, "Beautiful stamp from 1950")
        
        # Test case insensitive search
        results = search_stamps("canada")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].country, "Canada")

    def test_search_stamps_sql_injection_attempts(self):
        """Test that SQL injection attempts are prevented."""
        # Common SQL injection payloads
        injection_payloads = [
            "'; DROP TABLE stamps; --",
            "' OR '1'='1",
            "' OR 1=1 --",
            "' UNION SELECT * FROM stamps --",
            "'; DELETE FROM stamps; --",
            "' OR 'x'='x",
            "1'; UPDATE stamps SET country='HACKED' WHERE '1'='1",
            "'; INSERT INTO stamps (country) VALUES ('INJECTED'); --",
            "' AND (SELECT COUNT(*) FROM stamps) > 0 --",
            "' OR (SELECT COUNT(*) FROM sqlite_master) > 0 --"
        ]
        
        for payload in injection_payloads:
            with self.subTest(payload=payload):
                # The search should either return no results or legitimate results
                # but should never cause database corruption or expose sensitive data
                try:
                    results = search_stamps(payload)
                    # Verify that the results are legitimate stamps, not injected data
                    for result in results:
                        self.assertIsInstance(result, Stamp)
                        # Verify the data hasn't been corrupted
                        self.assertIn(result.country, ["United States", "Canada"])
                except Exception as e:
                    # If an exception is raised, it should be a ValueError from our validation
                    # not a database error
                    self.assertIsInstance(e, ValueError)
                
                # Verify that our test data is still intact after the injection attempt
                all_stamps = search_stamps("")
                self.assertEqual(len(all_stamps), 2)
                countries = [stamp.country for stamp in all_stamps]
                self.assertIn("United States", countries)
                self.assertIn("Canada", countries)

    def test_search_stamps_with_special_characters(self):
        """Test that special characters are handled safely."""
        special_chars = [
            "test'quote",
            'test"doublequote',
            "test\\backslash",
            "test%percent",
            "test_underscore",
            "test;semicolon",
            "test--comment",
            "test/*comment*/",
            "test<script>",
            "test&amp;",
        ]
        
        for char_test in special_chars:
            with self.subTest(special_char=char_test):
                # These should not cause errors and should not return unexpected results
                results = search_stamps(char_test)
                # Results should be empty or contain legitimate stamps
                for result in results:
                    self.assertIsInstance(result, Stamp)

    def test_search_stamps_tag_filter_injection(self):
        """Test that tag filter parameter is protected against injection."""
        # Test legitimate tag filtering
        results = search_stamps("", {"tags": ["vintage"]})
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].country, "United States")
        
        # Test injection attempts through tags parameter
        injection_attempts = [
            {"tags": ["'; DROP TABLE tags; --"]},
            {"tags": ["' OR '1'='1"]},
            {"tags": ["vintage'; DELETE FROM tags WHERE '1'='1"]},
            {"tags": "not_a_list"},  # Wrong type
            {"tags": [123]},  # Wrong element type
            {"tags": [None]},  # None element
        ]
        
        for attempt in injection_attempts:
            with self.subTest(injection=attempt):
                try:
                    results = search_stamps("", attempt)
                    # If successful, results should be legitimate
                    for result in results:
                        self.assertIsInstance(result, Stamp)
                except (ValueError, TypeError):
                    # Expected for invalid input types
                    pass
                
                # Verify database integrity
                all_stamps = search_stamps("")
                self.assertEqual(len(all_stamps), 2)

    def test_add_tag_legitimate_usage(self):
        """Test that add_tag works correctly with legitimate input."""
        # Add a new tag to stamp 1
        add_tag(1, "new_tag")
        
        # Verify the tag was added
        results = search_stamps("", {"tags": ["new_tag"]})
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, 1)

    def test_add_tag_sql_injection_attempts(self):
        """Test that add_tag is protected against SQL injection."""
        injection_payloads = [
            "'; DROP TABLE tags; --",
            "' OR '1'='1",
            "test'; DELETE FROM stamps; --",
            "'; INSERT INTO tags (name) VALUES ('INJECTED'); --",
        ]
        
        for payload in injection_payloads:
            with self.subTest(payload=payload):
                try:
                    add_tag(1, payload)
                    # If successful, verify no malicious data was inserted
                    session = Session()
                    try:
                        all_tags = session.query(Tag).all()
                        tag_names = [tag.name for tag in all_tags]
                        # Should not contain the raw injection payload
                        self.assertNotIn(payload, tag_names)
                        # Should not contain obvious injection indicators
                        for name in tag_names:
                            self.assertNotIn("DROP", name.upper())
                            self.assertNotIn("DELETE", name.upper())
                            self.assertNotIn("INSERT", name.upper())
                    finally:
                        session.close()
                except (ValueError, RuntimeError):
                    # Expected for invalid input
                    pass
                
                # Verify database integrity
                all_stamps = search_stamps("")
                self.assertEqual(len(all_stamps), 2)

    def test_add_tag_input_validation(self):
        """Test that add_tag properly validates input parameters."""
        # Test invalid stamp_id types
        with self.assertRaises(ValueError):
            add_tag("not_an_int", "test_tag")
        
        with self.assertRaises(ValueError):
            add_tag(-1, "test_tag")
        
        with self.assertRaises(ValueError):
            add_tag(0, "test_tag")
        
        # Test invalid tag_name types
        with self.assertRaises(ValueError):
            add_tag(1, 123)
        
        with self.assertRaises(ValueError):
            add_tag(1, None)
        
        # Test empty tag name
        with self.assertRaises(ValueError):
            add_tag(1, "")
        
        with self.assertRaises(ValueError):
            add_tag(1, "   ")  # Only whitespace
        
        # Test non-existent stamp
        with self.assertRaises(RuntimeError):
            add_tag(999, "test_tag")

    def test_search_stamps_input_validation(self):
        """Test that search_stamps properly validates input parameters."""
        # Test invalid query types
        with self.assertRaises(ValueError):
            search_stamps(123)
        
        with self.assertRaises(ValueError):
            search_stamps(None)
        
        # Test invalid filters types
        with self.assertRaises(ValueError):
            search_stamps("test", {"tags": "not_a_list"})

    def test_session_management(self):
        """Test that database sessions are properly managed."""
        # This test ensures that sessions are closed even if exceptions occur
        with patch('gallery.Session') as mock_session_class:
            mock_session = MagicMock()
            mock_session_class.return_value = mock_session
            
            # Test that session.close() is called even when an exception occurs
            mock_session.query.side_effect = Exception("Database error")
            
            try:
                search_stamps("test")
            except Exception:
                pass
            
            mock_session.close.assert_called_once()

    def test_sanitization_effectiveness(self):
        """Test that input sanitization removes dangerous characters."""
        # Test query sanitization
        results = search_stamps("test'; DROP TABLE stamps; --")
        # Should not cause any database errors and should return empty or safe results
        for result in results:
            self.assertIsInstance(result, Stamp)
        
        # Test tag name sanitization
        try:
            add_tag(1, "test'; DROP TABLE tags; --")
            # If successful, verify the tag name was sanitized
            session = Session()
            try:
                tags = session.query(Tag).filter(Tag.name.like("%test%")).all()
                for tag in tags:
                    # Should not contain SQL injection characters
                    self.assertNotIn("';", tag.name)
                    self.assertNotIn("--", tag.name)
            finally:
                session.close()
        except ValueError:
            # Expected if sanitization results in empty string
            pass


if __name__ == '__main__':
    unittest.main()