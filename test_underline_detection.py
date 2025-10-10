#!/usr/bin/env python
"""
Test script for underline detection in contract documents
"""
import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from improved_field_detector import ImprovedFieldDetector, convert_form_fields_to_dict
from intelligent_field_filler import IntelligentFieldFiller

def test_underline_detection():
    """Test underline and blank space detection"""
    
    print("Testing Underline Detection for Contract Documents")
    print("=" * 70)
    
    # Read the test contract
    if os.path.exists('test_contract_text.txt'):
        with open('test_contract_text.txt', 'r', encoding='utf-8') as f:
            contract_text = f.read()
        
        print("\nContract Text:")
        print("-" * 70)
        print(contract_text[:300] + "...")
        print("-" * 70)
        
        # Test with improved detector
        detector = ImprovedFieldDetector()
        result = detector._process_text_file('test_contract_text.txt')
        
        print(f"\nExtracted text length: {len(result['extracted_text'])}")
        print(f"Total fields detected: {result['total_fields']}")
        
        if result['fields']:
            print("\nDetected Fields:")
            for i, field in enumerate(result['fields']):
                print(f"  {i+1}. {field.field_type:15} - {field.context[:60]}")
            
            # Test intelligent filling
            print("\n" + "=" * 70)
            print("Testing Intelligent Filling:")
            print("=" * 70)
            
            filler = IntelligentFieldFiller()
            field_dicts = convert_form_fields_to_dict(result['fields'])
            
            for i, field in enumerate(field_dicts[:10]):  # Show first 10
                content = filler.generate_field_content(field)
                print(f"  {i+1}. {field['field_type']:15} - {field['context'][:40]:40} => {content}")
            
            # Count field types
            field_types = {}
            for field in result['fields']:
                field_types[field.field_type] = field_types.get(field.field_type, 0) + 1
            
            print(f"\nField Type Summary:")
            for ftype, count in field_types.items():
                print(f"  {ftype:15}: {count} fields")
        else:
            print("\nNo fields detected!")
            print("This might indicate the detector needs more enhancement.")
    else:
        print("Test contract file not found!")

if __name__ == "__main__":
    test_underline_detection()



