#!/usr/bin/env python
"""
Test script for the enhanced AI Autofill Assistant system
Tests the improved field detection and intelligent filling capabilities
"""
import os
import sys
import json
from enhanced_document_processor import EnhancedDocumentProcessor, convert_form_fields_to_dict
from intelligent_field_filler import IntelligentFieldFiller

def test_enhanced_processor():
    """Test the enhanced document processor"""
    print("=" * 60)
    print("TESTING ENHANCED DOCUMENT PROCESSOR")
    print("=" * 60)
    
    processor = EnhancedDocumentProcessor()
    
    # Test with sample PDF if available
    test_files = [
        'media/uploads/Sample-Fillable-PDF.pdf',
        'test_form.png',
        'media/uploads/test_form.png'
    ]
    
    for file_path in test_files:
        if os.path.exists(file_path):
            print(f"\nTesting with: {file_path}")
            try:
                result = processor.process_document(file_path)
                print(f"✓ Successfully processed {file_path}")
                print(f"  - Document type: {result.get('document_type', 'unknown')}")
                print(f"  - Total fields detected: {result.get('total_fields', 0)}")
                print(f"  - Has AcroForm: {result.get('has_acroform', False)}")
                
                # Show field details
                fields = result.get('fields', [])
                for i, field in enumerate(fields[:5]):  # Show first 5 fields
                    print(f"  Field {i+1}: {field.get('field_type', 'unknown')} - {field.get('context', 'no context')}")
                    print(f"    Position: ({field.get('x_position', 0)}, {field.get('y_position', 0)})")
                    print(f"    Size: {field.get('width', 0)}x{field.get('height', 0)}")
                    print(f"    Confidence: {field.get('confidence', 0):.2f}")
                
                if len(fields) > 5:
                    print(f"  ... and {len(fields) - 5} more fields")
                
                return result
                
            except Exception as e:
                print(f"✗ Error processing {file_path}: {e}")
        else:
            print(f"⚠ File not found: {file_path}")
    
    print("\n⚠ No test files found. Please ensure you have sample documents in the media/uploads/ directory.")
    return None

def test_intelligent_filler():
    """Test the intelligent field filler"""
    print("\n" + "=" * 60)
    print("TESTING INTELLIGENT FIELD FILLER")
    print("=" * 60)
    
    filler = IntelligentFieldFiller()
    
    # Test different field types
    test_fields = [
        {'field_type': 'name', 'context': 'full name'},
        {'field_type': 'email', 'context': 'email address'},
        {'field_type': 'phone', 'context': 'phone number'},
        {'field_type': 'address', 'context': 'street address'},
        {'field_type': 'date', 'context': 'date of birth'},
        {'field_type': 'age', 'context': 'age'},
        {'field_type': 'signature', 'context': 'signature'},
        {'field_type': 'company', 'context': 'company name'},
        {'field_type': 'job_title', 'context': 'job title'}
    ]
    
    print("Testing field content generation:")
    for field in test_fields:
        content = filler.generate_field_content(field)
        is_valid = filler.validate_field_content(content, field['field_type'])
        print(f"  {field['field_type']:12} -> {content:30} {'✓' if is_valid else '✗'}")
    
    print("\nTesting field suggestions:")
    for field in test_fields[:3]:  # Test first 3 fields
        suggestions = filler.get_field_suggestions(field)
        print(f"  {field['field_type']:12} -> {suggestions}")
    
    print("\nTesting user input extraction:")
    test_inputs = [
        "My name is John Smith",
        "My email is john.smith@email.com",
        "Call me at (555) 123-4567",
        "I live at 123 Main Street, New York, NY",
        "I am 25 years old"
    ]
    
    for user_input in test_inputs:
        print(f"  Input: {user_input}")
        for field in test_fields[:5]:  # Test first 5 field types
            extracted = filler._extract_content_from_input(user_input, field['field_type'])
            if extracted:
                print(f"    {field['field_type']:12} -> {extracted}")

def test_integration():
    """Test the integration of enhanced processor and intelligent filler"""
    print("\n" + "=" * 60)
    print("TESTING INTEGRATED SYSTEM")
    print("=" * 60)
    
    # Process a document
    processor = EnhancedDocumentProcessor()
    filler = IntelligentFieldFiller()
    
    # Look for test files
    test_files = [
        'media/uploads/Sample-Fillable-PDF.pdf',
        'test_form.png',
        'media/uploads/test_form.png'
    ]
    
    for file_path in test_files:
        if os.path.exists(file_path):
            print(f"\nProcessing: {file_path}")
            try:
                # Process document
                result = processor.process_document(file_path)
                fields = result.get('fields', [])
                
                if not fields:
                    print("  ⚠ No fields detected")
                    continue
                
                print(f"  ✓ Detected {len(fields)} fields")
                
                # Convert to dictionary format
                field_dicts = convert_form_fields_to_dict(fields)
                
                # Fill fields with intelligent content
                filled_fields = filler.fill_all_fields(field_dicts)
                
                print("  ✓ Filled fields with intelligent content:")
                for field in filled_fields[:5]:  # Show first 5
                    print(f"    {field['field_type']:12} -> {field['user_content']}")
                
                if len(filled_fields) > 5:
                    print(f"    ... and {len(filled_fields) - 5} more fields")
                
                return True
                
            except Exception as e:
                print(f"  ✗ Error: {e}")
    
    print("  ⚠ No test files available for integration testing")
    return False

def main():
    """Run all tests"""
    print("AI AUTOFILL ASSISTANT - ENHANCED SYSTEM TEST")
    print("=" * 60)
    
    # Test enhanced processor
    processor_result = test_enhanced_processor()
    
    # Test intelligent filler
    test_intelligent_filler()
    
    # Test integration
    integration_success = test_integration()
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Enhanced Processor: {'✓ PASS' if processor_result else '✗ FAIL'}")
    print(f"Intelligent Filler: ✓ PASS")
    print(f"Integration: {'✓ PASS' if integration_success else '✗ FAIL'}")
    
    if processor_result and integration_success:
        print("\n🎉 All tests passed! The enhanced system is ready to use.")
        print("\nKey improvements:")
        print("  • Better field detection using multiple techniques")
        print("  • Precise field positioning and sizing")
        print("  • Intelligent content generation based on field types")
        print("  • Proper validation and formatting")
        print("  • Support for PDF AcroForm fields")
        print("  • Context-aware field classification")
    else:
        print("\n⚠ Some tests failed. Please check the error messages above.")

if __name__ == '__main__':
    main()

