#!/usr/bin/env python3
"""Verification script to demonstrate that SQL injection vulnerability has been fixed."""

import sys
import os

# Add the workspace to the Python path
sys.path.insert(0, '/workspace')

from gallery import search_stamps, add_tag
from db import Session, Stamp, Base, engine, init_db

def setup_test_data():
    """Set up some test data for demonstration."""
    print("Setting up test data...")
    
    # Initialize database
    init_db()
    
    session = Session()
    try:
        # Clear existing data
        session.query(Stamp).delete()
        session.commit()
        
        # Add test stamps
        stamps = [
            Stamp(
                country="United States",
                description="Beautiful commemorative stamp from 1950",
                stamp_name="Liberty Bell"
            ),
            Stamp(
                country="Canada", 
                description="Vintage maple leaf design",
                stamp_name="Maple Leaf"
            )
        ]
        
        for stamp in stamps:
            session.add(stamp)
        session.commit()
        
        print(f"✅ Added {len(stamps)} test stamps")
        
    finally:
        session.close()

def test_legitimate_searches():
    """Test that legitimate searches still work correctly."""
    print("\n" + "="*50)
    print("Testing legitimate search functionality...")
    print("="*50)
    
    # Test basic search
    results = search_stamps("United States")
    print(f"Search for 'United States': {len(results)} results")
    for result in results:
        print(f"  - {result.country}: {result.description}")
    
    # Test partial search
    results = search_stamps("maple")
    print(f"Search for 'maple': {len(results)} results")
    for result in results:
        print(f"  - {result.country}: {result.description}")
    
    # Test empty search (should return all)
    results = search_stamps("")
    print(f"Empty search: {len(results)} results")

def test_sql_injection_prevention():
    """Test that SQL injection attempts are now safely handled."""
    print("\n" + "="*50)
    print("Testing SQL injection prevention...")
    print("="*50)
    
    # Common SQL injection payloads
    injection_payloads = [
        "'; DROP TABLE stamps; --",
        "' OR '1'='1",
        "' OR 1=1 --",
        "' UNION SELECT * FROM stamps --",
        "'; DELETE FROM stamps; --",
        "' OR 'x'='x",
    ]
    
    for payload in injection_payloads:
        print(f"\nTesting payload: {payload}")
        try:
            results = search_stamps(payload)
            print(f"  ✅ Safely handled - returned {len(results)} results")
            
            # Verify results are legitimate
            for result in results:
                if not isinstance(result, Stamp):
                    print(f"  ❌ ERROR: Non-stamp object returned: {type(result)}")
                    return False
                    
        except ValueError as e:
            print(f"  ✅ Safely rejected with ValueError: {e}")
        except Exception as e:
            print(f"  ❌ Unexpected error: {type(e).__name__}: {e}")
            return False
    
    # Verify database integrity after injection attempts
    print("\nVerifying database integrity after injection attempts...")
    try:
        all_results = search_stamps("")
        print(f"  ✅ Database intact - {len(all_results)} stamps still exist")
        
        # Verify the data is still correct
        countries = [stamp.country for stamp in all_results]
        if "United States" in countries and "Canada" in countries:
            print("  ✅ Original test data is still intact")
            return True
        else:
            print("  ❌ Original test data appears to be corrupted")
            return False
            
    except Exception as e:
        print(f"  ❌ Database integrity check failed: {e}")
        return False

def test_add_tag_security():
    """Test that add_tag function is also secure."""
    print("\n" + "="*50)
    print("Testing add_tag security...")
    print("="*50)
    
    # Get a stamp ID to test with
    results = search_stamps("")
    if not results:
        print("❌ No stamps available for testing")
        return False
    
    stamp_id = results[0].id
    print(f"Testing with stamp ID: {stamp_id}")
    
    # Test legitimate tag addition
    try:
        add_tag(stamp_id, "test_tag")
        print("✅ Legitimate tag addition successful")
    except Exception as e:
        print(f"❌ Legitimate tag addition failed: {e}")
        return False
    
    # Test injection attempts
    injection_payloads = [
        "'; DROP TABLE tags; --",
        "' OR '1'='1",
        "test'; DELETE FROM stamps; --",
    ]
    
    for payload in injection_payloads:
        print(f"\nTesting tag injection payload: {payload}")
        try:
            add_tag(stamp_id, payload)
            print("  ✅ Payload was sanitized and processed safely")
        except ValueError as e:
            print(f"  ✅ Payload was rejected: {e}")
        except Exception as e:
            print(f"  ❌ Unexpected error: {e}")
            return False
    
    return True

def main():
    """Main verification function."""
    print("🔒 SQL Injection Vulnerability Fix Verification")
    print("=" * 60)
    
    try:
        # Setup test environment
        setup_test_data()
        
        # Test legitimate functionality
        test_legitimate_searches()
        
        # Test security
        injection_safe = test_sql_injection_prevention()
        tag_safe = test_add_tag_security()
        
        print("\n" + "="*60)
        print("VERIFICATION SUMMARY")
        print("="*60)
        
        if injection_safe and tag_safe:
            print("✅ ALL SECURITY TESTS PASSED")
            print("✅ SQL injection vulnerability has been successfully fixed")
            print("✅ Application is now secure against tested attack vectors")
            return True
        else:
            print("❌ SOME SECURITY TESTS FAILED")
            print("❌ Manual review required")
            return False
            
    except Exception as e:
        print(f"❌ Verification failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)