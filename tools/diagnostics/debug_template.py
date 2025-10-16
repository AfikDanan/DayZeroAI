#!/usr/bin/env python3
"""
Debug template loading issue
"""

import sys
import os
from pathlib import Path
from PIL import Image

# Add the parent directory to Python path
sys.path.append('.')

def debug_template_loading():
    """Debug why template isn't loading"""
    print("🔍 Template Loading Debug")
    print("=" * 40)
    
    # Test different path variations
    template_paths = [
        "preboarding_service/app/utils/static/template.png",
        "app/utils/static/template.png",
        "./app/utils/static/template.png",
        Path("app/utils/static/template.png"),
        Path("preboarding_service/app/utils/static/template.png"),
    ]
    
    print(f"📁 Current working directory: {os.getcwd()}")
    print()
    
    for i, template_path in enumerate(template_paths, 1):
        print(f"{i}. Testing path: {template_path}")
        
        try:
            # Check if file exists
            path_obj = Path(template_path)
            exists = path_obj.exists()
            print(f"   📄 File exists: {exists}")
            
            if exists:
                # Try to open the image
                try:
                    with Image.open(template_path) as img:
                        print(f"   ✅ Image loaded successfully!")
                        print(f"   📏 Size: {img.size}")
                        print(f"   🎨 Mode: {img.mode}")
                        
                        # Test the actual code path
                        img_rgb = img.convert('RGB')
                        print(f"   🔄 Converted to RGB: {img_rgb.mode}")
                        
                        return template_path  # Return working path
                        
                except Exception as e:
                    print(f"   ❌ Failed to load image: {e}")
            else:
                # Show what files are actually in the directory
                parent_dir = path_obj.parent
                if parent_dir.exists():
                    files = list(parent_dir.glob("*"))
                    print(f"   📂 Files in {parent_dir}: {[f.name for f in files]}")
                else:
                    print(f"   📂 Directory doesn't exist: {parent_dir}")
        
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()
    
    return None

def test_template_in_slide_creation():
    """Test template loading in actual slide creation"""
    print("🎨 Testing Template in Slide Creation")
    print("=" * 40)
    
    from app.models.webhook import EmployeeData
    from app.services.video_generator import VideoGenerator
    from datetime import date
    
    # Create test data
    employee_data = EmployeeData(
        employee_id="TEMPLATE_TEST",
        name="Template Test User",
        email="test@company.com",
        position="Template Tester",
        team="Engineering",
        manager="Manager",
        start_date=date(2025, 10, 20),
        office="Office",
        tech_stack=["Python"],
        first_day_schedule=[],
        first_week_schedule={}
    )
    
    # Create video generator
    video_gen = VideoGenerator()
    
    # Test slide creation
    output_path = Path("debug_template_slide.png")
    
    try:
        result_path = video_gen._create_welcome_slide(employee_data, output_path)
        
        if output_path.exists():
            file_size = output_path.stat().st_size
            print(f"✅ Slide created: {output_path}")
            print(f"📏 File size: {file_size:,} bytes")
            
            # Check if it's using template or fallback
            with Image.open(output_path) as img:
                # Get dominant colors to see if it's the template or solid background
                colors = img.getcolors(maxcolors=1000000)
                print(f"🎨 Unique colors: {len(colors)}")
                
                # Check for the fallback background color
                fallback_color = (248, 247, 252)  # #f8f7fc
                has_fallback = any(color[1] == fallback_color for color in colors)
                
                if has_fallback:
                    print("⚠️ Using fallback background (template not loaded)")
                else:
                    print("✅ Template appears to be loaded (no fallback color)")
            
            return True
        else:
            print("❌ Slide not created")
            return False
            
    except Exception as e:
        print(f"❌ Error creating slide: {e}")
        import traceback
        traceback.print_exc()
        return False

def fix_template_path():
    """Suggest fixes for template path issue"""
    print("🔧 Template Path Fix Suggestions")
    print("=" * 40)
    
    # Find the correct working path
    working_path = debug_template_loading()
    
    if working_path:
        print(f"✅ Working path found: {working_path}")
        print()
        print("🔧 To fix the issue, update the video_generator.py:")
        print(f'   Change: template_path = Path("preboarding_service/app/utils/static/template.png")')
        print(f'   To:     template_path = Path("{working_path}")')
    else:
        print("❌ No working path found")
        print()
        print("🔧 Possible solutions:")
        print("1. Check if template.png exists in app/utils/static/")
        print("2. Verify the file is a valid PNG image")
        print("3. Use absolute path or adjust relative path")
        print("4. Add debug prints in the video generator")

def main():
    """Main debug function"""
    print("🐛 Template Loading Debug Tool")
    print("=" * 50)
    
    # Debug template loading
    fix_template_path()
    
    print()
    
    # Test in actual slide creation
    test_template_in_slide_creation()
    
    print("\n" + "=" * 50)
    print("🎯 Debug Complete!")

if __name__ == "__main__":
    main()