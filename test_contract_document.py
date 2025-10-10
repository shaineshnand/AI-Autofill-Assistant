#!/usr/bin/env python
"""
Test script for contract/legal document field detection
"""
from improved_field_detector import ImprovedFieldDetector, convert_form_fields_to_dict
from intelligent_field_filler import IntelligentFieldFiller

def test_contract_detection():
    """Test field detection for contract documents"""
    
    # Simulate contract text
    contract_text = """
    THIS AGREEMENT IS DATED ON THE DAY OF BETWEEN 20__.
    TELECOM (FIJI) PTE LIMITED a limited liability company
    AND a student at the having the Student Identification number as
    """
    
    print("Testing Contract Document Field Detection")
    print("=" * 60)
    
    # Test with improved field detector
    detector = ImprovedFieldDetector()
    filler = IntelligentFieldFiller()
    
    # Create simulated fields based on contract patterns
    test_fields = [
        {'field_type': 'text', 'context': 'DAY OF'},
        {'field_type': 'text', 'context': 'MONTH'},
        {'field_type': 'text', 'context': 'YEAR 20__'},
        {'field_type': 'name', 'context': 'student name'},
        {'field_type': 'text', 'context': 'institution'},
        {'field_type': 'text', 'context': 'Student Identification number'}
    ]
    
    print("\nSimulated Contract Fields:")
    for i, field in enumerate(test_fields):
        content = filler.generate_field_content(field)
        print(f"{i+1}. {field['context']:30} -> {content}")
    
    print("\n" + "=" * 60)
    print("Contract filling simulation complete!")
    print("\nRecommendations:")
    print("- Upload your contract as PDF")
    print("- System will detect underlines and blank spaces")
    print("- Use 'Fill All' to auto-complete all fields")
    print("- Manual editing available for specific corrections")

if __name__ == "__main__":
    test_contract_detection()


