#!/usr/bin/env python
"""
Test script for improved field detection
"""
import os
import sys
import django
from django.test import Client
from django.conf import settings

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_autofill_project.settings')
django.setup()

def test_improved_field_detection():
    """Test the improved field detection system"""
    print("Testing Improved Field Detection System")
    print("=" * 50)
    
    # Test the improved field detector directly
    try:
        from improved_field_detector import ImprovedFieldDetector, convert_form_fields_to_dict
        
        detector = ImprovedFieldDetector()
        
        # Test with a sample PDF if available
        test_files = [
            'media/uploads/Sample-Fillable-PDF.pdf',
            'test_form.png',
            'media/uploads/test_form.png'
        ]
        
        for test_file in test_files:
            if os.path.exists(test_file):
                print(f"\nTesting with: {test_file}")
                result = detector.process_document(test_file)
                
                print(f"Extracted text length: {len(result['extracted_text'])}")
                print(f"Total fields detected: {result['total_fields']}")
                
                if result['fields']:
                    print("\nDetected fields:")
                    for i, field in enumerate(result['fields'][:5]):  # Show first 5 fields
                        print(f"  {i+1}. {field.field_type} at ({field.x_position}, {field.y_position}) - {field.context}")
                else:
                    print("No fields detected")
                
                # Convert to dict format
                field_dicts = convert_form_fields_to_dict(result['fields'])
                print(f"\nConverted to dict format: {len(field_dicts)} fields")
                
                if field_dicts:
                    print("Sample field dict:")
                    print(field_dicts[0])
                
                break
        else:
            print("No test files found")
            
    except Exception as e:
        print(f"Error testing improved detector: {e}")
        import traceback
        traceback.print_exc()
    
    # Test the upload endpoint
    print("\n" + "=" * 50)
    print("Testing Upload Endpoint with Improved Detection")
    print("=" * 50)
    
    try:
        client = Client()
        
        # Test with a sample file
        test_files = [
            'media/uploads/Sample-Fillable-PDF.pdf',
            'test_form.png'
        ]
        
        for test_file in test_files:
            if os.path.exists(test_file):
                print(f"\nTesting upload with: {test_file}")
                
                with open(test_file, 'rb') as f:
                    response = client.post('/upload/', {'file': f}, format='multipart')
                
                print(f"Response status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"Success: {data.get('success', False)}")
                    print(f"Document ID: {data.get('document_id', 'N/A')}")
                    
                    if 'result' in data:
                        result = data['result']
                        print(f"Extracted text length: {len(result.get('extracted_text', ''))}")
                        print(f"Total blanks: {result.get('total_blanks', 0)}")
                    
                    if 'document' in data and 'fields' in data['document']:
                        fields = data['document']['fields']
                        print(f"Fields in document: {len(fields)}")
                        
                        if fields:
                            print("\nField details:")
                            for i, field in enumerate(fields[:5]):  # Show first 5 fields
                                print(f"  {i+1}. {field.get('field_type', 'unknown')} at ({field.get('x_position', 0)}, {field.get('y_position', 0)})")
                                print(f"      Context: {field.get('context', 'N/A')}")
                                print(f"      Size: {field.get('width', 0)}x{field.get('height', 0)}")
                else:
                    print(f"Error: {response.status_code}")
                    if hasattr(response, 'data'):
                        print(f"Error details: {response.data}")
                
                break
        else:
            print("No test files found for upload testing")
            
    except Exception as e:
        print(f"Error testing upload endpoint: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_improved_field_detection()

