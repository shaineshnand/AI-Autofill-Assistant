#!/usr/bin/env python3
"""
Test script to analyze NDA document fields
"""

import re

def analyze_nda_fields():
    """Analyze the NDA document to identify all fields"""
    
    # Sample NDA text with fields
    nda_text = """
    NON-DISCLOSURE AGREEMENT 
    THIS AGREEMENT IS DATED ON THE            DAY OF                             
    BETWEEN 
    20__. 
    TELECOM (FIJI) PTE LIMITED a limited liability company, whose registered 
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
    
    ……………………………...    ………………………….. 
    Print Name                          Office Held 
    
    _____________________________ as signed by the 
    recipient in person:
    
    ..........................................................................  
    Signature of Authorised Person  
    
    ……………………………...     …………………………. 
    Print Name                          Office Held
    """
    
    print('=== NDA DOCUMENT FIELD ANALYSIS ===')
    print()
    
    # Find different types of fields
    fields_found = []
    
    # 1. Underscore fields (blanks)
    underscore_pattern = r'_+'
    underscore_matches = re.findall(underscore_pattern, nda_text)
    for match in underscore_matches:
        fields_found.append({
            'type': 'underscore_blank',
            'content': match,
            'length': len(match),
            'context': 'Blank field for data entry'
        })
    
    # 2. Dotted lines (signature fields)
    dotted_pattern = r'\.{10,}'
    dotted_matches = re.findall(dotted_pattern, nda_text)
    for match in dotted_matches:
        fields_found.append({
            'type': 'signature_line',
            'content': match,
            'length': len(match),
            'context': 'Signature line'
        })
    
    # 3. Date fields
    date_pattern = r'DAY OF.*?20__'
    date_matches = re.findall(date_pattern, nda_text, re.DOTALL)
    for match in date_matches:
        fields_found.append({
            'type': 'date_field',
            'content': match.strip(),
            'length': len(match),
            'context': 'Date field'
        })
    
    # 4. Specific field patterns
    specific_patterns = [
        (r'______________________', 'student_name', 'Student name field'),
        (r'__________________________________', 'institution_name', 'Institution name field'),
        (r'_______________________', 'student_id', 'Student ID field'),
        (r'_____ day of', 'day_field', 'Day field'),
        (r'________________ 20__', 'year_field', 'Year field'),
        (r'……………………………...', 'print_name', 'Print name field'),
        (r'……………………………..', 'office_held', 'Office held field'),
    ]
    
    for pattern, field_type, description in specific_patterns:
        matches = re.findall(pattern, nda_text)
        for match in matches:
            fields_found.append({
                'type': field_type,
                'content': match,
                'length': len(match),
                'context': description
            })
    
    # Group fields by type
    field_types = {}
    for field in fields_found:
        field_type = field['type']
        if field_type not in field_types:
            field_types[field_type] = []
        field_types[field_type].append(field)
    
    # Display results
    print(f'Total fields found: {len(fields_found)}')
    print()
    
    for field_type, fields in field_types.items():
        print(f'📝 {field_type.upper().replace("_", " ")}: {len(fields)} fields')
        for field in fields:
            print(f'   - {field["context"]}: {field["content"]} (length: {field["length"]})')
        print()
    
    # Summary
    print('=== FIELD SUMMARY ===')
    print(f'📅 Date fields: {len(field_types.get("date_field", []))}')
    print(f'📝 Name fields: {len(field_types.get("student_name", [])) + len(field_types.get("print_name", []))}')
    print(f'🏫 Institution fields: {len(field_types.get("institution_name", []))}')
    print(f'🆔 ID fields: {len(field_types.get("student_id", []))}')
    print(f'✍️ Signature fields: {len(field_types.get("signature_line", []))}')
    print(f'📋 Office fields: {len(field_types.get("office_held", []))}')
    print(f'📄 General blanks: {len(field_types.get("underscore_blank", []))}')
    
    return fields_found

if __name__ == "__main__":
    analyze_nda_fields()
