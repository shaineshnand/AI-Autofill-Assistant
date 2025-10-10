#!/usr/bin/env python
"""
Test script specifically for PDF field detection
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

def test_pdf_field_detection():
    """Test PDF field detection specifically"""
    print("Testing PDF Field Detection")
    print("=" * 50)
    
    # Test the improved field detector directly with PDF
    try:
        from improved_field_detector import ImprovedFieldDetector, convert_form_fields_to_dict
        
        detector = ImprovedFieldDetector()
        
        # Test with PDF files
        pdf_files = [f for f in os.listdir('media/uploads') if f.endswith('.pdf')]
        if pdf_files:
            test_file = os.path.join('media/uploads', pdf_files[0])
            print(f"Testing with PDF: {test_file}")
            
            result = detector.process_document(test_file)
            
            print(f"Extracted text length: {len(result['extracted_text'])}")
            print(f"Total fields detected: {result['total_fields']}")
            
            if result['fields']:
                print("\nDetected fields:")
                for i, field in enumerate(result['fields']):
                    print(f"  {i+1}. {field.field_type} at ({field.x_position}, {field.y_position}) - {field.context[:50]}")
                    
                # Check for specific field types
                field_types = {}
                for field in result['fields']:
                    field_types[field.field_type] = field_types.get(field.field_type, 0) + 1
                
                print(f"\nField type summary:")
                for ftype, count in field_types.items():
                    print(f"  {ftype}: {count} fields")
            else:
                print("No fields detected in PDF")
        else:
            print("No PDF files found for testing")
            
    except Exception as e:
        print(f"Error testing PDF detector: {e}")
        import traceback
        traceback.print_exc()
    
    # Test the upload endpoint with PDF
    print("\n" + "=" * 50)
    print("Testing Upload Endpoint with PDF")
    print("=" * 50)
    
    try:
        client = Client()
        
        # Test with PDF files
        pdf_files = [f for f in os.listdir('media/uploads') if f.endswith('.pdf')]
        if pdf_files:
            test_file = os.path.join('media/uploads', pdf_files[0])
            print(f"Testing upload with PDF: {test_file}")
            
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
                        for i, field in enumerate(fields):
                            print(f"  {i+1}. {field.get('field_type', 'unknown')} at ({field.get('x_position', 0)}, {field.get('y_position', 0)})")
                            print(f"      Context: {field.get('context', 'N/A')}")
                            print(f"      Size: {field.get('width', 0)}x{field.get('height', 0)}")
                            
                        # Check for specific field types
                        field_types = {}
                        for field in fields:
                            ftype = field.get('field_type', 'unknown')
                            field_types[ftype] = field_types.get(ftype, 0) + 1
                        
                        print(f"\nField type summary:")
                        for ftype, count in field_types.items():
                            print(f"  {ftype}: {count} fields")
            else:
                print(f"Error: {response.status_code}")
                if hasattr(response, 'data'):
                    print(f"Error details: {response.data}")
        else:
            print("No PDF files found for upload testing")
            
    except Exception as e:
        print(f"Error testing upload endpoint: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pdf_field_detection()

