"""
Test the PDF recreator with the blue Personal Info Form
"""

import os
from pdf_recreator import PDFRecreator

def test_blue_form():
    """Test PDF recreation with blue Personal Info Form"""
    
    pdf_path = "blue_personal_info_form.pdf"
    if not os.path.exists(pdf_path):
        print(f"Blue form not found: {pdf_path}")
        return False
    
    print(f"Testing PDF Recreation with Blue Personal Info Form")
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
        
        # Check if output exists
        if os.path.exists(result['output_pdf']):
            file_size = os.path.getsize(result['output_pdf'])
            print(f"\nOutput PDF created: {result['output_pdf']}")
            print(f"File size: {file_size} bytes")
            print(f"\nThe recreated PDF should preserve:")
            print("- Original blue input boxes")
            print("- Original layout and spacing")
            print("- Original fonts and formatting")
            print("- Only the data should be filled in")
            return True
        else:
            print(f"\nOutput PDF not found: {result['output_pdf']}")
            return False
    else:
        print(f"PDF Recreation Failed!")
        print(f"Error: {result.get('error', 'Unknown error')}")
        return False

if __name__ == "__main__":
    success = test_blue_form()
    if success:
        print("\nBlue form test completed!")
        print("Check the output PDF to verify original formatting is preserved.")
    else:
        print("\nBlue form test failed!")
