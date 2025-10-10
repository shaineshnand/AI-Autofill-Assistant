#!/usr/bin/env python
"""
Test script for the enhanced selection logic
"""
from intelligent_field_filler import IntelligentFieldFiller

def test_selection_logic():
    """Test the intelligent field filler with different field types"""
    filler = IntelligentFieldFiller()

    # Test different field types
    test_fields = [
        {'field_type': 'checkbox', 'context': 'Option 1'},
        {'field_type': 'checkbox', 'context': 'Option 2'},
        {'field_type': 'radio', 'context': 'Dropdown2'},
        {'field_type': 'dropdown', 'context': 'Please select an item from the combo/dropdown list'},
        {'field_type': 'name', 'context': 'Please enter your name'},
        {'field_type': 'text', 'context': 'Name of Dependent'}
    ]

    print('Testing Intelligent Field Filler with Selection Logic')
    print('=' * 60)

    for i, field in enumerate(test_fields):
        content = filler.generate_field_content(field)
        print(f'{i+1}. {field["field_type"]} - "{field["context"]}"')
        print(f'   Generated: "{content}"')
        print()

if __name__ == "__main__":
    test_selection_logic()

