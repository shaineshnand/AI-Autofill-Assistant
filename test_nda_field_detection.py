#!/usr/bin/env python3
"""
Test NDA field detection specifically
"""

from html_pdf_processor import HTMLPDFProcessor
import re

def test_nda_field_detection():
    """Test field detection with the NDA content"""
    
    # The NDA content you provided
    nda_text = """TELECOM (FIJI) PTE LIMITED a limited liability company, whose registered
office is located at Level 5, GPO New Wing Building, Edward Street, Suva,
Fiji, (hereinafter called and referred to as "Telecom" which term or
expression as herein used shall where the context so requires or admits
mean and include the said company and its successor or successors and
assigns) on THE FIRST PART;

AND

______________________

a

student

at

the

__________________________________ having the Student Identification
number as _______________________ (hereinafter referred to as "the
recipient" which term of expression as herein shall where the context so
requires or admits and include the said Person and its successor or
successors and assigns) on THE SECOND PART.

IN WITNESS WHEREOF the Parties hereto have caused their respective Company Stamps to be
affixed hereunto two others of the same tenor and date as these presents on this _____ day of
________________ 20__.

Signed by TELECOM (FIJI) PTE LIMITED by its duly
authorised signatory:

..........................................................................
Signature of Authorised Person

…………………………... …………………………..
Print Name Office Held

_____________________________ as signed by the
recipient in person:

..........................................................................
Signature of Authorised Person

…………………………... ………………………….
Print Name Office Held"""
    
    print('=== TESTING NDA CONTENT FIELD DETECTION ===')
    print()
    
    processor = HTMLPDFProcessor()
    
    # Test visual field detection
    fields = processor._detect_visual_fields(nda_text, 0)
    
    print(f'Detected {len(fields)} fields:')
    print()
    
    for i, field in enumerate(fields, 1):
        print(f'{i}. {field.id}')
        print(f'   Placeholder: {field.placeholder}')
        print(f'   Width: {field.width}px')
        print()
    
    # Test HTML conversion
    from dataclasses import dataclass
    from typing import List
    
    @dataclass
    class DocumentLayout:
        title: str
        pages: List[dict]
        fields: List
        extracted_text: str
        document_type: str
    
    # Create a simple layout for testing
    layout = DocumentLayout(
        title="NDA Test",
        pages=[{'page_number': 0, 'text': nda_text, 'fields': fields, 'tables': []}],
        fields=fields,
        extracted_text=nda_text,
        document_type="contract"
    )
    
    html_content = processor.create_html_template(layout)
    
    # Count form elements
    input_count = html_content.count('<input')
    print(f'Input fields in HTML: {input_count}')
    
    if input_count == 0:
        print('❌ NO INPUT FIELDS DETECTED!')
        print('This is the problem - fields are not being converted to HTML inputs')
        
        # Debug: Check what's in the HTML
        print('\nHTML sample (first 1000 chars):')
        print(html_content[:1000])
        
    else:
        print('✅ Input fields detected in HTML')
    
    # Test field embedding specifically
    print('\n=== TESTING FIELD EMBEDDING ===')
    
    test_lines = [
        '______________________',
        '__________________________________ having the Student Identification',
        'number as _______________________',
        'this _____ day of',
        '________________ 20__',
        '…………………………... …………………………..',
        '..........................................................................'
    ]
    
    for line in test_lines:
        print(f'\nTesting line: {line}')
        
        # Find matching fields
        matching_fields = []
        for field in fields:
            if processor._should_embed_field_in_line(line, field):
                matching_fields.append(field)
        
        if matching_fields:
            field = matching_fields[0]
            embedded = processor._embed_field_in_line(line, field)
            print(f'  Embedded: {embedded}')
        else:
            print('  No field embedded')

if __name__ == "__main__":
    test_nda_field_detection()
