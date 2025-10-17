"""
HTML-Based PDF Processor
Converts PDF to HTML, fills with AI data, then converts back to PDF
This approach is much more reliable than direct PDF manipulation
"""

import os
import json
import fitz  # PyMuPDF
import pdfplumber
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import re


@dataclass
class Field:
    """Represents a form field"""
    id: str
    name: str
    field_type: str  # 'text', 'checkbox', 'select', 'date', etc.
    x: float
    y: float
    width: float
    height: float
    page: int
    placeholder: str = ""
    value: str = ""
    required: bool = False


@dataclass
class DocumentLayout:
    """Represents the layout of a document"""
    title: str
    pages: List[Dict]
    fields: List[Field]
    extracted_text: str
    document_type: str = "form"


class HTMLPDFProcessor:
    """Processes PDFs by converting to HTML, filling with AI, then converting back to PDF"""
    
    def __init__(self):
        self.supported_field_types = ['text', 'email', 'phone', 'date', 'number', 'checkbox', 'select']
        
    def process_pdf(self, input_pdf_path: str, output_pdf_path: str = None) -> Dict:
        """
        Main processing method:
        1. Extract PDF content and detect fields
        2. Convert to HTML template
        3. Fill with AI data
        4. Convert HTML to PDF
        """
        try:
            if not os.path.exists(input_pdf_path):
                raise FileNotFoundError(f"Input PDF not found: {input_pdf_path}")
            
            if output_pdf_path is None:
                base_name = os.path.splitext(os.path.basename(input_pdf_path))[0]
                output_pdf_path = f"{base_name}_html_filled.pdf"
            
            print("Step 1: Extracting PDF content and detecting fields...")
            layout = self.extract_pdf_layout(input_pdf_path)
            
            print("Step 2: Converting to HTML template...")
            html_content = self.create_html_template(layout)
            
            print("Step 3: Generating AI data...")
            ai_data = self.generate_ai_data(layout)
            
            print("Step 4: Filling HTML with AI data...")
            filled_html = self.fill_html_with_ai_data(html_content, ai_data)
            
            print("Step 5: Converting HTML to PDF...")
            self.html_to_pdf(filled_html, output_pdf_path)
            
            return {
                'success': True,
                'output_path': output_pdf_path,
                'fields_detected': len(layout.fields),
                'ai_data_generated': len(ai_data),
                'document_type': layout.document_type
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def extract_pdf_layout(self, pdf_path: str) -> DocumentLayout:
        """Extract text content and detect form fields from PDF"""
        
        # Extract text content
        extracted_text = ""
        pages_data = []
        all_fields = []
        
        # Method 1: Try PyMuPDF for AcroForm fields
        try:
            doc = fitz.open(pdf_path)
            for page_num in range(len(doc)):
                page = doc[page_num]
                page_text = page.get_text()
                extracted_text += page_text + "\n"
                
                # Extract AcroForm fields if they exist
                widgets = page.widgets()
                page_fields = []
                
                for widget in widgets:
                    if hasattr(widget, 'field_name') and widget.field_name:
                        field = Field(
                            id=f"field_{len(all_fields)}",
                            name=widget.field_name,
                            field_type=self._detect_field_type(widget),
                            x=widget.rect.x0,
                            y=widget.rect.y0,
                            width=widget.rect.width,
                            height=widget.rect.height,
                            page=page_num,
                            placeholder=widget.field_name.replace('_', ' ').title()
                        )
                        page_fields.append(field)
                        all_fields.append(field)
                
                pages_data.append({
                    'page_number': page_num,
                    'text': page_text,
                    'fields': page_fields
                })
            
            doc.close()
            
        except Exception as e:
            print(f"PyMuPDF extraction failed: {e}")
        
        # Method 2: Use pdfplumber for additional field detection
        if not all_fields:
            try:
                with pdfplumber.open(pdf_path) as pdf:
                    for page_num, page in enumerate(pdf.pages):
                        page_text = page.extract_text() or ""
                        extracted_text += page_text + "\n"
                        
                        # Detect visual blanks and form-like patterns
                        visual_fields = self._detect_visual_fields(page_text, page_num)
                        all_fields.extend(visual_fields)
                        
                        pages_data.append({
                            'page_number': page_num,
                            'text': page_text,
                            'fields': visual_fields
                        })
                        
            except Exception as e:
                print(f"PDFplumber extraction failed: {e}")
        
        # Determine document type
        document_type = self._analyze_document_type(extracted_text)
        
        return DocumentLayout(
            title=os.path.splitext(os.path.basename(pdf_path))[0],
            pages=pages_data,
            fields=all_fields,
            extracted_text=extracted_text,
            document_type=document_type
        )
    
    def _detect_field_type(self, widget) -> str:
        """Detect field type from PyMuPDF widget"""
        if hasattr(widget, 'field_type'):
            field_type = widget.field_type
            if field_type == 2:  # Text field
                return 'text'
            elif field_type == 4:  # Checkbox
                return 'checkbox'
            elif field_type == 5:  # Radio button
                return 'radio'
            elif field_type == 6:  # Dropdown
                return 'select'
        return 'text'
    
    def _detect_visual_fields(self, text: str, page_num: int) -> List[Field]:
        """Detect form fields from visual patterns in text"""
        fields = []
        
        # Pattern 1: Dotted lines (...)
        dotted_pattern = r'\.{3,}'
        for match in re.finditer(dotted_pattern, text):
            field = Field(
                id=f"dotted_{len(fields)}",
                name=f"field_{len(fields)}",
                field_type='text',
                x=0,  # Will be positioned in HTML
                y=0,
                width=100,
                height=20,
                page=page_num,
                placeholder="Enter value"
            )
            fields.append(field)
        
        # Pattern 2: Underscore lines (___)
        underscore_pattern = r'_{3,}'
        for match in re.finditer(underscore_pattern, text):
            field = Field(
                id=f"underscore_{len(fields)}",
                name=f"field_{len(fields)}",
                field_type='text',
                x=0,
                y=0,
                width=100,
                height=20,
                page=page_num,
                placeholder="Enter value"
            )
            fields.append(field)
        
        # Pattern 3: Dash lines (---)
        dash_pattern = r'-{3,}'
        for match in re.finditer(dash_pattern, text):
            field = Field(
                id=f"dash_{len(fields)}",
                name=f"field_{len(fields)}",
                field_type='text',
                x=0,
                y=0,
                width=100,
                height=20,
                page=page_num,
                placeholder="Enter value"
            )
            fields.append(field)
        
        return fields
    
    def _analyze_document_type(self, text: str) -> str:
        """Analyze text to determine document type"""
        text_lower = text.lower()
        
        # Check for common form keywords
        form_keywords = ['name', 'address', 'phone', 'email', 'date', 'signature']
        form_score = sum(1 for keyword in form_keywords if keyword in text_lower)
        
        # Check for contract keywords
        contract_keywords = ['agreement', 'contract', 'terms', 'conditions', 'party']
        contract_score = sum(1 for keyword in contract_keywords if keyword in text_lower)
        
        if contract_score > form_score:
            return 'contract'
        elif form_score > 3:
            return 'form'
        else:
            return 'document'
    
    def create_html_template(self, layout: DocumentLayout) -> str:
        """Create HTML template that replicates the original PDF layout exactly"""
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{layout.title}</title>
    <style>
        body {{
            font-family: 'Times New Roman', serif;
            line-height: 1.4;
            margin: 0;
            padding: 20px;
            background-color: white;
            color: black;
            font-size: 11pt;
        }}
        
        .document-container {{
            max-width: 210mm; /* A4 width */
            min-height: 297mm; /* A4 height */
            margin: 0 auto;
            background: white;
            padding: 25mm;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
            position: relative;
        }}
        
        .page {{
            margin-bottom: 40px;
            position: relative;
            font-size: 11pt;
            line-height: 1.4;
        }}
        
        .text-content {{
            white-space: pre-line;
            font-size: 11pt;
            line-height: 1.4;
            margin-bottom: 15px;
        }}
        
        .input-line {{
            display: inline-block;
            border-bottom: 1px solid #000;
            background: transparent;
            font-family: inherit;
            font-size: 11pt;
            padding: 0 3px;
            margin: 0 2px;
            min-width: 120px;
            height: 18px;
            line-height: 18px;
            vertical-align: baseline;
            position: relative;
        }}
        
        /* PDF-specific styling for better rendering */
        @media print {{
            .input-line {{
                border-bottom: 1px solid #000 !important;
                background: transparent !important;
                padding: 0 3px !important;
                margin: 0 2px !important;
                height: 18px !important;
                line-height: 18px !important;
                display: inline-block !important;
                position: relative !important;
                vertical-align: baseline !important;
            }}
        }}
        
        /* Alternative approach for PDF - use absolute positioning */
        .pdf-input-line {{
            position: relative;
            display: inline-block;
            min-width: 120px;
            height: 18px;
            border-bottom: 1px solid #000;
            background: transparent;
            font-family: inherit;
            font-size: 11pt;
            line-height: 18px;
            padding: 0 3px;
            margin: 0 2px;
        }}
        
        .pdf-input-line::after {{
            content: attr(data-value);
            position: absolute;
            top: 0;
            left: 3px;
            right: 3px;
            height: 18px;
            line-height: 18px;
            font-family: inherit;
            font-size: 11pt;
            background: transparent;
            border: none;
            outline: none;
        }}
        
        .editable-field {{
            display: inline-block;
            border: none;
            border-bottom: 1px solid #000;
            background: transparent;
            font-family: inherit;
            font-size: 11pt;
            padding: 0 3px;
            margin: 0 2px;
            min-width: 120px;
            height: 18px;
            line-height: 18px;
            outline: none;
            transition: all 0.2s ease;
        }}
        
        .editable-field:hover {{
            border-bottom: 2px solid #007bff;
            background-color: rgba(0, 123, 255, 0.05);
        }}
        
        .editable-field:focus {{
            border-bottom: 2px solid #007bff;
            background-color: rgba(0, 123, 255, 0.1);
            box-shadow: 0 2px 4px rgba(0, 123, 255, 0.2);
        }}
        
        .form-field {{
            display: inline-block;
            border: none;
            border-bottom: 1px solid #000;
            background: transparent;
            font-family: inherit;
            font-size: 11pt;
            padding: 1px 3px;
            margin: 0 2px;
            min-width: 80px;
            outline: none;
            position: relative;
        }}
        
        .form-field:focus {{
            border-bottom: 2px solid #007bff;
            background-color: rgba(0, 123, 255, 0.1);
        }}
        
        .field-label {{
            font-weight: normal;
            display: inline;
        }}
        
        .field-line {{
            border-bottom: 1px solid #000;
            display: inline-block;
            min-width: 150px;
            height: 18px;
            position: relative;
            margin: 0 5px;
        }}
        
        .field-line input {{
            border: none;
            background: transparent;
            width: 100%;
            height: 100%;
            font-family: inherit;
            font-size: 11pt;
            padding: 0 3px;
            outline: none;
        }}
        
        .signature-line {{
            border-bottom: 1px solid #000;
            display: inline-block;
            min-width: 200px;
            height: 20px;
            margin: 10px 0;
        }}
        
        .signature-line input {{
            border: none;
            background: transparent;
            width: 100%;
            height: 100%;
            font-family: inherit;
            font-size: 11pt;
            padding: 0 3px;
            outline: none;
        }}
        
        .checkbox-field {{
            display: inline-block;
            margin: 0 5px;
        }}
        
        .checkbox-field input[type="checkbox"] {{
            margin-right: 5px;
            transform: scale(1.1);
        }}
        
        .section {{
            margin: 15px 0;
        }}
        
        .section-title {{
            font-weight: bold;
            font-size: 12pt;
            margin-bottom: 8px;
        }}
        
        .form-row {{
            margin: 6px 0;
            display: flex;
            align-items: center;
            flex-wrap: wrap;
        }}
        
        /* PDF-specific form row styling */
        @media print {{
            .form-row {{
                margin: 6px 0 !important;
                display: flex !important;
                align-items: center !important;
                flex-wrap: wrap !important;
            }}
        }}
        
        .form-row label {{
            margin-right: 8px;
            min-width: 80px;
            font-size: 11pt;
        }}
        
        .dotted-line {{
            border-bottom: 1px dotted #000;
            display: inline-block;
            min-width: 100px;
            height: 15px;
            margin: 0 5px;
        }}
        
        .dotted-line input {{
            border: none;
            background: transparent;
            width: 100%;
            height: 100%;
            font-family: inherit;
            font-size: 11pt;
            padding: 0 3px;
            outline: none;
        }}
        
        @media print {{
            body {{ 
                margin: 0; 
                padding: 0;
            }}
            .document-container {{ 
                box-shadow: none; 
                padding: 20mm;
                margin: 0;
                max-width: none;
                min-height: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="document-container">
        <h1 class="form-title" style="text-align: center; margin-bottom: 30px; font-size: 14pt; text-decoration: underline;">{layout.title.replace('_', ' ').title()}</h1>
"""
        
        # Process each page
        for page in layout.pages:
            html_content += f'        <div class="page">\n'
            
            # Convert page text to HTML with form fields
            page_html = self._convert_text_to_html_with_fields(
                page['text'], 
                page['fields']
            )
            
            html_content += f'            <div class="text-content">{page_html}</div>\n'
            html_content += '        </div>\n'
        
        html_content += """
    </div>
</body>
</html>
"""
        
        return html_content
    
    def _convert_text_to_html_with_fields(self, text: str, fields: List[Field]) -> str:
        """Convert plain text to HTML with embedded form fields that look exactly like the original PDF"""
        
        # Preserve the exact text layout from the PDF
        html_content = ""
        processed_field_ids = set()  # Track which fields we've already processed
        
        # Process the text and embed fields naturally within the existing text structure
        lines = text.split('\n')
        
        for line in lines:
            if not line.strip():
                html_content += '<br>\n'
                continue
            
            # Check if this line contains field indicators and embed fields naturally
            field_added = False
            for field in fields:
                if field.id in processed_field_ids:
                    continue
                    
                # Look for field indicators in the line and embed the field naturally
                if self._should_embed_field_in_line(line, field):
                    # Embed the field naturally within the line
                    embedded_line = self._embed_field_in_line(line, field)
                    html_content += f'<div class="text-content">{embedded_line}</div>\n'
                    processed_field_ids.add(field.id)
                    field_added = True
                    break
            
            if not field_added:
                # Regular text line - preserve exactly as it appears in the PDF
                html_content += f'<div class="text-content">{line}</div>\n'
        
        # Add any remaining fields that weren't caught by the text processing
        for field in fields:
            if field.id not in processed_field_ids:
                if field.field_type == 'checkbox':
                    html_content += f'''
                    <div class="form-row">
                        <label>{field.placeholder}:</label>
                        <input type="checkbox" class="checkbox-field" id="{field.id}" name="{field.name}">
                    </div>\n'''
                else:
                    html_content += f'''
                    <div class="form-row">
                        <label>{field.placeholder}:</label>
                        <div class="field-line">
                            <input type="{field.field_type}" class="form-field" id="{field.id}" name="{field.name}" placeholder="{field.placeholder}">
                        </div>
                    </div>\n'''
                processed_field_ids.add(field.id)
        
        return html_content
    
    def _should_embed_field_in_line(self, line: str, field: Field) -> bool:
        """Check if a field should be embedded in a specific line"""
        line_lower = line.lower()
        field_name_lower = field.name.lower()
        field_placeholder_lower = field.placeholder.lower()
        
        # Check for common field patterns in the contract
        if 'full name' in line_lower and ('name' in field_name_lower or 'name' in field_placeholder_lower):
            return True
        elif 'given name' in line_lower and ('name' in field_name_lower or 'name' in field_placeholder_lower):
            return True
        elif 'family name' in line_lower and ('name' in field_name_lower or 'name' in field_placeholder_lower):
            return True
        elif 'address' in line_lower and 'address' in field_name_lower:
            return True
        elif 'house nr' in line_lower and 'house' in field_name_lower:
            return True
        elif 'postcode' in line_lower and 'postcode' in field_name_lower:
            return True
        elif 'city' in line_lower and 'city' in field_name_lower:
            return True
        elif 'country' in line_lower and 'country' in field_name_lower:
            return True
        elif 'gender' in line_lower and 'gender' in field_name_lower:
            return True
        elif 'height' in line_lower and 'height' in field_name_lower:
            return True
        elif 'driving license' in line_lower and 'driving' in field_name_lower:
            return True
        elif 'language' in line_lower and 'language' in field_name_lower:
            return True
        elif 'favourite colour' in line_lower and 'colour' in field_name_lower:
            return True
        elif 'dob' in line_lower and 'dob' in field_name_lower:
            return True
        elif 'date of birth' in line_lower and 'dob' in field_name_lower:
            return True
        elif 'signature' in line_lower and 'signature' in field_name_lower:
            return True
        # Contract-specific patterns
        elif 'employer' in line_lower and 'employer' in field_name_lower:
            return True
        elif 'employee' in line_lower and 'employee' in field_name_lower:
            return True
        elif 'salary' in line_lower and 'salary' in field_name_lower:
            return True
        elif 'capacity' in line_lower and 'capacity' in field_name_lower:
            return True
        elif 'day' in line_lower and 'month' in line_lower and 'year' in line_lower:
            return True
        elif 'id no' in line_lower and 'id' in field_name_lower:
            return True
        elif 'contact no' in line_lower and 'contact' in field_name_lower:
            return True
        elif 'name:' in line_lower and 'name' in field_name_lower:
            return True
        elif 'at' in line_lower and 'at' in field_name_lower:
            return True
        elif 'responsible to' in line_lower and 'responsible' in field_name_lower:
            return True
        elif 'job responsibilities' in line_lower and 'job' in field_name_lower:
            return True
        
        return False
    
    def _embed_field_in_line(self, line: str, field: Field) -> str:
        """Embed a field naturally within a line of text"""
        # Find the position where the field should be embedded
        # Look for common patterns like "Full Name:" followed by space or line
        
        if ':' in line:
            # Split at the colon and add the field after it
            parts = line.split(':', 1)
            if len(parts) == 2:
                label = parts[0] + ':'
                rest = parts[1].strip()
                
                # If there's text after the colon, replace it with the field
                if rest:
                    return f'{label} <span class="input-line" id="{field.id}" data-field-name="{field.name}"></span>'
                else:
                    return f'{label} <span class="input-line" id="{field.id}" data-field-name="{field.name}"></span>'
        
        # Handle specific contract patterns
        if 'employer' in line.lower() and 'hereinafter' in line.lower():
            # Replace the long line with a field
            return line.replace('………………………………………………………', f'<span class="input-line" id="{field.id}" data-field-name="{field.name}"></span>')
        elif 'employee' in line.lower() and 'hereinafter' in line.lower():
            # Replace the long line with a field
            return line.replace('………………………………………………………', f'<span class="input-line" id="{field.id}" data-field-name="{field.name}"></span>')
        elif 'salary' in line.lower() and 'nu.' in line.lower():
            # Replace the salary blank with a field
            return line.replace('_______', f'<span class="input-line" id="{field.id}" data-field-name="{field.name}"></span>')
        elif 'capacity' in line.lower() and '__________' in line:
            # Replace the capacity blank with a field
            return line.replace('__________', f'<span class="input-line" id="{field.id}" data-field-name="{field.name}"></span>')
        elif 'day' in line.lower() and 'month' in line.lower() and 'year' in line.lower():
            # Replace the date blanks with fields
            line = line.replace('…..day……', f'<span class="input-line" id="{field.id}" data-field-name="{field.name}"></span>')
            return line
        elif 'id no' in line.lower() and '………………' in line:
            # Replace the ID blank with a field
            return line.replace('………………', f'<span class="input-line" id="{field.id}" data-field-name="{field.name}"></span>')
        elif 'contact no' in line.lower() and '………………' in line:
            # Replace the contact blank with a field
            return line.replace('………………', f'<span class="input-line" id="{field.id}" data-field-name="{field.name}"></span>')
        elif 'name:' in line.lower() and '………………' in line:
            # Replace the name blank with a field
            return line.replace('………………', f'<span class="input-line" id="{field.id}" data-field-name="{field.name}"></span>')
        elif 'at' in line.lower() and '………………………' in line:
            # Replace the location blank with a field
            return line.replace('………………………', f'<span class="input-line" id="{field.id}" data-field-name="{field.name}"></span>')
        elif 'responsible to' in line.lower() and '…………………………' in line:
            # Replace the responsibility blank with a field
            return line.replace('…………………………', f'<span class="input-line" id="{field.id}" data-field-name="{field.name}"></span>')
        elif 'job responsibilities' in line.lower() and '________________' in line:
            # Replace the job responsibilities blank with a field
            return line.replace('________________', f'<span class="input-line" id="{field.id}" data-field-name="{field.name}"></span>')
        
        # If no specific pattern, just add the field at the end
        return f'{line} <span class="input-line" id="{field.id}" data-field-name="{field.name}"></span>'
    
    def generate_ai_data(self, layout: DocumentLayout) -> Dict[str, str]:
        """Generate AI data for form fields"""
        
        # Import the intelligent field filler
        try:
            from chat.views import IntelligentFieldFiller
            intelligent_filler = IntelligentFieldFiller()
        except ImportError:
            print("IntelligentFieldFiller not available, using basic data generation")
            return self._generate_basic_ai_data(layout)
        
        ai_data = {}
        doc_context = {
            'document_type': layout.document_type,
            'total_blanks': len(layout.fields),
            'field_types': [field.field_type for field in layout.fields],
            'extracted_text': layout.extracted_text
        }
        
        for field in layout.fields:
            try:
                # Convert field to the format expected by IntelligentFieldFiller
                field_data = {
                    'id': field.id,
                    'name': field.name,
                    'field_type': field.field_type,
                    'placeholder': field.placeholder
                }
                
                suggested_content = intelligent_filler.generate_field_content(field_data, doc_context)
                ai_data[field.id] = suggested_content
                print(f"Generated AI data for {field.id}: {suggested_content[:50]}...")
                
            except Exception as e:
                print(f"Failed to generate AI data for {field.id}: {e}")
                ai_data[field.id] = self._get_default_value(field.field_type)
        
        return ai_data
    
    def _generate_basic_ai_data(self, layout: DocumentLayout) -> Dict[str, str]:
        """Generate basic AI data when IntelligentFieldFiller is not available"""
        ai_data = {}
        
        for field in layout.fields:
            ai_data[field.id] = self._get_default_value(field.field_type)
        
        return ai_data
    
    def _get_default_value(self, field_type: str) -> str:
        """Get default value based on field type"""
        defaults = {
            'text': 'Sample Text',
            'email': 'user@example.com',
            'phone': '(555) 123-4567',
            'date': '2024-01-01',
            'number': '123',
            'checkbox': 'checked',
            'select': 'Option 1'
        }
        return defaults.get(field_type, 'Sample Value')
    
    def fill_html_with_ai_data(self, html_content: str, ai_data: Dict[str, str]) -> str:
        """Fill HTML form fields with AI-generated data and make them editable"""
        
        filled_html = html_content
        
        for field_id, value in ai_data.items():
            if field_id in filled_html:
                import re
                
                # First, handle existing editable input fields - update their values
                # Find the input field with the specific field_id and replace all value attributes
                editable_input_pattern = rf'<input([^>]*class="editable-field"[^>]*id="{re.escape(field_id)}"[^>]*)>'
                
                def replace_editable_input(match):
                    attributes = match.group(1)
                    # Remove all existing value attributes
                    attributes = re.sub(r'\s+value="[^"]*"', '', attributes)
                    # Add the new value attribute
                    return f'<input{attributes} value="{value}">'
                
                filled_html = re.sub(editable_input_pattern, replace_editable_input, filled_html)
                
                # Then, handle input-line spans with the specific field_id
                pattern = rf'(<span[^>]*class="input-line"[^>]*id="{re.escape(field_id)}"[^>]*data-field-name="([^"]*)"[^>]*>)([^<]*)(</span>)'
                
                def replace_span(match):
                    field_name = match.group(2)
                    # Convert to editable input field
                    return f'<input type="text" class="editable-field" id="{field_id}" name="{field_name}" value="{value}" style="display: inline-block; border: none; border-bottom: 1px solid #000; background: transparent; font-family: inherit; font-size: 11pt; padding: 0 3px; margin: 0 2px; min-width: 120px; height: 18px; line-height: 18px; outline: none;">'
                
                filled_html = re.sub(pattern, replace_span, filled_html)
                
                # Also handle regular input fields for backward compatibility
                input_pattern = rf'(<input[^>]*id="{re.escape(field_id)}"[^>]*?)(?:\s+value="[^"]*")?([^>]*>)'
                
                def replace_input(match):
                    before_value = match.group(1)
                    after_value = match.group(2)
                    return f'{before_value} value="{value}"{after_value}'
                
                filled_html = re.sub(input_pattern, replace_input, filled_html)
        
        # Add JavaScript to communicate field values to parent window
        js_script = """
        <script>
        // Function to get current field values and send to parent
        function getFieldValues() {
            const fieldValues = {};
            const editableFields = document.querySelectorAll('.editable-field');
            editableFields.forEach(field => {
                if (field.id && field.value) {
                    fieldValues[field.id] = field.value;
                }
            });
            return fieldValues;
        }
        
        // Listen for messages from parent window
        window.addEventListener('message', function(event) {
            if (event.data.type === 'GET_FIELD_VALUES') {
                const fieldValues = getFieldValues();
                event.source.postMessage({
                    type: 'FIELD_VALUES',
                    values: fieldValues
                }, event.origin);
            }
        });
        
        // Also expose function globally for direct access
        window.getFieldValues = getFieldValues;
        </script>
        """
        
        # Insert the script before closing body tag
        if '</body>' in filled_html:
            filled_html = filled_html.replace('</body>', js_script + '</body>')
        else:
            filled_html += js_script
        
        return filled_html
    
    def html_to_pdf(self, html_content: str, output_path: str):
        """Convert HTML to PDF using pdfkit (with wkhtmltopdf)"""
        try:
            # Create output directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Create a PDF-optimized version of the HTML
            pdf_optimized_html = self._optimize_html_for_pdf(html_content)
            
            # Try pdfkit first (now that wkhtmltopdf is installed)
            self._html_to_pdf_with_pdfkit(pdf_optimized_html, output_path)
            print(f"Successfully converted HTML to PDF: {output_path}")
            
        except Exception as e:
            print(f"PDF conversion failed: {e}")
            # Fallback to simple PDF creation
            self._html_to_pdf_simple(html_content, output_path)
    
    def _optimize_html_for_pdf(self, html_content: str) -> str:
        """Optimize HTML for better PDF rendering"""
        import re
        
        # Replace editable input fields with PDF-friendly structure
        def replace_editable_field(match):
            field_id = match.group(1) if match.group(1) else ""
            field_name = match.group(2) if match.group(2) else ""
            value = match.group(3) if match.group(3) else ""
            
            # Create a more robust structure for PDF
            return f'''<span class="pdf-field-container" style="display: inline-block; position: relative; min-width: 120px; height: 18px; border-bottom: 1px solid #000; margin: 0 2px;">
                <span class="pdf-field-text" style="position: absolute; top: 0; left: 3px; right: 3px; height: 18px; line-height: 18px; font-family: inherit; font-size: 11pt; background: transparent;">{value}</span>
            </span>'''
        
        # Pattern to match editable input fields
        editable_pattern = r'<input[^>]*class="editable-field"[^>]*id="([^"]*)"[^>]*name="([^"]*)"[^>]*value="([^"]*)"[^>]*>'
        optimized_html = re.sub(editable_pattern, replace_editable_field, html_content)
        
        # Also handle input-line spans for backward compatibility
        def replace_input_line(match):
            field_id = match.group(1) if match.group(1) else ""
            field_name = match.group(2) if match.group(2) else ""
            content = match.group(3) if match.group(3) else ""
            
            # Create a more robust structure for PDF
            return f'''<span class="pdf-field-container" style="display: inline-block; position: relative; min-width: 120px; height: 18px; border-bottom: 1px solid #000; margin: 0 2px;">
                <span class="pdf-field-text" style="position: absolute; top: 0; left: 3px; right: 3px; height: 18px; line-height: 18px; font-family: inherit; font-size: 11pt; background: transparent;">{content}</span>
            </span>'''
        
        # Pattern to match input-line spans with content
        pattern = r'<span[^>]*class="input-line"[^>]*id="([^"]*)"[^>]*data-field-name="([^"]*)"[^>]*>([^<]*)</span>'
        optimized_html = re.sub(pattern, replace_input_line, optimized_html)
        
        return optimized_html
    
    def _add_inline_css(self, html_content: str) -> str:
        """Add inline CSS for better PDF formatting"""
        css_style = """
        <style>
        @page {
            size: A4;
            margin: 1in;
        }
        body {
            font-family: Arial, sans-serif;
            line-height: 1.4;
            color: #333;
            margin: 0;
            padding: 20px;
        }
        </style>
        """
        
        # Insert CSS before </head> or at the beginning if no head tag
        if '</head>' in html_content:
            return html_content.replace('</head>', css_style + '</head>')
        elif '<body>' in html_content:
            return html_content.replace('<body>', '<head>' + css_style + '</head><body>')
        else:
            return css_style + html_content
    
    def _html_to_pdf_with_weasyprint(self, html_content: str, output_path: str):
        """Fallback method using WeasyPrint"""
        try:
            from weasyprint import HTML
            
            # Create output directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Convert HTML to PDF
            HTML(string=html_content).write_pdf(output_path)
            print(f"Successfully converted HTML to PDF with WeasyPrint: {output_path}")
            
        except Exception as e:
            print(f"WeasyPrint conversion also failed: {e}")
            raise
    
    def _html_to_pdf_with_pdfkit(self, html_content: str, output_path: str):
        """Fallback method using pdfkit"""
        try:
            import pdfkit
            
            # Configure pdfkit to use the installed wkhtmltopdf
            config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
            
            options = {
                'page-size': 'A4',
                'margin-top': '0.75in',
                'margin-right': '0.75in',
                'margin-bottom': '0.75in',
                'margin-left': '0.75in',
                'encoding': "UTF-8",
                'no-outline': None,
                'enable-local-file-access': None,
                'print-media-type': None,
                'disable-smart-shrinking': None,
                'dpi': 300,
                'image-quality': 100,
                'disable-external-links': None,
                'disable-forms': None,
                'disable-javascript': None,
                'load-error-handling': 'ignore',
                'load-media-error-handling': 'ignore'
            }
            
            pdfkit.from_string(html_content, output_path, options=options, configuration=config)
            print(f"Successfully converted HTML to PDF with pdfkit: {output_path}")
            
        except Exception as e:
            print(f"PDFkit conversion also failed: {e}")
            raise


def test_html_processor():
    """Test the HTML PDF processor"""
    processor = HTMLPDFProcessor()
    
    # Test with an existing PDF
    test_pdf = "test_form.pdf"
    if os.path.exists(test_pdf):
        result = processor.process_pdf(test_pdf)
        print(f"Processing result: {result}")
    else:
        print(f"Test PDF not found: {test_pdf}")


if __name__ == "__main__":
    test_html_processor()
