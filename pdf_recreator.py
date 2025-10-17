"""
PDF Recreator - Extract text and create new editable PDFs with AI auto-filling
This module recreates PDFs exactly like the original but makes them editable with AI-filled data.
"""

import fitz  # PyMuPDF
import pdfplumber
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import black, blue, red
import os
import json
import re
from typing import List, Dict, Tuple, Optional
from datetime import datetime
import logging

# Import AI integration
try:
    from ollama_integration import AIDocumentProcessor
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    print("AI integration not available")

class PDFRecreator:
    """
    Recreates PDFs by extracting text and creating new editable versions with AI auto-filling.
    """
    
    def __init__(self):
        self.ai_processor = AIDocumentProcessor() if AI_AVAILABLE else None
        self.setup_fonts()
        
    def setup_fonts(self):
        """Setup fonts for PDF generation"""
        try:
            # Try to register system fonts
            font_paths = [
                'C:/Windows/Fonts/arial.ttf',
                'C:/Windows/Fonts/times.ttf',
                'C:/Windows/Fonts/calibri.ttf'
            ]
            
            for font_path in font_paths:
                if os.path.exists(font_path):
                    font_name = os.path.splitext(os.path.basename(font_path))[0]
                    try:
                        pdfmetrics.registerFont(TTFont(font_name, font_path))
                    except:
                        pass
        except:
            pass  # Use default fonts if custom fonts fail
    
    def extract_text_with_layout(self, pdf_path: str) -> Dict:
        """
        Extract text with layout information from PDF using both PyMuPDF and pdfplumber
        """
        extracted_data = {
            'pages': [],
            'metadata': {},
            'text_content': '',
            'fields_detected': []
        }
        
        try:
            # Extract with PyMuPDF for layout and positioning
            doc = fitz.open(pdf_path)
            extracted_data['metadata'] = doc.metadata
            
            # Extract with pdfplumber for better text extraction
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, (fitz_page, plumber_page) in enumerate(zip(doc, pdf.pages)):
                    page_data = {
                        'page_number': page_num,
                        'text': '',
                        'words': [],
                        'lines': [],
                        'rects': [],
                        'fields': []
                    }
                    
                    # Extract text from pdfplumber (better for complex layouts)
                    page_data['text'] = plumber_page.extract_text() or ''
                    
                    # Extract words with positions
                    words = plumber_page.extract_words()
                    page_data['words'] = words
                    
                    # Extract lines
                    lines = plumber_page.lines
                    page_data['lines'] = lines
                    
                    # Extract rectangles (potential form fields)
                    rects = plumber_page.rects
                    page_data['rects'] = rects
                    
                    # Detect potential form fields from PyMuPDF
                    fitz_annotations = fitz_page.annots()
                    for annot in fitz_annotations:
                        if annot.type[0] == 1:  # Text widget
                            rect = annot.rect
                            field_data = {
                                'type': 'text_field',
                                'rect': [rect.x0, rect.y0, rect.x1, rect.y1],
                                'name': annot.field_name,
                                'value': annot.field_value,
                                'page': page_num
                            }
                            page_data['fields'].append(field_data)
                    
                    # Detect visual form fields (dotted lines, blanks, etc.)
                    visual_fields = self._detect_visual_fields(plumber_page, page_num)
                    page_data['fields'].extend(visual_fields)
                    
                    extracted_data['pages'].append(page_data)
                    extracted_data['text_content'] += page_data['text'] + '\n'
            
            doc.close()
            
        except Exception as e:
            logging.error(f"Error extracting text from PDF: {str(e)}")
            raise Exception(f"Failed to extract text from PDF: {str(e)}")
        
        return extracted_data
    
    def _detect_visual_fields(self, page, page_num: int) -> List[Dict]:
        """Detect visual form fields like dotted lines, blanks, colons, etc."""
        fields = []
        
        try:
            # Look for dotted lines or underscores
            text = page.extract_text() or ''
            
            # Pattern 1: Fields ending with colon (like "Full Name:", "Date of Birth:")
            colon_pattern = r'([A-Za-z\s]+):\s*$'
            for match in re.finditer(colon_pattern, text, re.MULTILINE):
                field_label = match.group(1).strip()
                field_data = {
                    'type': 'colon_field',
                    'name': field_label.lower().replace(' ', '_'),
                    'text': match.group(),
                    'label': field_label,
                    'position': match.start(),
                    'page': page_num,
                    'suggested_type': 'text'
                }
                fields.append(field_data)
            
            # Pattern 2: Dotted lines (...)
            dotted_pattern = r'\.{3,}'
            for match in re.finditer(dotted_pattern, text):
                start_pos = match.start()
                field_data = {
                    'type': 'dotted_line',
                    'name': f'dotted_field_{len(fields)}',
                    'text': match.group(),
                    'position': start_pos,
                    'page': page_num,
                    'suggested_type': 'text'
                }
                fields.append(field_data)
            
            # Pattern 3: Underscores (___)
            underscore_pattern = r'_{3,}'
            for match in re.finditer(underscore_pattern, text):
                start_pos = match.start()
                field_data = {
                    'type': 'underscore',
                    'name': f'underscore_field_{len(fields)}',
                    'text': match.group(),
                    'position': start_pos,
                    'page': page_num,
                    'suggested_type': 'text'
                }
                fields.append(field_data)
            
            # Pattern 4: Dashes (---)
            dash_pattern = r'-{3,}'
            for match in re.finditer(dash_pattern, text):
                start_pos = match.start()
                field_data = {
                    'type': 'dash',
                    'name': f'dash_field_{len(fields)}',
                    'text': match.group(),
                    'position': start_pos,
                    'page': page_num,
                    'suggested_type': 'text'
                }
                fields.append(field_data)
            
            # Pattern 5: Blank spaces between text
            # Look for large gaps in text
            words = page.extract_words()
            for i, word in enumerate(words):
                if i < len(words) - 1:
                    next_word = words[i + 1]
                    # If there's a large gap, it might be a field
                    gap = next_word['x0'] - word['x1']
                    if gap > 50:  # Significant gap
                        field_data = {
                            'type': 'blank_space',
                            'name': f'blank_field_{len(fields)}',
                            'x0': word['x1'],
                            'y0': word['top'],
                            'x1': next_word['x0'],
                            'y1': word['bottom'],
                            'page': page_num,
                            'suggested_type': 'text'
                        }
                        fields.append(field_data)
        
        except Exception as e:
            logging.error(f"Error detecting visual fields: {str(e)}")
        
        return fields
    
    def analyze_document_type(self, text_content: str) -> Dict:
        """Analyze document type and suggest field types"""
        analysis = {
            'document_type': 'general',
            'suggested_fields': [],
            'confidence': 0.5
        }
        
        text_lower = text_content.lower()
        
        # Contract document patterns
        contract_keywords = ['contract', 'agreement', 'terms', 'conditions', 'signature', 'date', 'party']
        if any(keyword in text_lower for keyword in contract_keywords):
            analysis['document_type'] = 'contract'
            analysis['suggested_fields'] = [
                {'name': 'contract_date', 'type': 'date', 'label': 'Contract Date'},
                {'name': 'party_name', 'type': 'text', 'label': 'Party Name'},
                {'name': 'signature', 'type': 'signature', 'label': 'Signature'},
                {'name': 'amount', 'type': 'currency', 'label': 'Amount'}
            ]
            analysis['confidence'] = 0.8
        
        # Invoice patterns
        invoice_keywords = ['invoice', 'bill', 'amount due', 'payment', 'total', 'subtotal']
        if any(keyword in text_lower for keyword in invoice_keywords):
            analysis['document_type'] = 'invoice'
            analysis['suggested_fields'] = [
                {'name': 'invoice_date', 'type': 'date', 'label': 'Invoice Date'},
                {'name': 'customer_name', 'type': 'text', 'label': 'Customer Name'},
                {'name': 'total_amount', 'type': 'currency', 'label': 'Total Amount'},
                {'name': 'due_date', 'type': 'date', 'label': 'Due Date'}
            ]
            analysis['confidence'] = 0.8
        
        # Application form patterns
        application_keywords = ['application', 'personal information', 'contact', 'address', 'phone']
        if any(keyword in text_lower for keyword in application_keywords):
            analysis['document_type'] = 'application'
            analysis['suggested_fields'] = [
                {'name': 'applicant_name', 'type': 'text', 'label': 'Applicant Name'},
                {'name': 'address', 'type': 'text', 'label': 'Address'},
                {'name': 'phone', 'type': 'phone', 'label': 'Phone Number'},
                {'name': 'email', 'type': 'email', 'label': 'Email Address'}
            ]
            analysis['confidence'] = 0.7
        
        return analysis
    
    def generate_ai_filled_data(self, extracted_data: Dict, document_analysis: Dict) -> Dict:
        """Generate AI-filled data for the detected fields"""
        if not self.ai_processor:
            return self._generate_sample_data(extracted_data, document_analysis)
        
        try:
            # Prepare context for AI
            context = {
                'document_type': document_analysis['document_type'],
                'text_content': extracted_data['text_content'][:2000],  # Limit context size
                'fields': []
            }
            
            # Collect all detected fields
            all_fields = []
            for page in extracted_data['pages']:
                for field in page['fields']:
                    field_info = {
                        'name': field.get('name', ''),
                        'type': field.get('suggested_type', 'text'),
                        'page': field.get('page', 0)
                    }
                    all_fields.append(field_info)
            
            context['fields'] = all_fields
            
            # Use AI to generate appropriate data
            ai_prompt = f"""
            Based on this {document_analysis['document_type']} document, generate realistic sample data for the following fields:
            
            Document Type: {document_analysis['document_type']}
            Fields to fill: {json.dumps(all_fields, indent=2)}
            
            Please return a JSON object with field names as keys and appropriate sample values as values.
            Make the data realistic and contextually appropriate for a {document_analysis['document_type']} document.
            """
            
            # Try different AI processor methods
            if hasattr(self.ai_processor, 'process_text'):
                ai_response = self.ai_processor.process_text(ai_prompt)
            elif hasattr(self.ai_processor, 'generate_response'):
                ai_response = self.ai_processor.generate_response(ai_prompt)
            elif hasattr(self.ai_processor, 'chat'):
                ai_response = self.ai_processor.chat(ai_prompt)
            else:
                # Fallback to sample data
                filled_data = self._generate_sample_data(extracted_data, document_analysis)
                return filled_data
            
            # Try to parse AI response as JSON
            try:
                filled_data = json.loads(ai_response)
            except:
                # Fallback to sample data generation
                filled_data = self._generate_sample_data(extracted_data, document_analysis)
            
            return filled_data
            
        except Exception as e:
            logging.error(f"Error generating AI data: {str(e)}")
            return self._generate_sample_data(extracted_data, document_analysis)
    
    def _generate_sample_data(self, extracted_data: Dict, document_analysis: Dict) -> Dict:
        """Generate sample data when AI is not available"""
        sample_data = {}
        
        # Get all detected field names to generate appropriate data
        all_field_names = []
        for page in extracted_data['pages']:
            for field in page['fields']:
                field_name = field.get('name', '')
                if field_name:
                    all_field_names.append(field_name.lower())
        
        # Generate specific data based on field names found
        if 'full_name' in all_field_names:
            sample_data['full_name'] = 'John Smith'
        if 'name' in all_field_names:
            sample_data['name'] = 'John Smith'
        # Also check for fields that might contain 'full' and 'name'
        for field_name in all_field_names:
            if 'full' in field_name and 'name' in field_name:
                sample_data[field_name] = 'John Smith'
        
        if 'date_of_birth' in all_field_names or 'birth' in all_field_names:
            sample_data['date_of_birth'] = '1985-06-15'
            sample_data['birth'] = '1985-06-15'
        
        if 'signature' in all_field_names:
            sample_data['signature'] = 'John Smith'
        
        if 'address' in all_field_names:
            sample_data['address'] = '123 Main Street, City, State 12345'
        
        if 'phone' in all_field_names:
            sample_data['phone'] = '(555) 123-4567'
        
        if 'email' in all_field_names:
            sample_data['email'] = 'john.smith@email.com'
        
        if 'date' in all_field_names:
            sample_data['date'] = datetime.now().strftime('%Y-%m-%d')
        
        if 'amount' in all_field_names:
            sample_data['amount'] = '$1,250.00'
        
        # Generate sample data based on document type if no specific fields found
        if not sample_data:
            if document_analysis['document_type'] == 'contract':
                sample_data = {
                    'contract_date': datetime.now().strftime('%Y-%m-%d'),
                    'party_name': 'John Doe',
                    'signature': 'John Doe',
                    'amount': '$5,000.00'
                }
            elif document_analysis['document_type'] == 'invoice':
                sample_data = {
                    'invoice_date': datetime.now().strftime('%Y-%m-%d'),
                    'customer_name': 'ABC Company',
                    'total_amount': '$1,250.00',
                    'due_date': datetime.now().strftime('%Y-%m-%d')
                }
            elif document_analysis['document_type'] == 'application':
                sample_data = {
                    'applicant_name': 'Jane Smith',
                    'address': '123 Main St, City, State 12345',
                    'phone': '(555) 123-4567',
                    'email': 'jane.smith@email.com'
                }
            else:
                # Generic sample data
                sample_data = {
                    'name': 'Sample Name',
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'amount': '$100.00',
                    'signature': 'Sample Signature'
                }
        
        return sample_data
    
    def create_editable_pdf(self, extracted_data: Dict, filled_data: Dict, output_path: str) -> str:
        """Create a new editable PDF that preserves original formatting with AI-filled data"""
        try:
            # Use PyMuPDF to preserve original layout and styling
            import fitz
            
            # Open the original PDF to get layout information
            original_pdf_path = extracted_data.get('original_path', '')
            if not original_pdf_path or not os.path.exists(original_pdf_path):
                # Fallback to reportlab if no original path
                return self._create_simple_editable_pdf(extracted_data, filled_data, output_path)
            
            # Open the original document
            original_doc = fitz.open(original_pdf_path)
            
            # Create a copy of the original document
            new_doc = fitz.open()
            
            # Copy each page from original to new document
            for page_num in range(len(original_doc)):
                original_page = original_doc[page_num]
                
                # Create a new page with same dimensions
                new_page = new_doc.new_page(width=original_page.rect.width, height=original_page.rect.height)
                
                # Copy the entire original page content (including formatting, colors, layout)
                new_page.show_pdf_page(original_page.rect, original_doc, page_num)
                
                # Now fill in the data while preserving all original formatting
                if page_num < len(extracted_data['pages']):
                    page_data = extracted_data['pages'][page_num]
                    self._fill_form_fields_preserving_layout(new_page, page_data, filled_data)
            
            original_doc.close()
            
            # Save the new PDF
            new_doc.save(output_path)
            new_doc.close()
            
            return output_path
            
        except Exception as e:
            logging.error(f"Error creating editable PDF with original formatting: {str(e)}")
            # Fallback to simple PDF creation
            return self._create_simple_editable_pdf(extracted_data, filled_data, output_path)
    
    def _fill_form_fields_preserving_layout(self, page, page_data: Dict, filled_data: Dict):
        """Fill form fields while preserving the original layout and formatting"""
        try:
            # Get text blocks from the original page to understand positioning
            text_dict = page.get_text("dict")
            
            # Process each field and fill it while preserving original formatting
            for field in page_data['fields']:
                field_name = field.get('name', '')
                field_type = field.get('type', '')
                filled_value = filled_data.get(field_name, '')
                
                if not filled_value:
                    continue
                
                # Find the position of this field on the page
                field_position = self._find_field_position_for_filling(page, field, text_dict)
                
                if field_position:
                    # Fill the field with data while preserving original formatting
                    self._fill_single_field(page, field, filled_value, field_position)
                    
        except Exception as e:
            logging.error(f"Error filling form fields: {str(e)}")
    
    def _fill_single_field(self, page, field: Dict, filled_value: str, position: tuple):
        """Fill a single form field while preserving original formatting"""
        try:
            field_type = field.get('type', '')
            field_label = field.get('label', '')
            field_name = field.get('name', '')
            
            # For colon-based fields, fill in the appropriate location
            if field_type == 'colon_field':
                # Find the area after the colon to fill
                rect = fitz.Rect(position)
                
                # Calculate position to the right of the colon with better spacing
                fill_x = rect.x1 + 20  # More space after the colon
                fill_y = rect.y0 - 2   # Align with the label baseline
                
                # First, clear any existing text in the area where we'll fill
                clear_rect = fitz.Rect(fill_x, rect.y0 - 15, fill_x + 200, rect.y0 + 5)
                page.add_redact_annot(clear_rect, fill=(1, 1, 1))  # White fill
                page.apply_redactions()
                
                # Insert the filled text
                page.insert_text(
                    fitz.Point(fill_x, fill_y),
                    str(filled_value),
                    fontsize=12,
                    color=(0, 0, 0),  # Black text
                    fontname="helv"
                )
                
                print(f"Filled field '{field_label}' with '{filled_value}' at position ({fill_x}, {fill_y})")
            
            # For other field types (dotted lines, underscores, etc.)
            else:
                rect = fitz.Rect(position)
                
                # Clear the area first
                page.add_redact_annot(rect, fill=(1, 1, 1))  # White fill
                page.apply_redactions()
                
                # Insert text in the field area
                page.insert_text(
                    rect.tl + fitz.Point(5, -8),
                    str(filled_value),
                    fontsize=11,
                    color=(0, 0, 0),
                    fontname="helv"
                )
                
                print(f"Filled field '{field_name}' with '{filled_value}'")
                
        except Exception as e:
            logging.error(f"Error filling single field '{field_label}': {str(e)}")
    
    def _find_field_position_for_filling(self, page, field: Dict, text_dict: Dict) -> tuple:
        """Find the exact position where to fill the field data"""
        try:
            field_type = field.get('type', '')
            field_text = field.get('text', '')
            field_label = field.get('label', '')
            
            # Look for the field text in the page's text blocks
            for block in text_dict.get("blocks", []):
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            text = span.get("text", "")
                            
                            # For colon fields, find the label
                            if field_type == 'colon_field' and field_label:
                                if field_label.lower() in text.lower() and ':' in text:
                                    bbox = span["bbox"]
                                    return bbox
                            
                            # For other fields, look for the field pattern
                            elif field_text and (field_text in text or self._text_matches_field(text, field_text)):
                                bbox = span["bbox"]
                                return bbox
            
            # If not found, estimate position based on field type
            if field_type == 'colon_field':
                # For colon fields, return a reasonable position
                return (200, 200, 400, 220)
            else:
                # Default position
                return (100, 100, 200, 120)
            
        except Exception as e:
            logging.error(f"Error finding field position for filling: {str(e)}")
            return (100, 100, 200, 120)
    
    def _find_field_position(self, page, field: Dict, text_dict: Dict) -> tuple:
        """Find the position of a field on the page"""
        try:
            field_type = field.get('type', '')
            field_text = field.get('text', '')
            
            # Look for the field text in the page's text blocks
            for block in text_dict.get("blocks", []):
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            text = span.get("text", "")
                            if field_text in text or self._text_matches_field(text, field_text):
                                # Found the field text, return its position
                                bbox = span["bbox"]
                                return bbox
            
            # If not found in text, try to estimate position based on field type
            if field_type == 'dotted_line':
                # For dotted lines, create a reasonable text box
                return (100, 100, 200, 120)
            elif field_type == 'underscore':
                # For underscores, create a text box
                return (100, 100, 200, 120)
            
            # Default position
            return (100, 100, 200, 120)
            
        except Exception as e:
            logging.error(f"Error finding field position: {str(e)}")
            return (100, 100, 200, 120)
    
    def _text_matches_field(self, text: str, field_text: str) -> bool:
        """Check if text matches a field pattern"""
        # Remove extra spaces and normalize
        text_clean = re.sub(r'\s+', '', text)
        field_clean = re.sub(r'\s+', '', field_text)
        
        # Check for common field patterns
        if '...' in field_text and '...' in text:
            return True
        if '___' in field_text and '___' in text:
            return True
        if '---' in field_text and '---' in text:
            return True
            
        return text_clean == field_clean
    
    def _create_simple_editable_pdf(self, extracted_data: Dict, filled_data: Dict, output_path: str) -> str:
        """Fallback method to create a simple editable PDF"""
        try:
            doc = SimpleDocTemplate(output_path, pagesize=letter)
            story = []
            styles = getSampleStyleSheet()
            
            # Create styles that mimic original formatting
            normal_style = ParagraphStyle(
                'Normal',
                parent=styles['Normal'],
                fontSize=11,
                leading=14,
                textColor=colors.black
            )
            
            # Process each page
            for page_num, page_data in enumerate(extracted_data['pages']):
                if page_num > 0:
                    story.append(PageBreak())
                
                # Add page content with original formatting preserved
                page_text = page_data['text']
                
                # Replace field patterns with filled data while preserving formatting
                processed_text = self._process_text_with_filled_data(page_text, page_data['fields'], filled_data)
                
                # Add the processed text
                if processed_text.strip():
                    story.append(Paragraph(processed_text, normal_style))
                    story.append(Spacer(1, 12))
            
            # Build the PDF
            doc.build(story)
            
            return output_path
            
        except Exception as e:
            logging.error(f"Error creating simple editable PDF: {str(e)}")
            raise Exception(f"Failed to create editable PDF: {str(e)}")
    
    def _process_text_with_filled_data(self, text: str, fields: List[Dict], filled_data: Dict) -> str:
        """Process text and replace field patterns with filled data"""
        processed_text = text
        
        for field in fields:
            field_name = field.get('name', '')
            field_text = field.get('text', '')
            field_type = field.get('type', '')
            filled_value = filled_data.get(field_name, '')
            
            if filled_value:
                # Handle colon-based fields (like "Full Name:", "Date of Birth:")
                if field_type == 'colon_field':
                    # For colon fields, add the filled value after the colon
                    if field_text in processed_text:
                        # Replace "Full Name:" with "Full Name: John Smith"
                        processed_text = processed_text.replace(
                            field_text, 
                            f"{field_text} <b>{filled_value}</b>"
                        )
                    else:
                        # If not found exactly, try to find the label part
                        label = field.get('label', '')
                        if label:
                            label_colon = f"{label}:"
                            if label_colon in processed_text:
                                processed_text = processed_text.replace(
                                    label_colon,
                                    f"{label_colon} <b>{filled_value}</b>"
                                )
                
                # Handle other field types
                elif field_text and field_text in processed_text:
                    # Replace the field pattern with filled value
                    processed_text = processed_text.replace(
                        field_text, 
                        f"<b>{filled_value}</b>"
                    )
        
        return processed_text
    
    def process_pdf(self, input_pdf_path: str, output_pdf_path: str = None) -> Dict:
        """
        Main method to process a PDF: extract text, analyze, fill with AI, and create editable PDF
        """
        try:
            if not os.path.exists(input_pdf_path):
                raise FileNotFoundError(f"Input PDF not found: {input_pdf_path}")
            
            if output_pdf_path is None:
                base_name = os.path.splitext(os.path.basename(input_pdf_path))[0]
                output_pdf_path = f"{base_name}_editable_ai_filled.pdf"
            
            # Step 1: Extract text and layout
            print("Step 1: Extracting text and layout from PDF...")
            extracted_data = self.extract_text_with_layout(input_pdf_path)
            # Store original path for preserving formatting
            extracted_data['original_path'] = input_pdf_path
            
            # Step 2: Analyze document type
            print("Step 2: Analyzing document type...")
            document_analysis = self.analyze_document_type(extracted_data['text_content'])
            
            # Step 3: Generate AI-filled data
            print("Step 3: Generating AI-filled data...")
            
            # Debug: Print detected fields
            all_fields = []
            for page in extracted_data['pages']:
                for field in page['fields']:
                    all_fields.append(f"{field.get('name', '')} ({field.get('type', '')})")
            print(f"Detected fields: {all_fields}")
            
            filled_data = self.generate_ai_filled_data(extracted_data, document_analysis)
            print(f"Generated filled data: {filled_data}")
            
            # Step 4: Create editable PDF
            print("Step 4: Creating editable PDF with AI-filled data...")
            output_path = self.create_editable_pdf(extracted_data, filled_data, output_pdf_path)
            
            result = {
                'success': True,
                'input_pdf': input_pdf_path,
                'output_pdf': output_path,
                'document_type': document_analysis['document_type'],
                'fields_detected': len([f for page in extracted_data['pages'] for f in page['fields']]),
                'fields_filled': len(filled_data),
                'extracted_text': extracted_data['text_content'][:500] + "..." if len(extracted_data['text_content']) > 500 else extracted_data['text_content'],
                'filled_data': filled_data
            }
            
            print(f"Successfully created editable PDF: {output_path}")
            print(f"Document type: {document_analysis['document_type']}")
            print(f"Fields detected: {result['fields_detected']}")
            print(f"Fields filled: {result['fields_filled']}")
            
            return result
            
        except Exception as e:
            logging.error(f"Error processing PDF: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'input_pdf': input_pdf_path
            }


def main():
    """Test the PDF recreator with a sample file"""
    recreator = PDFRecreator()
    
    # Test with a sample PDF (if available)
    test_pdf = "test_document.pdf"
    if os.path.exists(test_pdf):
        result = recreator.process_pdf(test_pdf)
        print(json.dumps(result, indent=2))
    else:
        print("No test PDF found. Please provide a PDF file to test.")


if __name__ == "__main__":
    main()
