#!/usr/bin/env python
"""
Training Script for Universal Document Processing System
This script demonstrates how to train the system on various document types
"""
import os
import sys
import json
import logging
from typing import List, Dict, Any

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from universal_document_processor import UniversalDocumentProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_sample_training_data() -> List[Dict]:
    """
    Create sample training data for various document types
    """
    training_data = [
        # Personal Information Fields
        {
            'text': 'Please enter your full name:',
            'field_type': 'name',
            'document_type': 'application_form',
            'context': 'full name',
            'confidence': 1.0
        },
        {
            'text': 'Email Address:',
            'field_type': 'email',
            'document_type': 'application_form',
            'context': 'email address',
            'confidence': 1.0
        },
        {
            'text': 'Phone Number:',
            'field_type': 'phone',
            'document_type': 'application_form',
            'context': 'phone number',
            'confidence': 1.0
        },
        {
            'text': 'Date of Birth:',
            'field_type': 'date_of_birth',
            'document_type': 'application_form',
            'context': 'date of birth',
            'confidence': 1.0
        },
        {
            'text': 'Social Security Number:',
            'field_type': 'ssn',
            'document_type': 'application_form',
            'context': 'social security number',
            'confidence': 1.0
        },
        
        # Financial Fields
        {
            'text': 'Annual Income:',
            'field_type': 'income',
            'document_type': 'financial_form',
            'context': 'annual income',
            'confidence': 1.0
        },
        {
            'text': 'Bank Account Number:',
            'field_type': 'bank_account',
            'document_type': 'financial_form',
            'context': 'bank account number',
            'confidence': 1.0
        },
        {
            'text': 'Credit Score:',
            'field_type': 'credit_score',
            'document_type': 'financial_form',
            'context': 'credit score',
            'confidence': 1.0
        },
        
        # Medical Fields
        {
            'text': 'Patient ID:',
            'field_type': 'patient_id',
            'document_type': 'medical_form',
            'context': 'patient id',
            'confidence': 1.0
        },
        {
            'text': 'Insurance Provider:',
            'field_type': 'insurance',
            'document_type': 'medical_form',
            'context': 'insurance provider',
            'confidence': 1.0
        },
        {
            'text': 'Current Medications:',
            'field_type': 'medications',
            'document_type': 'medical_form',
            'context': 'current medications',
            'confidence': 1.0
        },
        {
            'text': 'Known Allergies:',
            'field_type': 'allergies',
            'document_type': 'medical_form',
            'context': 'known allergies',
            'confidence': 1.0
        },
        
        # Legal Fields
        {
            'text': 'Case Number:',
            'field_type': 'case_number',
            'document_type': 'legal_document',
            'context': 'case number',
            'confidence': 1.0
        },
        {
            'text': 'Court Name:',
            'field_type': 'court',
            'document_type': 'legal_document',
            'context': 'court name',
            'confidence': 1.0
        },
        {
            'text': 'Attorney Name:',
            'field_type': 'attorney',
            'document_type': 'legal_document',
            'context': 'attorney name',
            'confidence': 1.0
        },
        
        # Education Fields
        {
            'text': 'Student ID:',
            'field_type': 'student_id',
            'document_type': 'education_form',
            'context': 'student id',
            'confidence': 1.0
        },
        {
            'text': 'GPA:',
            'field_type': 'gpa',
            'document_type': 'education_form',
            'context': 'gpa',
            'confidence': 1.0
        },
        {
            'text': 'Major:',
            'field_type': 'major',
            'document_type': 'education_form',
            'context': 'major',
            'confidence': 1.0
        },
        
        # Generic Text Fields
        {
            'text': 'Comments:',
            'field_type': 'text',
            'document_type': 'application_form',
            'context': 'comments',
            'confidence': 1.0
        },
        {
            'text': 'Additional Information:',
            'field_type': 'text',
            'document_type': 'application_form',
            'context': 'additional information',
            'confidence': 1.0
        },
        
        # Checkbox Fields
        {
            'text': 'Check all that apply:',
            'field_type': 'checkbox',
            'document_type': 'application_form',
            'context': 'check all that apply',
            'confidence': 1.0
        },
        {
            'text': 'I agree to the terms and conditions',
            'field_type': 'checkbox',
            'document_type': 'contract',
            'context': 'terms and conditions',
            'confidence': 1.0
        },
        
        # Dropdown Fields
        {
            'text': 'Please select your state:',
            'field_type': 'dropdown',
            'document_type': 'application_form',
            'context': 'select state',
            'confidence': 1.0
        },
        {
            'text': 'Choose your preferred contact method:',
            'field_type': 'dropdown',
            'document_type': 'application_form',
            'context': 'contact method',
            'confidence': 1.0
        }
    ]
    
    return training_data

