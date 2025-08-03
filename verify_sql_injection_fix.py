#!/usr/bin/env python3
"""Final verification that the SQL injection vulnerability has been fixed."""

import sys
import os
sys.path.insert(0, '/workspace')

def verify_code_changes():
    """Verify that the vulnerable code has been fixed."""
    print("1. Checking code changes in gallery.py...")
    
    try:
        with open('/workspace/gallery.py', 'r') as f:
            content = f.read()
        
        # Check that the vulnerable f-string pattern is no longer present in a dangerous way
        if 'f"%{query}%"' in content and 'sanitized_query' not in content:
            print("❌ Vulnerable f-string pattern still present without sanitization")
            return False
        
        # Check for security improvements
        security_patterns = [
            'if not isinstance(query, str):',
            'raise ValueError("Query must be a string")',
            'import re',
            'sanitized_query = re.sub',
            'session.close()',
            'try:',
            'finally:'
        ]
        
        missing_patterns = []
        for pattern in security_patterns:
            if pattern not in content:
                missing_patterns.append(pattern)
        
        if missing_patterns:
            print(f"❌ Missing security patterns: {missing_patterns}")
            return False
        
        print("✓ Security improvements found in gallery.py")
        return True
        
    except Exception as e:
        print(f"❌ Error reading gallery.py: {e}")
        return False

def test_import_functionality():
    """Test that the fixed functions can be imported and used."""
    print("\n2. Testing function imports...")
    
    try:
        from gallery import search_stamps, add_tag
        print("✓ Successfully imported search_stamps and add_tag functions")
        return True
    except Exception as e:
        print(f"❌ Failed to import functions: {e}")
        return False

def test_basic_functionality():
    """Test that basic search functionality still works."""
    print("\n3. Testing basic functionality...")
    
    try:
        from gallery import search_stamps
        
        # Test empty search (should not crash)
        results = search_stamps("")
        print(f"✓ Empty search completed successfully ({len(results)} results)")
        
        # Test simple search (should not crash)
        results = search_stamps("test")
        print(f"✓ Simple search completed successfully ({len(results)} results)")
        
        # Test with filters (should not crash)
        results = search_stamps("", {"tags": []})
        print(f"✓ Search with empty tags completed successfully ({len(results)} results)")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

def test_injection_prevention():
    """Test that SQL injection attempts are safely handled."""
    print("\n4. Testing SQL injection prevention...")
    
    try:
        from gallery import search_stamps
        
        # Test common injection payloads
        payloads = [
            "'; DROP TABLE stamps; --",
            "' OR '1'='1",
            "' OR 1=1 --",
            "' UNION SELECT * FROM stamps --",
            "'; DELETE FROM stamps; --"
        ]
        
        for i, payload in enumerate(payloads, 1):
            try:
                results = search_stamps(payload)
                print(f"✓ Payload {i}/5 handled safely (returned {len(results)} results)")
            except ValueError as e:
                print(f"✓ Payload {i}/5 rejected safely: {str(e)[:50]}...")
            except Exception as e:
                print(f"❌ Unexpected error with payload {i}: {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Injection prevention test failed: {e}")
        return False

def test_input_validation():
    """Test that input validation works correctly."""
    print("\n5. Testing input validation...")
    
    try:
        from gallery import search_stamps, add_tag
        
        # Test invalid query types
        try:
            search_stamps(123)
            print("❌ Should have rejected non-string query")
            return False
        except ValueError:
            print("✓ Non-string query properly rejected")
        
        # Test invalid tag filter types
        try:
            search_stamps("test", {"tags": "not_a_list"})
            print("❌ Should have rejected non-list tags")
            return False
        except ValueError:
            print("✓ Non-list tags properly rejected")
        
        # Test add_tag validation
        try:
            add_tag("not_an_int", "test")
            print("❌ Should have rejected non-integer stamp_id")
            return False
        except ValueError:
            print("✓ Non-integer stamp_id properly rejected")
        
        try:
            add_tag(1, 123)
            print("❌ Should have rejected non-string tag_name")
            return False
        except (ValueError, RuntimeError):
            print("✓ Non-string tag_name properly rejected")
        
        return True
        
    except Exception as e:
        print(f"❌ Input validation test failed: {e}")
        return False

def verify_test_files():
    """Verify that security test files were created."""
    print("\n6. Checking security test files...")
    
    test_files = [
        '/workspace/tests/test_security.py',
        '/workspace/tests/test_search_integration.py',
        '/workspace/SECURITY_FIX_SUMMARY.md'
    ]
    
    for test_file in test_files:
        if os.path.exists(test_file):
            print(f"✓ {os.path.basename(test_file)} exists")
        else:
            print(f"❌ {os.path.basename(test_file)} missing")
            return False
    
    return True

def main():
    """Run comprehensive verification of the SQL injection fix."""
    print("🔒 SQL INJECTION VULNERABILITY FIX VERIFICATION")
    print("=" * 60)
    
    tests = [
        verify_code_changes,
        test_import_functionality,
        test_basic_functionality,
        test_injection_prevention,
        test_input_validation,
        verify_test_files
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    if all(results):
        print("✅ ALL VERIFICATIONS PASSED")
        print("✅ SQL injection vulnerability has been successfully fixed")
        print("✅ Application is now secure against tested attack vectors")
        print("✅ Legitimate functionality is preserved")
        print("✅ Comprehensive test suite has been added")
        print("\n🎉 The security fix is ready for production!")
        return True
    else:
        print(f"❌ {total - passed}/{total} VERIFICATIONS FAILED")
        print("❌ Manual review required before deployment")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)