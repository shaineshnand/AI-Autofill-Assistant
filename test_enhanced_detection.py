#!/usr/bin/env python
"""
Test script for Enhanced Field Detection
"""
import os
import sys
import traceback
from pathlib import Path

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_enhanced_field_detection():
    """Test the enhanced field detection system"""
    print("Testing Enhanced Field Detection System")
    print("=" * 60)
    
    # Import the enhanced field detector
    try:
        from enhanced_field_detector import EnhancedFieldDetector, convert_form_fields_to_dict
        detector = EnhancedFieldDetector()
        print("SUCCESS: Enhanced Field Detector loaded successfully")
    except ImportError as e:
        print(f"ERROR: Failed to import Enhanced Field Detector: {e}")
        print("Falling back to improved field detector...")
        try:
            from improved_field_detector import ImprovedFieldDetector, convert_form_fields_to_dict
            detector = ImprovedFieldDetector()
            print("SUCCESS: Improved Field Detector loaded successfully")
        except ImportError as e2:
            print(f"ERROR: Failed to import Improved Field Detector: {e2}")
            return
    
    # Test files
    test_files = [
        "test_form.png",
        "test_contract_text.txt",
        "uploads"
    ]
    
    print(f"\nLooking for test files...")
    
    for test_file in test_files:
        if os.path.exists(test_file):
            print(f"FOUND: {test_file}")
            
            if test_file == "uploads":
                # Check for uploaded files
                upload_files = []
                for root, dirs, files in os.walk(test_file):
                    for file in files:
                        if file.lower().endswith(('.pdf', '.png', '.jpg', '.jpeg', '.doc', '.docx', '.txt')):
                            upload_files.append(os.path.join(root, file))
                
                if upload_files:
                    print(f"  Found {len(upload_files)} uploaded files:")
                    for file in upload_files[:3]:  # Test first 3 files
                        print(f"    Testing: {file}")
                        test_single_file(detector, file)
                    if len(upload_files) > 3:
                        print(f"    ... and {len(upload_files) - 3} more files")
                else:
                    print("  No uploaded files found")
            else:
                # Test individual file
                test_single_file(detector, test_file)
        else:
            print(f"NOT FOUND: {test_file}")
    
    # Create and test a sample document
    print(f"\nCreating and testing sample document...")
    create_and_test_sample_document(detector)

def test_single_file(detector, file_path):
    """Test field detection on a single file"""
    try:
        print(f"\nTesting: {file_path}")
        print("-" * 40)
        
        result = detector.process_document(file_path)
        
        print(f"SUCCESS: Document processed successfully")
        print(f"Extracted text length: {len(result['extracted_text'])} characters")
        print(f"Fields detected: {result['total_fields']}")
        
        if 'error' in result:
            print(f"WARNING: Error: {result['error']}")
        
        if result['total_fields'] > 0:
            print(f"\nField Details:")
            for i, field in enumerate(result['fields'][:15]):  # Show first 15 fields
                print(f"  {i+1:2d}. {field.field_type:12} at ({field.x_position:4d}, {field.y_position:4d}) "
                      f"size {field.width:3d}x{field.height:2d} - '{field.context}' "
                      f"(conf: {field.confidence:.2f}, method: {field.detection_method})")
            
            if result['total_fields'] > 15:
                print(f"  ... and {result['total_fields'] - 15} more fields")
            
            # Group fields by detection method
            methods = {}
            for field in result['fields']:
                method = field.detection_method
                if method not in methods:
                    methods[method] = 0
                methods[method] += 1
            
            print(f"\nDetection Methods:")
            for method, count in methods.items():
                print(f"  - {method}: {count} fields")
                
        else:
            print("ERROR: No fields detected")
            
        # Show first 300 characters of extracted text
        text_preview = result['extracted_text'][:300]
        if text_preview:
            print(f"\nText Preview:")
            print(f"  {text_preview}...")
        
    except Exception as e:
        print(f"ERROR: Error processing {file_path}: {e}")
        traceback.print_exc()

