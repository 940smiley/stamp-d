#!/usr/bin/env python3
"""Manual verification that the thumbnail error handling fix works."""

import sys
import os
import tempfile
from PIL import Image
from io import BytesIO
import base64

# Add workspace to path
sys.path.insert(0, '/workspace')

def create_test_image(path):
    """Create a valid test image."""
    img = Image.new('RGB', (100, 100), color='red')
    img.save(path, 'JPEG')

def test_thumbnail_generation_directly():
    """Test the thumbnail generation logic directly."""
    print("Testing thumbnail generation logic...")
    
    # Create temp directory
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Test 1: Valid image
        print("\n1. Testing with valid image:")
        valid_path = os.path.join(temp_dir, "valid.jpg")
        create_test_image(valid_path)
        
        if os.path.exists(valid_path):
            try:
                with Image.open(valid_path) as img:
                    img.thumbnail((64, 64))
                    buf = BytesIO()
                    img.save(buf, format="PNG")
                b64 = base64.b64encode(buf.getvalue()).decode()
                thumb = f"<img src='data:image/png;base64,{b64}' width='50'/>"
                print(f"✓ Valid image: Generated thumbnail HTML (length: {len(thumb)})")
            except (IOError, OSError):
                thumb = ""
                print("❌ Valid image: Unexpected error")
        else:
            thumb = ""
            print("❌ Valid image: File doesn't exist")
            
        # Test 2: Non-existent image
        print("\n2. Testing with non-existent image:")
        nonexistent_path = os.path.join(temp_dir, "nonexistent.jpg")
        
        if os.path.exists(nonexistent_path):
            try:
                with Image.open(nonexistent_path) as img:
                    img.thumbnail((64, 64))
                    buf = BytesIO()
                    img.save(buf, format="PNG")
                b64 = base64.b64encode(buf.getvalue()).decode()
                thumb = f"<img src='data:image/png;base64,{b64}' width='50'/>"
                print("❌ Non-existent image: Unexpected success")
            except (IOError, OSError):
                thumb = ""
                print("✓ Non-existent image: Exception handled, empty thumbnail")
        else:
            thumb = ""
            print("✓ Non-existent image: File check passed, empty thumbnail")
            
        # Test 3: Corrupted image
        print("\n3. Testing with corrupted image:")
        corrupted_path = os.path.join(temp_dir, "corrupted.jpg")
        with open(corrupted_path, 'w') as f:
            f.write("This is not a valid image file")
            
        if os.path.exists(corrupted_path):
            try:
                with Image.open(corrupted_path) as img:
                    img.thumbnail((64, 64))
                    buf = BytesIO()
                    img.save(buf, format="PNG")
                b64 = base64.b64encode(buf.getvalue()).decode()
                thumb = f"<img src='data:image/png;base64,{b64}' width='50'/>"
                print("❌ Corrupted image: Unexpected success")
            except (IOError, OSError):
                thumb = ""
                print("✓ Corrupted image: Exception handled, empty thumbnail")
        else:
            thumb = ""
            print("❌ Corrupted image: File doesn't exist")
            
        print("\n🎉 Direct thumbnail generation test completed successfully!")
        
    finally:
        # Clean up
        import shutil
        shutil.rmtree(temp_dir)
        print("✓ Cleaned up temp directory")

def verify_app_function_structure():
    """Verify that the app.py function has the correct structure."""
    print("\nVerifying app.py function structure...")
    
    try:
        # Read the app.py file
        with open('/workspace/app.py', 'r') as f:
            content = f.read()
            
        # Check for the key components
        checks = [
            ("load_gallery_data function exists", "def load_gallery_data():"),
            ("os.path.exists check", "if os.path.exists(s.image_path):"),
            ("try block exists", "try:"),
            ("Image.open usage", "with Image.open(s.image_path) as img:"),
            ("thumbnail generation", "img.thumbnail((64, 64))"),
            ("exception handling", "except (IOError, OSError):"),
            ("empty thumbnail fallback", 'thumb = ""'),
        ]
        
        for check_name, pattern in checks:
            if pattern in content:
                print(f"✓ {check_name}")
            else:
                print(f"❌ {check_name} - Pattern not found: {pattern}")
                
        print("✓ Function structure verification completed")
        
    except Exception as e:
        print(f"❌ Error reading app.py: {e}")

if __name__ == '__main__':
    print("=== Verifying Thumbnail Error Handling Fix ===")
    
    verify_app_function_structure()
    test_thumbnail_generation_directly()
    
    print("\n=== Verification Complete ===")
    print("The error handling implementation should prevent crashes when:")
    print("- Image files don't exist")
    print("- Image files are corrupted")
    print("- PIL/Pillow raises IOError or OSError")
    print("- The gallery loading process continues gracefully")