def create_document_templates(processor: UniversalDocumentProcessor):
    """
    Create document templates for various document types
    """
    templates = [
        {
            'document_type': 'application_form',
            'description': 'General application forms for various purposes',
            'field_patterns': {
                'name': ['name', 'full name', 'applicant name'],
                'email': ['email', 'email address'],
                'phone': ['phone', 'telephone', 'contact number'],
                'address': ['address', 'home address', 'mailing address'],
                'date_of_birth': ['date of birth', 'dob', 'birth date'],
                'ssn': ['ssn', 'social security number']
            },
            'validation_rules': {
                'email': ['email_format'],
                'phone': ['phone_format'],
                'ssn': ['ssn_format'],
                'date_of_birth': ['date_format']
            }
        },
        {
            'document_type': 'financial_form',
            'description': 'Financial forms for loans, applications, etc.',
            'field_patterns': {
                'income': ['income', 'annual income', 'monthly income'],
                'bank_account': ['bank account', 'account number'],
                'credit_score': ['credit score', 'fico score'],
                'assets': ['assets', 'total assets', 'net worth']
            },
            'validation_rules': {
                'income': ['numeric', 'positive'],
                'credit_score': ['numeric', 'range_300_850']
            }
        },
        {
            'document_type': 'medical_form',
            'description': 'Medical forms and health-related documents',
            'field_patterns': {
                'patient_id': ['patient id', 'patient number', 'mrn'],
                'insurance': ['insurance', 'health insurance'],
                'medications': ['medications', 'current medications'],
                'allergies': ['allergies', 'known allergies']
            },
            'validation_rules': {
                'patient_id': ['alphanumeric'],
                'medications': ['text_list'],
                'allergies': ['text_list']
            }
        },
        {
            'document_type': 'legal_document',
            'description': 'Legal documents and court forms',
            'field_patterns': {
                'case_number': ['case number', 'case id', 'docket number'],
                'court': ['court', 'court name', 'jurisdiction'],
                'attorney': ['attorney', 'lawyer', 'counsel']
            },
            'validation_rules': {
                'case_number': ['alphanumeric'],
                'court': ['text'],
                'attorney': ['text']
            }
        },
        {
            'document_type': 'education_form',
            'description': 'Educational forms and academic documents',
            'field_patterns': {
                'student_id': ['student id', 'student number'],
                'gpa': ['gpa', 'grade point average'],
                'major': ['major', 'field of study', 'program']
            },
            'validation_rules': {
                'student_id': ['alphanumeric'],
                'gpa': ['numeric', 'range_0_4'],
                'major': ['text']
            }
        }
    ]
    
    for template_data in templates:
        success = processor.create_document_template(
            document_type=template_data['document_type'],
            description=template_data['description'],
            field_patterns=template_data['field_patterns'],
            validation_rules=template_data['validation_rules']
        )
        if success:
            logger.info(f"Created template for {template_data['document_type']}")
        else:
            logger.error(f"Failed to create template for {template_data['document_type']}")

def test_system(processor: UniversalDocumentProcessor):
    """
    Test the trained system with sample documents
    """
    logger.info("Testing the universal document processing system...")
    
    # Test document type classification
    test_texts = [
        "Please enter your full name and email address. This is an application form for membership.",
        "Patient ID: 12345. Insurance Provider: Blue Cross. Current Medications: Aspirin.",
        "Case Number: CV-2023-001. Court: Superior Court of California. Attorney: John Smith.",
        "Annual Income: $75,000. Bank Account: 123456789. Credit Score: 750."
    ]
    
    for text in test_texts:
        doc_type, confidence = processor.classify_document_type(text)
        logger.info(f"Text: '{text[:50]}...' -> Document Type: {doc_type} (confidence: {confidence:.2f})")
    
    # Test field type classification
    test_fields = [
        "Please enter your name:",
        "Email Address:",
        "Date of Birth:",
        "Social Security Number:",
        "Annual Income:",
        "Patient ID:",
        "Case Number:",
        "Student ID:"
    ]
    
    for field_text in test_fields:
        field_type = processor._classify_field_type_from_text(field_text)
        logger.info(f"Field: '{field_text}' -> Type: {field_type}")

def main():
    """
    Main training function
    """
    logger.info("Starting Universal Document Processing System Training")
    
    # Initialize processor
    processor = UniversalDocumentProcessor()
    
    # Get initial stats
    stats = processor.get_system_stats()
    logger.info(f"Initial system stats: {stats}")
    
    # Create document templates
    logger.info("Creating document templates...")
    create_document_templates(processor)
    
    # Prepare training data
    logger.info("Preparing training data...")
    training_data = create_sample_training_data()
    logger.info(f"Created {len(training_data)} training samples")
    
    # Train the models
    logger.info("Training machine learning models...")
    results = processor.train_model(training_data)
    logger.info(f"Training results: {results}")
    
    # Get updated stats
    stats = processor.get_system_stats()
    logger.info(f"Updated system stats: {stats}")
    
    # Test the system
    test_system(processor)
    
    # Export training data
    logger.info("Exporting training data...")
    export_data = {
        'samples': training_data,
        'templates': [processor.document_templates[dt].__dict__ for dt in processor.document_templates],
        'field_patterns': processor.field_patterns,
        'document_type_patterns': processor.document_type_patterns
    }
    
    with open('training_data_export.json', 'w') as f:
        json.dump(export_data, f, indent=2)
    
    logger.info("Training completed successfully!")
    logger.info("Training data exported to 'training_data_export.json'")
    logger.info("Models saved to 'models/' directory")

if __name__ == "__main__":
    main()