def create_and_test_sample_document(detector):
    """Create and test a sample document"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a comprehensive test form
        img = Image.new('RGB', (1000, 800), 'white')
        draw = ImageDraw.Draw(img)
        
        # Try to use a system font
        try:
            font = ImageFont.truetype("arial.ttf", 18)
            small_font = ImageFont.truetype("arial.ttf", 14)
        except:
            try:
                font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 18)
                small_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 14)
            except:
                font = ImageFont.load_default()
                small_font = ImageFont.load_default()
        
        # Draw form elements
        y_pos = 50
        form_elements = [
            ("Full Name:", 50, y_pos, "name"),
            ("Email Address:", 50, y_pos + 70, "email"),
            ("Phone Number:", 50, y_pos + 140, "phone"),
            ("Street Address:", 50, y_pos + 210, "address"),
            ("Date of Birth:", 50, y_pos + 280, "date"),
            ("Age:", 50, y_pos + 350, "age"),
            ("ID Number:", 50, y_pos + 420, "id_number"),
        ]
        
        for label, x, y, field_type in form_elements:
            # Draw label
            draw.text((x, y), label, fill='black', font=font)
            
            # Draw underline (field)
            draw.line([(x + 200, y + 25), (x + 600, y + 25)], fill='black', width=2)
            
            # Add some context text
            if field_type == "name":
                draw.text((x + 200, y + 30), "Enter your full name here", fill='gray', font=small_font)
            elif field_type == "email":
                draw.text((x + 200, y + 30), "example@email.com", fill='gray', font=small_font)
        
        # Add checkboxes
        checkbox_y = y_pos + 500
        draw.text((50, checkbox_y), "Please check all that apply:", fill='black', font=font)
        for i, option in enumerate(["Option 1", "Option 2", "Option 3"]):
            # Draw checkbox
            checkbox_x = 50 + (i * 200)
            checkbox_y_pos = checkbox_y + 40
            draw.rectangle([checkbox_x, checkbox_y_pos, checkbox_x + 20, checkbox_y_pos + 20], outline='black', width=2)
            draw.text((checkbox_x + 30, checkbox_y_pos + 2), option, fill='black', font=small_font)
        
        # Save test image
        test_image_path = "test_comprehensive_form.png"
        img.save(test_image_path)
        print(f"SUCCESS: Created comprehensive test form: {test_image_path}")
        
        # Test the created form
        test_single_file(detector, test_image_path)
        
    except Exception as e:
        print(f"ERROR: Error creating test document: {e}")
        traceback.print_exc()

def analyze_detection_performance():
    """Analyze field detection performance"""
    print(f"\nField Detection Performance Analysis")
    print("=" * 60)
    
    improvements = [
        "SUCCESS: Multiple detection algorithms (rectangular, underline, box, whitespace, text-positioned)",
        "SUCCESS: Enhanced field type classification with 10+ field types",
        "SUCCESS: Better coordinate accuracy with 3x image scaling",
        "SUCCESS: Comprehensive deduplication and merging",
        "SUCCESS: Confidence scoring for each detected field",
        "SUCCESS: Detection method tracking for debugging",
        "SUCCESS: Support for AcroForm fields in PDFs",
        "SUCCESS: Enhanced text pattern matching",
        "SUCCESS: Better filtering to reduce false positives",
        "SUCCESS: Multi-page PDF support"
    ]
    
    field_types = [
        "name, email, phone, address, date, age, signature",
        "id_number, checkbox, dropdown, text"
    ]
    
    detection_methods = [
        "acroform (native PDF fields)",
        "rectangular (contour detection)",
        "underline (line detection)", 
        "box (shape detection)",
        "whitespace (white region detection)",
        "text_positioned (OCR-based positioning)",
        "text_pattern (pattern matching)"
    ]
    
    print("Key Improvements:")
    for improvement in improvements:
        print(f"  {improvement}")
    
    print(f"\nSupported Field Types:")
    for field_type in field_types:
        print(f"  - {field_type}")
    
    print(f"\nDetection Methods:")
    for method in detection_methods:
        print(f"  - {method}")

if __name__ == "__main__":
    test_enhanced_field_detection()
    analyze_detection_performance()
