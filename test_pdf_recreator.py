"""
Test script for the PDF Recreator functionality
"""

import os
import sys
from pdf_recreator import PDFRecreator

def test_pdf_recreator():
    """Test the PDF recreator with a sample PDF"""
    
    # Initialize the recreator
    recreator = PDFRecreator()
    
    # Test with a sample PDF if it exists
    test_files = [
        "test_form.pdf",
        "test_contract.pdf", 
        "test_document.pdf",
        "uploads/test.pdf",
        "media/uploads/test.pdf"
    ]
    
    test_pdf = None
    for file_path in test_files:
        if os.path.exists(file_path):
            test_pdf = file_path
            break
    
    if not test_pdf:
        print("No test PDF found. Please create a test PDF file named 'test_form.pdf' in the root directory.")
        print("You can use any PDF with form fields, dotted lines, or blank spaces.")
        return False
    
    print(f"Testing with PDF: {test_pdf}")
    print("=" * 50)
    
    try:
        # Process the PDF
        result = recreator.process_pdf(test_pdf)
        
        if result['success']:
            print("PDF Recreation Successful!")
            print(f"Input PDF: {result['input_pdf']}")
            print(f"Output PDF: {result['output_pdf']}")
            print(f"Document Type: {result['document_type']}")
            print(f"Fields Detected: {result['fields_detected']}")
            print(f"Fields Filled: {result['fields_filled']}")
            print(f"Extracted Text Preview: {result['extracted_text'][:200]}...")
            print(f"Filled Data: {result['filled_data']}")
            
            # Check if output file exists
            if os.path.exists(result['output_pdf']):
                print(f"Output PDF created successfully: {result['output_pdf']}")
                file_size = os.path.getsize(result['output_pdf'])
                print(f"File size: {file_size} bytes")
            else:
                print("Output PDF was not created")
                
        else:
            print("PDF Recreation Failed!")
            print(f"Error: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"Error during testing: {str(e)}")
        return False
    
    return True

def create_sample_pdf():
    """Create a sample PDF for testing if none exists"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        sample_pdf = "test_form.pdf"
        c = canvas.Canvas(sample_pdf, pagesize=letter)
        width, height = letter
        
        # Add title
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 50, "Sample Form for Testing")
        
        # Add form fields
        y_pos = height - 100
        fields = [
            ("Name:", "_________________"),
            ("Date:", "_________________"),
            ("Address:", "_________________"),
            ("Phone:", "_________________"),
            ("Email:", "_________________"),
            ("Amount:", "$_______________"),
            ("Signature:", "_________________")
        ]
        
        for label, field in fields:
            c.setFont("Helvetica", 12)
            c.drawString(50, y_pos, label)
            c.drawString(150, y_pos, field)
            y_pos -= 30
        
        # Add some dotted lines
        c.drawString(50, y_pos - 20, "Additional Information:")
        c.drawString(50, y_pos - 40, "................................................")
        c.drawString(50, y_pos - 70, "................................................")
        
        c.save()
        print(f"Created sample PDF: {sample_pdf}")
        return sample_pdf
        
    except Exception as e:
        print(f"Error creating sample PDF: {str(e)}")
        return None

if __name__ == "__main__":
    print("Testing PDF Recreator")
    print("=" * 50)
    
    # Try to test with existing PDF
    success = test_pdf_recreator()
    
    if not success:
        print("\nCreating sample PDF for testing...")
        sample_pdf = create_sample_pdf()
        
        if sample_pdf:
            print("\nTesting with newly created sample PDF...")
            success = test_pdf_recreator()
    
    if success:
        print("\nAll tests passed! PDF Recreator is working correctly.")
        print("\nNext steps:")
        print("1. Upload a PDF to your Django app")
        print("2. Click the 'Recreate Editable PDF (AI-Filled)' button")
        print("3. Download your recreated PDF with AI-filled data")
    else:
        print("\nTests failed. Please check the error messages above.")
        sys.exit(1)
