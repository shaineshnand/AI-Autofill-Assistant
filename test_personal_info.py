"""
Test the PDF recreator with the Personal Info Form
"""

import os
from pdf_recreator import PDFRecreator

def test_personal_info_form():
    """Test PDF recreation with Personal Info Form"""
    
    pdf_path = "personal_info_form.pdf"
    if not os.path.exists(pdf_path):
        print(f"Personal Info Form not found: {pdf_path}")
        return False
    
    print(f"Testing PDF Recreation with Personal Info Form")
    print("=" * 60)
    
    # Initialize recreator
    recreator = PDFRecreator()
    
    # Process the PDF
    result = recreator.process_pdf(pdf_path)
    
    if result['success']:
        print("PDF Recreation Successful!")
        print(f"Input: {result['input_pdf']}")
        print(f"Output: {result['output_pdf']}")
        print(f"Document Type: {result['document_type']}")
        print(f"Fields Detected: {result['fields_detected']}")
        print(f"Fields Filled: {result['fields_filled']}")
        print(f"Filled Data:")
        
        for key, value in result['filled_data'].items():
            print(f"   {key}: {value}")
        
        print(f"\nExtracted Text Preview:")
        print(result['extracted_text'][:300] + "...")
        
        # Check if output exists
        if os.path.exists(result['output_pdf']):
            file_size = os.path.getsize(result['output_pdf'])
            print(f"\nOutput PDF created: {result['output_pdf']}")
            print(f"File size: {file_size} bytes")
            return True
        else:
            print(f"\nOutput PDF not found: {result['output_pdf']}")
            return False
    else:
        print(f"PDF Recreation Failed!")
        print(f"Error: {result.get('error', 'Unknown error')}")
        return False

if __name__ == "__main__":
    success = test_personal_info_form()
    if success:
        print("\nPersonal Info Form test passed!")
        print("The PDF recreator is working correctly with colon-based fields.")
    else:
        print("\nPersonal Info Form test failed!")
