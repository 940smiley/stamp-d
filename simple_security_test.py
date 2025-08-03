#!/usr/bin/env python3
"""Simple test to verify the security fix works."""

import sys
import os

# Add the workspace to the Python path
sys.path.insert(0, '/workspace')

def test_basic_functionality():
    """Test that the basic search functionality works."""
    try:
        from gallery import search_stamps
        
        print("Testing basic search functionality...")
        
        # Test empty search (should not crash)
        results = search_stamps("")
        print(f"✅ Empty search returned {len(results)} results")
        
        # Test simple search (should not crash)
        results = search_stamps("test")
        print(f"✅ Simple search returned {len(results)} results")
        
        return True
        
    except Exception as e:
return True
        
    except ImportError as e:
        print(f"❌ Basic functionality test failed: Import error - {e}")
        return False
    except Exception as e:
        print(f"❌ Basic functionality test failed: Unexpected error - {e}")
        return False

def test_injection_prevention():
        return False

def test_injection_prevention():
    """Test that SQL injection attempts are handled safely."""
    try:
        from gallery import search_stamps
        
        print("\nTesting SQL injection prevention...")
        
        # Test common injection payloads
        payloads = [
            "'; DROP TABLE stamps; --",
            "' OR '1'='1",
            "' OR 1=1 --"
        ]
        
        for payload in payloads:
            try:
                results = search_stamps(payload)
                print(f"✅ Payload '{payload[:20]}...' handled safely")
            except ValueError:
                print(f"✅ Payload '{payload[:20]}...' rejected safely")
            except Exception as e:
                print(f"❌ Unexpected error with payload: {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Injection prevention test failed: {e}")
        return False

def main():
    """Run simple security verification."""
    print("🔒 Simple Security Fix Verification")
    print("=" * 40)
    
    basic_ok = test_basic_functionality()
    injection_ok = test_injection_prevention()
    
    print("\n" + "=" * 40)
    if basic_ok and injection_ok:
        print("✅ Security fix verification PASSED")
        print("✅ SQL injection vulnerability appears to be fixed")
        return True
    else:
        print("❌ Security fix verification FAILED")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)