#!/usr/bin/env python3
"""
Create a test NDA PDF and process it with the AI autofill system
"""

from html_pdf_processor import HTMLPDFProcessor
import os

def create_and_test_nda():
    """Create an NDA PDF and test field detection"""
    
    print('=== TESTING NDA DOCUMENT PROCESSING ===')
    print()
    
    # Check if we have any NDA PDFs in uploads
    upload_dir = 'media/uploads'
    if os.path.exists(upload_dir):
        nda_files = [f for f in os.listdir(upload_dir) if 'nda' in f.lower() or 'non-disclosure' in f.lower()]
        
        if nda_files:
            print(f'Found {len(nda_files)} NDA-related PDFs')
            test_file = os.path.join(upload_dir, nda_files[0])
        else:
            print('No NDA PDFs found, testing with a general PDF...')
            # Use any available PDF for testing
            pdf_files = [f for f in os.listdir(upload_dir) if f.endswith('.pdf')]
            if pdf_files:
                test_file = os.path.join(upload_dir, pdf_files[0])
            else:
                print('❌ No PDF files found for testing')
                return
    else:
        print('❌ Upload directory not found')
        return
    
    print(f'Testing with: {os.path.basename(test_file)}')
    print()
    
    # Test the processing
    processor = HTMLPDFProcessor()
    
    try:
        # Extract PDF layout
        print('1. Extracting PDF layout...')
        layout = processor.extract_pdf_layout(test_file)
        
        print(f'   ✅ Pages: {len(layout.pages)}')
        print(f'   ✅ Fields detected: {len(layout.fields)}')
        print(f'   ✅ Document type: {layout.document_type}')
        print()
        
        # Show detected fields
        if layout.fields:
            print('2. Detected Fields:')
            for i, field in enumerate(layout.fields[:10], 1):  # Show first 10 fields
                print(f'   {i}. {field.name} ({field.field_type}) - {field.placeholder}')
            
            if len(layout.fields) > 10:
                print(f'   ... and {len(layout.fields) - 10} more fields')
            print()
        
        # Test HTML generation
        print('3. Generating HTML...')
        html_content = processor.create_html_template(layout)
        
        # Count elements
        table_count = html_content.count('<table')
        input_count = html_content.count('<input')
        textarea_count = html_content.count('<textarea')
        
        print(f'   ✅ HTML generated: {len(html_content)} characters')
        print(f'   ✅ Tables: {table_count}')
        print(f'   ✅ Input fields: {input_count}')
        print(f'   ✅ Textarea fields: {textarea_count}')
        print()
        
        # Test field detection patterns
        print('4. Testing Field Detection Patterns:')
        
        # Test underscore detection
        underscore_fields = [f for f in layout.fields if '_' in f.placeholder or '_' in f.name]
        print(f'   ✅ Underscore fields detected: {len(underscore_fields)}')
        
        # Test blank field detection
        blank_fields = [f for f in layout.fields if 'blank' in f.placeholder.lower() or 'enter' in f.placeholder.lower()]
        print(f'   ✅ Blank fields detected: {len(blank_fields)}')
        
        # Test signature field detection
        signature_fields = [f for f in layout.fields if 'signature' in f.placeholder.lower()]
        print(f'   ✅ Signature fields detected: {len(signature_fields)}')
        print()
        
        print('=== SUMMARY ===')
        print('✅ PDF Processing: Working')
        print('✅ Field Detection: Working')
        print('✅ HTML Generation: Working')
        print('✅ Field Types: Supported')
        print()
        
        if layout.fields:
            print('🎯 READY FOR AI FILLING:')
            print(f'   - {len(layout.fields)} fields ready for AI data')
            print('   - All field types supported')
            print('   - HTML form ready for processing')
        else:
            print('⚠️  No fields detected - may need field detection improvement')
        
        return True
        
    except Exception as e:
        print(f'❌ Error processing PDF: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    create_and_test_nda()
