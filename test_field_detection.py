#!/usr/bin/env python
"""
Test script to evaluate field detection across different document types
"""
import os
import sys
import traceback
from pathlib import Path

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_field_detection():
    """Test field detection on various document types"""
    print("🔍 Testing Field Detection System")
    print("=" * 50)
    
    # Import the field detector
    try:
        from improved_field_detector import ImprovedFieldDetector, convert_form_fields_to_dict
        detector = ImprovedFieldDetector()
        print("✅ Improved Field Detector loaded successfully")
    except ImportError as e:
        print(f"❌ Failed to import Improved Field Detector: {e}")
        return
    
    # Test files to check
    test_files = [
        "test_form.png",
        "test_contract_text.txt", 
        "uploads",  # Check if there are uploaded files
    ]
    
    print(f"\n📁 Looking for test files...")
    
    for test_file in test_files:
        if os.path.exists(test_file):
            print(f"✅ Found: {test_file}")
            
            if test_file == "uploads":
                # Check for uploaded files
                upload_files = []
                for root, dirs, files in os.walk(test_file):
                    for file in files:
                        if file.lower().endswith(('.pdf', '.png', '.jpg', '.jpeg', '.doc', '.docx', '.txt')):
                            upload_files.append(os.path.join(root, file))
                
                if upload_files:
                    print(f"  📄 Found {len(upload_files)} uploaded files:")
                    for file in upload_files[:5]:  # Show first 5
                        print(f"    - {file}")
                    if len(upload_files) > 5:
                        print(f"    ... and {len(upload_files) - 5} more")
                else:
                    print("  📄 No uploaded files found")
            else:
                # Test individual file
                test_single_file(detector, test_file)
        else:
            print(f"❌ Not found: {test_file}")
    
    print(f"\n🧪 Testing with sample documents...")
    
    # Create a simple test document if none exist
    create_test_document()

def test_single_file(detector, file_path):
    """Test field detection on a single file"""
    try:
        print(f"\n📄 Testing: {file_path}")
        print("-" * 30)
        
        result = detector.process_document(file_path)
        
        print(f"✅ Document processed successfully")
        print(f"📝 Extracted text length: {len(result['extracted_text'])} characters")
        print(f"🎯 Fields detected: {result['total_fields']}")
        
        if result['total_fields'] > 0:
            print(f"\n📋 Field Details:")
            for i, field in enumerate(result['fields'][:10]):  # Show first 10 fields
                print(f"  {i+1}. {field.field_type} at ({field.x_position}, {field.y_position}) "
                      f"size {field.width}x{field.height} - '{field.context}' (conf: {field.confidence:.2f})")
            
            if result['total_fields'] > 10:
                print(f"  ... and {result['total_fields'] - 10} more fields")
        else:
            print("❌ No fields detected")
            
        # Show first 200 characters of extracted text
        text_preview = result['extracted_text'][:200]
        if text_preview:
            print(f"\n📝 Text Preview:")
            print(f"  {text_preview}...")
        
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        traceback.print_exc()

def create_test_document():
    """Create a simple test document for field detection"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a simple form image
        img = Image.new('RGB', (800, 600), 'white')
        draw = ImageDraw.Draw(img)
        
        # Try to use a system font
        try:
            font = ImageFont.truetype("arial.ttf", 16)
        except:
            try:
                font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 16)
            except:
                font = ImageFont.load_default()
        
        # Draw form elements
        y_pos = 50
        form_elements = [
            ("Name:", 50, y_pos),
            ("Email:", 50, y_pos + 60),
            ("Phone:", 50, y_pos + 120),
            ("Address:", 50, y_pos + 180),
            ("Date:", 50, y_pos + 240),
        ]
        
        for label, x, y in form_elements:
            # Draw label
            draw.text((x, y), label, fill='black', font=font)
            
            # Draw underline (field)
            draw.line([(x + 100, y + 20), (x + 400, y + 20)], fill='black', width=2)
        
        # Save test image
        test_image_path = "test_simple_form.png"
        img.save(test_image_path)
        print(f"✅ Created test form: {test_image_path}")
        
        # Test the created form
        from improved_field_detector import ImprovedFieldDetector
        detector = ImprovedFieldDetector()
        test_single_file(detector, test_image_path)
        
    except Exception as e:
        print(f"❌ Error creating test document: {e}")

def analyze_field_detection_issues():
    """Analyze common field detection issues"""
    print(f"\n🔍 Field Detection Analysis")
    print("=" * 50)
    
    issues = [
        "1. Missing fields - Detection algorithms too restrictive",
        "2. False positives - Detecting non-form elements as fields", 
        "3. Poor positioning - Coordinates not accurate",
        "4. Wrong field types - Misclassification of field types",
        "5. Duplicate fields - Multiple algorithms detecting same field",
        "6. Text extraction issues - OCR not reading text properly"
    ]
    
    solutions = [
        "1. Expand detection patterns and reduce thresholds",
        "2. Add better filtering for actual form elements",
        "3. Improve coordinate calculation and scaling",
        "4. Enhance field type classification logic",
        "5. Improve deduplication algorithm",
        "6. Tune OCR parameters and preprocessing"
    ]
    
    print("📋 Common Issues:")
    for issue in issues:
        print(f"  {issue}")
    
    print(f"\n💡 Solutions:")
    for solution in solutions:
        print(f"  {solution}")

if __name__ == "__main__":
    test_field_detection()
    analyze_field_detection_issues()

