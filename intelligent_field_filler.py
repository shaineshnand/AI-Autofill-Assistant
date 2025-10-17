#!/usr/bin/env python
"""
Intelligent Field Filler for AI Autofill Assistant
Provides smart content generation and validation for different field types
"""
import re
import random
from typing import Dict, List, Optional, Any
from datetime import datetime, date
import json

class IntelligentFieldFiller:
    """Intelligent field filler with context-aware content generation"""
    
    def __init__(self):
        self.field_templates = self._initialize_field_templates()
        self.validation_patterns = self._initialize_validation_patterns()
    
    def _initialize_field_templates(self) -> Dict[str, List[str]]:
        """Initialize templates for different field types"""
        return {
            'name': [
                'John Smith', 'Sarah Johnson', 'Michael Brown', 'Emily Davis',
                'David Wilson', 'Lisa Anderson', 'Robert Taylor', 'Jennifer Martinez',
                'William Garcia', 'Ashley Rodriguez', 'James Lee', 'Jessica White',
                'Christopher Harris', 'Amanda Clark', 'Matthew Lewis', 'Stephanie Walker'
            ],
            'email': [
                'john.smith@email.com', 'sarah.johnson@gmail.com', 'michael.brown@yahoo.com',
                'emily.davis@outlook.com', 'david.wilson@hotmail.com', 'lisa.anderson@company.com',
                'robert.taylor@business.org', 'jennifer.martinez@corp.net'
            ],
            'phone': [
                '(555) 123-4567', '555-123-4567', '555.123.4567', '+1-555-123-4567',
                '(555) 987-6543', '555-987-6543', '555.987.6543', '+1-555-987-6543',
                '(212) 555-0123', '212-555-0123', '212.555.0123', '+1-212-555-0123'
            ],
            'address': [
                '123 Main Street, New York, NY 10001',
                '456 Oak Avenue, Los Angeles, CA 90210',
                '789 Pine Road, Chicago, IL 60601',
                '321 Elm Street, Houston, TX 77001',
                '654 Maple Drive, Phoenix, AZ 85001',
                '987 Cedar Lane, Philadelphia, PA 19101',
                '147 Birch Street, San Antonio, TX 78201',
                '258 Spruce Avenue, San Diego, CA 92101'
            ],
            'date': [
                '01/15/1990', '03/22/1985', '07/08/1992', '11/30/1988',
                '05/14/1991', '09/03/1987', '12/25/1989', '02/18/1993',
                '06/07/1986', '10/12/1994', '04/29/1984', '08/16/1995'
            ],
            'age': ['25', '30', '28', '35', '22', '40', '27', '33', '29', '31', '26', '38'],
            'signature': ['[Signature]', '[Signed]', '[Initials]', '[Name]'],
            'text': [
                'Sample text', 'Example content', 'Placeholder text', 'Default value',
                'Test data', 'Sample input', 'Example entry', 'Default content'
            ],
            'day': [
                '1st', '2nd', '3rd', '5th', '10th', '15th', '20th', '25th',
                '1', '2', '3', '5', '10', '15', '20', '25', '28'
            ],
            'month': [
                'January', 'February', 'March', 'April', 'May', 'June',
                'July', 'August', 'September', 'October', 'November', 'December'
            ],
            'year': [
                '2024', '2023', '2025', '2022', '2021'
            ],
            'student_id': [
                'STU2024001', 'ID123456', 'S20240789', 'STU-2024-1234',
                'A12345678', 'ID-2024-567', 'S123456'
            ],
            'institution': [
                'University of Technology', 'State University', 'Technical College',
                'Community College', 'Pacific University', 'National University',
                'Institute of Technology', 'College of Arts and Sciences'
            ]
        }
    
    def _initialize_validation_patterns(self) -> Dict[str, str]:
        """Initialize validation patterns for different field types"""
        return {
            'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            'phone': r'^[\+]?[1-9][\d]{0,15}$',
            'date': r'^\d{1,2}[/-]\d{1,2}[/-]\d{2,4}$',
            'age': r'^\d{1,3}$',
            'name': r'^[a-zA-Z\s\'-]+$',
            'address': r'^[a-zA-Z0-9\s\.,\-#]+$'
        }
    
    def generate_field_content(self, field: Dict, context: Dict = None) -> str:
        """Generate appropriate content for a field based on its type and context"""
        field_type = field.get('field_type', 'text').lower()
        field_context = field.get('context', '').lower()
        
        # Handle special field types that need selection rather than text
        if field_type == 'checkbox':
            return self._generate_checkbox_selection(field, context)
        elif field_type == 'radio':
            return self._generate_radio_selection(field, context)
        elif field_type == 'dropdown':
            return self._generate_dropdown_selection(field, context)
        
        # Use context to refine field type if needed
        refined_type = self._refine_field_type(field_type, field_context, field)
        
        # Generate content based on refined type
        # First check in templates
        if refined_type in self.field_templates:
            content = random.choice(self.field_templates[refined_type])
        # Then try custom generation (which now includes day, month, year, etc.)
        else:
            content = self._generate_custom_content(refined_type, field_context)
        
        # Apply any field-specific formatting
        content = self._apply_field_formatting(content, refined_type, field)
        
        return content
    
    def _generate_checkbox_selection(self, field: Dict, context: Dict = None) -> str:
        """Generate checkbox selection (checked/unchecked)"""
        field_context = field.get('context', '').lower()
        
        # For checkboxes, we return selection status rather than text
        if 'option' in field_context:
            # This is an option checkbox - randomly select some options
            if random.choice([True, False]):  # 50% chance to check
                return "checked"
            else:
                return "unchecked"
        else:
            # This might be a general checkbox - check it
            return "checked"
    
    def _generate_radio_selection(self, field: Dict, context: Dict = None) -> str:
        """Generate radio button selection"""
        field_context = field.get('context', '').lower()
        
        # For radio buttons, we return selection status
        if 'dropdown' in field_context or 'select' in field_context:
            # This is a dropdown/radio selection - return a selection
            return "selected"
        else:
            return "selected"
    
    def _generate_dropdown_selection(self, field: Dict, context: Dict = None) -> str:
        """Generate dropdown selection"""
        field_context = field.get('context', '').lower()
        
        # Common dropdown options based on context
        if 'combo' in field_context or 'dropdown' in field_context:
            options = ['First Choice', 'Second Choice', 'Third Choice', 'Other']
            return random.choice(options)
        elif 'select' in field_context:
            options = ['Option A', 'Option B', 'Option C', 'None']
            return random.choice(options)
        else:
            return "Selected"
    
    def _refine_field_type(self, field_type: str, context: str, field: Dict = None) -> str:
        """Refine field type based on context"""
        context_lower = context.lower()
        
        # Also check field name and placeholder for better type detection
        if field:
            field_name = field.get('name', '').lower()
            placeholder = field.get('placeholder', '').lower()
            context_lower += ' ' + field_name + ' ' + placeholder
        
        # Check for date-related fields
        if any(keyword in context_lower for keyword in ['day of', 'dated on the', '__day']):
            return 'day'
        elif any(keyword in context_lower for keyword in ['month', 'of ___', 'between']):
            return 'month'
        elif any(keyword in context_lower for keyword in ['year', '20__', '19__']):
            return 'year'
        
        # Check for identification fields
        elif any(keyword in context_lower for keyword in ['student id', 'identification number', 'id number', 'student number']):
            return 'student_id'
        elif any(keyword in context_lower for keyword in ['institution', 'university', 'college', 'school']):
            return 'institution'
        
        # Check for name variations
        elif any(keyword in context_lower for keyword in ['first name', 'given name']):
            return 'first_name'
        elif any(keyword in context_lower for keyword in ['last name', 'surname', 'family name']):
            return 'last_name'
        elif any(keyword in context_lower for keyword in ['full name', 'complete name']):
            return 'name'
        elif any(keyword in context_lower for keyword in ['email', 'e-mail', 'email address']):
            return 'email'
        elif any(keyword in context_lower for keyword in ['dob', 'date of birth', 'birth date', 'birthday']):
            return 'date'
        elif any(keyword in context_lower for keyword in ['phone', 'telephone', 'tel', 'mobile', 'cell']):
            return 'phone'
        elif any(keyword in context_lower for keyword in ['address', 'street', 'location', 'residence']):
            return 'address'
        elif any(keyword in context_lower for keyword in ['date', 'birth', 'dob', 'date of birth']):
            return 'date'
        elif any(keyword in context_lower for keyword in ['age', 'years old', 'years of age']):
            return 'age'
        elif any(keyword in context_lower for keyword in ['signature', 'sign', 'initial', 'sign here']):
            return 'signature'
        elif any(keyword in context_lower for keyword in ['company', 'organization', 'employer']):
            return 'company'
        elif any(keyword in context_lower for keyword in ['job title', 'position', 'occupation']):
            return 'job_title'
        elif any(keyword in context_lower for keyword in ['ssn', 'social security', 'social security number']):
            return 'ssn'
        elif any(keyword in context_lower for keyword in ['id', 'identification', 'id number']):
            return 'id_number'
        
        return field_type
    
    def _generate_custom_content(self, field_type: str, context: str) -> str:
        """Generate custom content for field types not in templates"""
        if field_type == 'first_name':
            first_names = ['John', 'Sarah', 'Michael', 'Emily', 'David', 'Lisa', 'Robert', 'Jennifer']
            return random.choice(first_names)
        elif field_type == 'last_name':
            last_names = ['Smith', 'Johnson', 'Brown', 'Davis', 'Wilson', 'Anderson', 'Taylor', 'Martinez']
            return random.choice(last_names)
        elif field_type == 'company':
            companies = ['Acme Corp', 'Tech Solutions Inc', 'Global Industries', 'Innovation Labs',
                        'Future Systems', 'Digital Dynamics', 'Smart Technologies', 'NextGen Corp']
            return random.choice(companies)
        elif field_type == 'job_title':
            titles = ['Software Engineer', 'Project Manager', 'Data Analyst', 'Marketing Specialist',
                     'Sales Representative', 'HR Coordinator', 'Financial Advisor', 'Operations Manager']
            return random.choice(titles)
        elif field_type == 'ssn':
            return f"{random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(1000, 9999)}"
        elif field_type == 'id_number':
            return f"ID{random.randint(100000, 999999)}"
        elif field_type == 'day':
            # Return day as number or ordinal
            days = ['1st', '2nd', '3rd', '5th', '10th', '15th', '20th', '25th', '28th']
            return random.choice(days)
        elif field_type == 'month':
            # Return month name
            months = ['January', 'February', 'March', 'April', 'May', 'June',
                     'July', 'August', 'September', 'October', 'November', 'December']
            return random.choice(months)
        elif field_type == 'year':
            # Return 2 or 4 digit year
            years = ['24', '23', '25', '22', '2024', '2023', '2025']
            return random.choice(years)
        elif field_type == 'student_id':
            # Return student ID
            ids = ['STU2024001', 'ID123456', 'S20240789', 'STU-2024-1234', 'A12345678']
            return random.choice(ids)
        elif field_type == 'institution':
            # Return institution name
            institutions = ['University of Technology', 'State University', 'Technical College',
                          'Community College', 'Pacific University', 'National University']
            return random.choice(institutions)
        else:
            return f"Sample {field_type.replace('_', ' ').title()}"
    
    def _apply_field_formatting(self, content: str, field_type: str, field: Dict) -> str:
        """Apply appropriate formatting to field content"""
        if field_type == 'phone':
            # Ensure consistent phone formatting
            digits = re.sub(r'\D', '', content)
            if len(digits) == 10:
                return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
            elif len(digits) == 11 and digits[0] == '1':
                return f"+1-({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
        
        elif field_type == 'date':
            # Ensure consistent date formatting
            if '/' in content or '-' in content:
                return content
            else:
                # Generate a random date
                month = random.randint(1, 12)
                day = random.randint(1, 28)
                year = random.randint(1980, 2000)
                return f"{month:02d}/{day:02d}/{year}"
        
        elif field_type == 'email':
            # Ensure valid email format
            if '@' not in content:
                name = content.lower().replace(' ', '.')
                domains = ['gmail.com', 'yahoo.com', 'outlook.com', 'email.com']
                return f"{name}@{random.choice(domains)}"
        
        elif field_type == 'age':
            # Ensure age is a reasonable number
            try:
                age = int(content)
                if age < 18 or age > 100:
                    return str(random.randint(18, 65))
            except ValueError:
                return str(random.randint(18, 65))
        
        return content
    
    def validate_field_content(self, content: str, field_type: str) -> bool:
        """Validate field content against expected format"""
        if not content:
            return False
        
        field_type = field_type.lower()
        
        if field_type in self.validation_patterns:
            pattern = self.validation_patterns[field_type]
            return bool(re.match(pattern, content.strip()))
        
        return True  # No validation pattern, assume valid
    
    def suggest_field_content(self, field: Dict, user_input: str = "", context: Dict = None) -> str:
        """Suggest content for a field based on user input and context"""
        field_type = field.get('field_type', 'text').lower()
        
        # If user provided input, try to extract relevant information
        if user_input:
            extracted_content = self._extract_content_from_input(user_input, field_type)
            if extracted_content:
                return extracted_content
        
        # Generate content based on field type and context
        return self.generate_field_content(field, context)
    
    def _extract_content_from_input(self, user_input: str, field_type: str) -> Optional[str]:
        """Extract relevant content from user input based on field type"""
        user_input_lower = user_input.lower()
        
        if field_type == 'name':
            # Look for name patterns
            name_patterns = [
                r'my name is (\w+(?:\s+\w+)*)',
                r'i am (\w+(?:\s+\w+)*)',
                r'call me (\w+(?:\s+\w+)*)',
                r'name:?\s*(\w+(?:\s+\w+)*)',
                r'(\w+(?:\s+\w+)*) is my name'
            ]
            for pattern in name_patterns:
                match = re.search(pattern, user_input, re.IGNORECASE)
                if match:
                    return match.group(1).strip()
        
        elif field_type == 'email':
            # Look for email patterns
            email_pattern = r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
            match = re.search(email_pattern, user_input)
            if match:
                return match.group(1)
        
        elif field_type == 'phone':
            # Look for phone patterns
            phone_patterns = [
                r'my phone is ([\d\s\-\(\)\+]+)',
                r'phone:?\s*([\d\s\-\(\)\+]+)',
                r'call me at ([\d\s\-\(\)\+]+)',
                r'number:?\s*([\d\s\-\(\)\+]+)'
            ]
            for pattern in phone_patterns:
                match = re.search(pattern, user_input, re.IGNORECASE)
                if match:
                    return match.group(1).strip()
        
        elif field_type == 'address':
            # Look for address patterns
            address_patterns = [
                r'my address is ([^.!?]+)',
                r'address:?\s*([^.!?]+)',
                r'located at ([^.!?]+)'
            ]
            for pattern in address_patterns:
                match = re.search(pattern, user_input, re.IGNORECASE)
                if match:
                    return match.group(1).strip()
        
        elif field_type == 'age':
            # Look for age patterns
            age_patterns = [
                r'i am (\d+) years old',
                r'age:?\s*(\d+)',
                r'i\'m (\d+)',
                r'(\d+) years old'
            ]
            for pattern in age_patterns:
                match = re.search(pattern, user_input, re.IGNORECASE)
                if match:
                    return match.group(1).strip()
        
        return None
    
    def fill_all_fields(self, fields: List[Dict], context: Dict = None) -> List[Dict]:
        """Fill all fields with appropriate content"""
        filled_fields = []
        
        for field in fields:
            if not field.get('user_content'):  # Only fill empty fields
                suggested_content = self.generate_field_content(field, context)
                
                filled_field = field.copy()
                filled_field['user_content'] = suggested_content
                filled_field['ai_suggestion'] = suggested_content
                filled_field['ai_enhanced'] = True
                
                filled_fields.append(filled_field)
            else:
                filled_fields.append(field)
        
        return filled_fields
    
    def get_field_suggestions(self, field: Dict, context: Dict = None) -> List[str]:
        """Get multiple suggestions for a field"""
        field_type = field.get('field_type', 'text').lower()
        suggestions = []
        
        if field_type in self.field_templates:
            # Get 3 random suggestions from templates
            template_options = self.field_templates[field_type]
            suggestions = random.sample(template_options, min(3, len(template_options)))
        else:
            # Generate custom suggestions
            for _ in range(3):
                suggestions.append(self.generate_field_content(field, context))
        
        return suggestions
