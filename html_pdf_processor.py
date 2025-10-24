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
    # Table-related attributes
    table_id: str = ""
    table_row: int = -1
    table_col: int = -1


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
        text_extracted = False
        
        # Method 1: Try PyMuPDF for AcroForm fields
        try:
            doc = fitz.open(pdf_path)
            for page_num in range(len(doc)):
                page = doc[page_num]
                page_text = page.get_text()
                if not text_extracted:
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
                    'fields': page_fields,
                    'tables': []  # Initialize empty tables
                })
            
            doc.close()
            text_extracted = True
            
        except Exception as e:
            print(f"PyMuPDF extraction failed: {e}")
        
        # Method 2: Use pdfplumber for additional field detection and table extraction
        if not all_fields:
            try:
                with pdfplumber.open(pdf_path) as pdf:
                    for page_num, page in enumerate(pdf.pages):
                        page_text = page.extract_text() or ""
                        # Only add text if we haven't extracted it already
                        if not text_extracted:
                            extracted_text += page_text + "\n"
                        
                        # Detect visual blanks and form-like patterns
                        visual_fields = self._detect_visual_fields(page_text, page_num)
                        all_fields.extend(visual_fields)
                        
                        # Extract tables from the page
                        tables = self._extract_tables_from_page(page, page_num)
                        
                        # Only add to pages_data if we haven't already processed this page
                        if not pages_data or len(pages_data) <= page_num:
                            pages_data.append({
                                'page_number': page_num,
                                'text': page_text,
                                'fields': visual_fields,
                                'tables': tables
                            })
                        else:
                            # Update existing page data with tables
                            pages_data[page_num]['tables'] = tables
                        
            except Exception as e:
                print(f"PDFplumber extraction failed: {e}")
        
        # Also extract tables using PyMuPDF if we used that method
        if text_extracted and pages_data:
            try:
                doc = fitz.open(pdf_path)
                for page_num in range(len(doc)):
                    page = doc[page_num]
                    tables = self._extract_tables_with_pymupdf(page, page_num)
                    if page_num < len(pages_data):
                        pages_data[page_num]['tables'] = tables
                doc.close()
            except Exception as e:
                print(f"PyMuPDF table extraction failed: {e}")
        
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
        
        # Pattern 1: Dotted lines (...) - more aggressive detection
        dotted_patterns = [
            r'\.{3,}',  # Basic dots
            r'\.{2,}\s*\.{2,}',  # Dotted lines with spaces
            r'\.{4,}',  # Longer dotted lines
        ]
        for pattern in dotted_patterns:
            for match in re.finditer(pattern, text):
                field = Field(
                    id=f"dotted_{len(fields)}",
                    name=f"field_{len(fields)}",
                    field_type='text',
                    x=0,  # Will be positioned in HTML
                    y=0,
                    width=len(match.group()) * 8,  # Width based on length
                    height=20,
                    page=page_num,
                    placeholder=self._generate_contextual_placeholder(text, match.start()),
                    value=""  # Initialize empty
                )
                fields.append(field)
        
        # Pattern 2: Underscore lines (___) - more aggressive detection
        underscore_patterns = [
            r'_{3,}',  # Basic underscores
            r'_{2,}\s*_{2,}',  # Underscores with spaces
            r'_{4,}',  # Longer underscore lines
        ]
        for pattern in underscore_patterns:
            for match in re.finditer(pattern, text):
                field = Field(
                    id=f"underscore_{len(fields)}",
                    name=f"field_{len(fields)}",
                    field_type='text',
                    x=0,
                    y=0,
                    width=len(match.group()) * 8,
                    height=20,
                    page=page_num,
                    placeholder=self._generate_contextual_placeholder(text, match.start()),
                    value=""
                )
                fields.append(field)
        
        # Pattern 3: Dash lines (---) - more aggressive detection
        dash_patterns = [
            r'-{3,}',  # Basic dashes
            r'-{2,}\s*-{2,}',  # Dashes with spaces
            r'-{4,}',  # Longer dash lines
        ]
        for pattern in dash_patterns:
            for match in re.finditer(pattern, text):
                field = Field(
                    id=f"dash_{len(fields)}",
                    name=f"field_{len(fields)}",
                    field_type='text',
                    x=0,
                    y=0,
                    width=len(match.group()) * 8,
                    height=20,
                    page=page_num,
                    placeholder=self._generate_contextual_placeholder(text, match.start()),
                    value=""
                )
                fields.append(field)
        
        # Pattern 4: Empty brackets () - detect fillable blanks
        bracket_patterns = [
            r'\(\s*\)',  # Empty brackets
            r'\(\s*\.{2,}\s*\)',  # Brackets with dots
            r'\(\s*_{2,}\s*\)',  # Brackets with underscores
        ]
        for pattern in bracket_patterns:
            for match in re.finditer(pattern, text):
                field = Field(
                    id=f"bracket_{len(fields)}",
                    name=f"field_{len(fields)}",
                    field_type='text',
                    x=0,
                    y=0,
                    width=80,
                    height=20,
                    page=page_num,
                    placeholder=self._generate_contextual_placeholder(text, match.start()),
                    value=""
                )
                fields.append(field)
        
        # Pattern 5: Blank spaces that look like fields
        blank_patterns = [
            r'\s{5,}',  # Multiple spaces (5+ spaces)
            r'\t+',     # Tab characters
        ]
        for pattern in blank_patterns:
            for match in re.finditer(pattern, text):
                # Only create fields for significant blanks
                if len(match.group().strip()) == 0 and len(match.group()) >= 5:
                    field = Field(
                        id=f"blank_{len(fields)}",
                        name=f"field_{len(fields)}",
                        field_type='text',
                        x=0,
                        y=0,
                        width=len(match.group()) * 4,
                        height=20,
                        page=page_num,
                        placeholder=self._generate_contextual_placeholder(text, match.start()),
                        value=""
                    )
                    fields.append(field)
        
        return fields
    
    def _generate_contextual_placeholder(self, text: str, position: int) -> str:
        """Generate a contextual placeholder based on surrounding text"""
        # Get context around the field position
        start = max(0, position - 50)
        end = min(len(text), position + 50)
        context = text[start:end].lower()
        
        # Common field type patterns
        if any(word in context for word in ['name', 'full name', 'given name', 'family name']):
            return "Enter name"
        elif any(word in context for word in ['address', 'street', 'location']):
            return "Enter address"
        elif any(word in context for word in ['date', 'day', 'month', 'year']):
            return "Enter date"
        elif any(word in context for word in ['phone', 'mobile', 'contact', 'number']):
            return "Enter phone number"
        elif any(word in context for word in ['email', 'e-mail']):
            return "Enter email"
        elif any(word in context for word in ['id', 'identification', 'student id']):
            return "Enter ID number"
        elif any(word in context for word in ['signature', 'sign']):
            return "Enter signature"
        elif any(word in context for word in ['amount', 'salary', 'wage', 'money', 'cost']):
            return "Enter amount"
        elif any(word in context for word in ['age', 'birth', 'born']):
            return "Enter age"
        elif any(word in context for word in ['company', 'employer', 'organization']):
            return "Enter company name"
        elif any(word in context for word in ['position', 'job', 'title', 'role']):
            return "Enter position"
        elif any(word in context for word in ['department', 'division']):
            return "Enter department"
        elif any(word in context for word in ['city', 'town']):
            return "Enter city"
        elif any(word in context for word in ['country', 'nation']):
            return "Enter country"
        elif any(word in context for word in ['postcode', 'zip', 'code']):
            return "Enter postcode"
        elif any(word in context for word in ['yes', 'no', 'agree', 'accept']):
            return "Enter yes/no"
        else:
            return "Enter value"
    
    def _extract_tables_from_page(self, page, page_num: int) -> List[Dict]:
        """Extract tables from a PDF page using pdfplumber"""
        tables = []
        
        try:
            # Extract tables using pdfplumber's table detection
            page_tables = page.extract_tables()
            
            for table_idx, table in enumerate(page_tables):
                if table and len(table) > 0:
                    # Process the table data
                    processed_table = {
                        'id': f"table_{page_num}_{table_idx}",
                        'page': page_num,
                        'rows': len(table),
                        'cols': len(table[0]) if table else 0,
                        'data': table,
                        'has_form_fields': False,
                        'fields': []
                    }
                    
                    # Check if table contains form fields (blanks, underscores, etc.)
                    for row_idx, row in enumerate(table):
                        for col_idx, cell in enumerate(row):
                            if cell and isinstance(cell, str):
                                # Check for field indicators in table cells
                                if self._is_table_cell_field(cell):
                                    field = Field(
                                        id=f"table_field_{page_num}_{table_idx}_{row_idx}_{col_idx}",
                                        name=f"table_field_{row_idx}_{col_idx}",
                                        field_type='text',
                                        x=0,  # Will be positioned in HTML
                                        y=0,
                                        width=100,
                                        height=20,
                                        page=page_num,
                                        placeholder=self._extract_field_placeholder(cell),
                                        table_id=processed_table['id'],
                                        table_row=row_idx,
                                        table_col=col_idx
                                    )
                                    processed_table['fields'].append(field)
                                    processed_table['has_form_fields'] = True
                    
                    tables.append(processed_table)
                    
        except Exception as e:
            print(f"Error extracting tables from page {page_num}: {e}")
        
        return tables
    
    def _extract_tables_with_pymupdf(self, page, page_num: int) -> List[Dict]:
        """Extract tables from a PDF page using PyMuPDF"""
        tables = []
        
        try:
            # Get page text and try to identify table-like structures
            text = page.get_text()
            
            # Look for table patterns in text
            table_patterns = self._identify_table_patterns(text)
            
            for table_idx, pattern in enumerate(table_patterns):
                table_data = self._parse_table_from_pattern(pattern)
                
                if table_data:
                    processed_table = {
                        'id': f"pymupdf_table_{page_num}_{table_idx}",
                        'page': page_num,
                        'rows': len(table_data),
                        'cols': len(table_data[0]) if table_data else 0,
                        'data': table_data,
                        'has_form_fields': False,
                        'fields': []
                    }
                    
                    # Check for form fields in table
                    for row_idx, row in enumerate(table_data):
                        for col_idx, cell in enumerate(row):
                            if cell and isinstance(cell, str):
                                if self._is_table_cell_field(cell):
                                    field = Field(
                                        id=f"pymupdf_table_field_{page_num}_{table_idx}_{row_idx}_{col_idx}",
                                        name=f"table_field_{row_idx}_{col_idx}",
                                        field_type='text',
                                        x=0,
                                        y=0,
                                        width=100,
                                        height=20,
                                        page=page_num,
                                        placeholder=self._extract_field_placeholder(cell),
                                        table_id=processed_table['id'],
                                        table_row=row_idx,
                                        table_col=col_idx
                                    )
                                    processed_table['fields'].append(field)
                                    processed_table['has_form_fields'] = True
                    
                    tables.append(processed_table)
                    
        except Exception as e:
            print(f"Error extracting tables with PyMuPDF from page {page_num}: {e}")
        
        return tables
    
    def _is_table_cell_field(self, cell_content: str) -> bool:
        """Check if a table cell contains a form field"""
        if not cell_content or not isinstance(cell_content, str):
            return False
        
        cell = cell_content.strip()
        
        # Check for common field patterns
        field_patterns = [
            r'\.{3,}',  # Dotted lines
            r'_{3,}',   # Underscore lines
            r'___+',    # Multiple underscores
            r'\[.*\]',  # Brackets
            r'\(.*\)',  # Parentheses
            r'Enter.*', # "Enter value" type text
            r'Fill.*',  # "Fill in" type text
            r'\.\.\.',  # Three dots
            r'^\s*$',   # Empty or whitespace only
        ]
        
        for pattern in field_patterns:
            if re.search(pattern, cell, re.IGNORECASE):
                return True
        
        return False
    
    def _extract_field_placeholder(self, cell_content: str) -> str:
        """Extract a meaningful placeholder from table cell content"""
        if not cell_content:
            return "Enter value"
        
        cell = cell_content.strip()
        
        # If it's just dots or underscores, return generic placeholder
        if re.match(r'^[._\s]+$', cell):
            return "Enter value"
        
        # If it contains text, use that as placeholder
        if len(cell) > 0 and not re.match(r'^[._\s]+$', cell):
            return cell
        
        return "Enter value"
    
    def _identify_table_patterns(self, text: str) -> List[str]:
        """Identify potential table patterns in text"""
        patterns = []
        
        # Look for lines that might be table rows
        lines = text.split('\n')
        potential_table_lines = []
        
        # Special handling for structured sections like "Working Conditions"
        structured_sections = self._identify_structured_sections(text)
        patterns.extend(structured_sections)
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line has multiple columns (separated by spaces, tabs, or other delimiters)
            if self._looks_like_table_row(line):
                potential_table_lines.append(line)
            else:
                # If we have accumulated table lines and hit a non-table line, 
                # save the accumulated lines as a potential table
                if len(potential_table_lines) >= 2:
                    patterns.append('\n'.join(potential_table_lines))
                potential_table_lines = []
        
        # Don't forget the last potential table
        if len(potential_table_lines) >= 2:
            patterns.append('\n'.join(potential_table_lines))
        
        return patterns
    
    def _identify_structured_sections(self, text: str) -> List[str]:
        """Identify structured sections that should be treated as tables"""
        patterns = []
        
        # Look for "Working Conditions" section specifically
        working_conditions_pattern = self._extract_working_conditions_table(text)
        if working_conditions_pattern:
            patterns.append(working_conditions_pattern)
        
        return patterns
    
    def _extract_working_conditions_table(self, text: str) -> str:
        """Extract the Working Conditions table structure"""
        lines = text.split('\n')
        
        # Find the start of Working Conditions section
        start_idx = None
        for i, line in enumerate(lines):
            if 'Working Conditions' in line:
                # Look for "Sr." in the next few lines
                for j in range(i+1, min(i+5, len(lines))):
                    if 'Sr.' in lines[j] and 'Rights' in lines[j]:
                        start_idx = i
                        break
                if start_idx is not None:
                    break
        
        if start_idx is None:
            return ""
        
        # Extract the table structure
        table_lines = []
        i = start_idx
        
        # Add the section title and header lines
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue
                
            # Stop at next major section
            if (line.startswith('10.') or line.startswith('11.') or 
                line.startswith('Notice') or line.startswith('Interpretation')):
                break
            
            # Add all lines that are part of the Working Conditions table
            table_lines.append(line)
            i += 1
        
        if len(table_lines) >= 5:  # Minimum rows for a meaningful table
            return '\n'.join(table_lines)
        
        return ""
    
    def _looks_like_table_row(self, line: str) -> bool:
        """Check if a line looks like a table row"""
        line = line.strip()
        if not line or len(line) < 5:
            return False
        
        # Count potential column separators
        tab_count = line.count('\t')
        
        # Look for patterns like "Item | Value | Notes" with proper separators
        if '|' in line and line.count('|') >= 2:
            # Make sure it's not just text with pipes in it
            parts = line.split('|')
            if len(parts) >= 3 and all(len(part.strip()) > 0 for part in parts):
                return True
        
        # Only consider tab-separated as table rows if there are multiple meaningful columns
        if tab_count > 0:
            parts = line.split('\t')
            if len(parts) >= 2 and all(len(part.strip()) > 0 for part in parts):
                return True
        
        # Look for structured data patterns (like numbered lists with consistent spacing)
        # But be more strict about it
        words = line.split()
        if len(words) >= 3:
            # Check if it looks like structured data (not regular text)
            # Avoid treating regular sentences as table rows
            if any(char in line for char in ['\t', '|']) or self._has_table_like_structure(line):
                return True
        
        return False
    
    def _has_table_like_structure(self, line: str) -> bool:
        """Check if line has table-like structure without being regular text"""
        # Look for patterns that suggest structured data
        # Multiple short segments separated by spaces
        words = line.split()
        if len(words) < 3:
            return False
        
        # Check if words are relatively short and evenly spaced (table-like)
        avg_word_length = sum(len(word) for word in words) / len(words)
        if avg_word_length < 8:  # Short words suggest structured data
            # Check for consistent spacing patterns
            if line.count('  ') >= 2:  # Multiple double spaces suggest table formatting
                return True
        
        return False
    
    def _parse_table_from_pattern(self, pattern: str) -> List[List[str]]:
        """Parse a table pattern into structured data"""
        lines = pattern.split('\n')
        table_data = []
        
        # Special handling for Working Conditions table
        if 'Working Conditions' in pattern:
            return self._parse_working_conditions_table(pattern)
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Try different parsing methods
            row_data = None
            
            # Method 1: Tab-separated
            if '\t' in line:
                row_data = [cell.strip() for cell in line.split('\t')]
            
            # Method 2: Pipe-separated
            elif '|' in line:
                row_data = [cell.strip() for cell in line.split('|')]
            
            # Method 3: Space-separated (be careful with this)
            else:
                # Split by multiple spaces
                row_data = [cell.strip() for cell in re.split(r'\s{2,}', line)]
            
            if row_data:
                table_data.append(row_data)
        
        return table_data
    
    def _parse_working_conditions_table(self, pattern: str) -> List[List[str]]:
        """Parse the Working Conditions table specifically"""
        lines = pattern.split('\n')
        table_data = []
        
        # This is a structured table with specific format:
        # Header: Sr. Rights | Provisions | Remarks
        # Rows: 1 | Working Hours and rest periods | 8 hours a day...
        
        # Add header row
        table_data.append(['Sr.', 'Rights', 'Provisions', 'Remarks'])
        
        current_row = []
        row_number = None
        collecting_content = False
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Skip the section title
            if 'Working Conditions' in line:
                continue
            
            # Skip the header row (we already added it)
            if 'Sr.' in line and 'Rights' in line:
                continue
            
            # Check if this is a row number (like "1", "2", etc.)
            if re.match(r'^\d+$', line):
                # Save previous row if we have one
                if current_row and row_number is not None:
                    # Pad the row to 4 columns if needed
                    while len(current_row) < 4:
                        current_row.append('')
                    table_data.append(current_row)
                
                # Start new row
                row_number = line
                current_row = [row_number, '', '', '']  # Initialize with 4 columns
                collecting_content = False
                continue
            
            # If we have a row number, we're collecting content
            if row_number is not None:
                # Determine which column this content belongs to
                # This is a simplified approach - in practice, you might need more sophisticated logic
                if not collecting_content:
                    # First content line goes to "Rights" column
                    current_row[1] = line
                    collecting_content = True
                else:
                    # Additional content lines go to "Provisions" or "Remarks" columns
                    if not current_row[2]:  # Provisions column is empty
                        current_row[2] = line
                    else:  # Append to Provisions or move to Remarks
                        current_row[2] += ' ' + line
        
        # Don't forget the last row
        if current_row and row_number is not None:
            # Pad the row to 4 columns if needed
            while len(current_row) < 4:
                current_row.append('')
            table_data.append(current_row)
        
        return table_data
    
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
            line-height: 1.1;
            margin: 0;
            padding: 0;
            background-color: white;
            color: black;
            font-size: 10pt;
            -webkit-text-size-adjust: 100%;
            text-rendering: optimizeLegibility;
        }}
        
        .document-container {{
            max-width: 210mm; /* A4 width */
            min-height: 297mm; /* A4 height */
            margin: 0 auto;
            background: white;
            padding: 12mm;
            position: relative;
            box-sizing: border-box;
        }}
        
        .page {{
            margin-bottom: 0;
            position: relative;
            font-size: 9pt;
            line-height: 1.1;
            page-break-after: auto;
        }}
        
        .text-content {{
            white-space: pre-line;
            font-size: 9pt;
            line-height: 1.1;
            margin-bottom: 3px;
            margin-top: 0;
            word-spacing: normal;
            letter-spacing: normal;
        }}
        
        .document-header {{
            text-align: center;
            margin-bottom: 8px;
            font-weight: bold;
        }}
        
        .document-title {{
            font-size: 11pt;
            font-weight: bold;
            margin-bottom: 4px;
        }}
        
        .document-subtitle {{
            font-size: 9pt;
            font-weight: bold;
            margin-bottom: 3px;
        }}
        
        .section-heading {{
            font-weight: bold;
            margin-top: 10px;
            margin-bottom: 5px;
            font-size: 9pt;
        }}
        
        .field-label {{
            display: inline-block;
            margin-right: 5px;
            font-weight: normal;
        }}
        
        .input-line {{
            display: inline-block;
            border-bottom: 1px solid #000;
            background: transparent;
            font-family: inherit;
            font-size: 9pt;
            padding: 0 1px;
            margin: 0 1px;
            min-width: 80px;
            height: 12px;
            line-height: 12px;
            vertical-align: baseline;
            position: relative;
            box-sizing: border-box;
        }}
        
        .underscore-line {{
            display: inline-block;
            border-bottom: 1px solid #000;
            background: transparent;
            font-family: inherit;
            font-size: 9pt;
            padding: 0 1px;
            margin: 0 1px;
            min-width: 100px;
            height: 12px;
            line-height: 12px;
            vertical-align: baseline;
            position: relative;
            box-sizing: border-box;
        }}
        
        /* Table styling */
        .pdf-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 4px 0;
            font-size: 10pt;
            border: 1px solid #000;
            table-layout: fixed;
        }}
        
        .table-cell {{
            border: 1px solid #000;
            padding: 2px;
            vertical-align: top;
            font-size: 10pt;
            line-height: 1.1;
            word-wrap: break-word;
        }}
        
        .table-input {{
            width: 100%;
            border: none;
            background: transparent;
            font-family: inherit;
            font-size: 11pt;
            padding: 1px 2px;
            outline: none;
            border-bottom: 1px solid #000;
            line-height: 1.2;
            box-sizing: border-box;
        }}
        
        .table-checkbox {{
            width: 12px;
            height: 12px;
            margin: 0;
            vertical-align: middle;
        }}
        
        /* Additional spacing fixes */
        * {{
            box-sizing: border-box;
        }}
        
        p, div, span {{
            margin: 0;
            padding: 0;
        }}
        
        /* PDF-specific styling for better rendering */
        @media print {{
            body {{
                margin: 0 !important;
                padding: 0 !important;
            }}
            
            .document-container {{
                padding: 8mm !important;
                margin: 0 !important;
            }}
            
            .input-line {{
                border-bottom: 1px solid #000 !important;
                background: transparent !important;
                padding: 0 2px !important;
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
            font-size: 9pt;
            padding: 0 1px;
            margin: 0;
            min-width: 80px;
            height: 12px;
            line-height: 12px;
            outline: none;
            color: #000;
        }}
        
        .editable-field::placeholder {{
            color: transparent;
        }}
        
        .editable-field:hover {{
            border-bottom: 1px solid #000;
            background-color: rgba(0, 123, 255, 0.05);
        }}
        
        .editable-field:focus {{
            border-bottom: 2px solid #007bff;
            background-color: rgba(0, 123, 255, 0.1);
            box-shadow: 0 1px 2px rgba(0, 123, 255, 0.2);
            color: #000;
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
            
            # Process tables if they exist
            if 'tables' in page and page['tables']:
                for table in page['tables']:
                    table_html = self._convert_table_to_html(table)
                    html_content += f'            {table_html}\n'
            
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
        
        # IMPORTANT: Global field counter that persists across all lines!
        self._field_counter = {'underscore': 0, 'dotted': 0, 'bracket': 0, 'blank': 0}
        
        # Process the text and embed fields naturally within the existing text structure
        lines = text.split('\n')
        
        for line in lines:
            if not line.strip():
                html_content += '<br>\n'
                continue
            
            # Detect centered headings and special formatting
            line_stripped = line.strip()
            is_centered = False
            style_class = "text-content"
            
            # Check if it's a centered heading (company name, document title, etc.)
            # But ONLY if it's a standalone heading line, not part of a paragraph
            if "TELECOM (FIJI) LIMITED" in line_stripped and len(line_stripped) < 50:
                is_centered = True
                style_class = "document-title"
            elif "EMPLOYMENT INDUCTION AGREEMENT" in line_stripped and len(line_stripped) < 50:
                is_centered = True
                style_class = "document-subtitle"
            elif line_stripped.startswith("Level 5,") or "Edward Street" in line_stripped:
                is_centered = True
            elif line_stripped.startswith("Phone:") and "Email:" in line_stripped:
                is_centered = True
            elif line_stripped.startswith("Website:"):
                is_centered = True
            elif line_stripped.isupper() and len(line_stripped) < 80 and not line_stripped.startswith("THIS"):
                # Short all-caps lines are likely section headings
                # But exclude lines starting with "THIS" (like the opening sentence)
                style_class = "section-heading"
            
            # Check if this line contains field indicators and embed fields naturally
            field_added = False
            for field in fields:
                if field.id in processed_field_ids:
                    continue
                    
                # Look for field indicators in the line and embed the field naturally
                if self._should_embed_field_in_line(line, field):
                    # Embed the field naturally within the line
                    embedded_line = self._embed_field_in_line(line, field)
                    
                    # Apply styling based on line type
                    if is_centered:
                        html_content += f'<div class="{style_class}" style="text-align: center;">{embedded_line}</div>\n'
                    else:
                        html_content += f'<div class="{style_class}">{embedded_line}</div>\n'
                    
                    processed_field_ids.add(field.id)
                    field_added = True
                    break
            
            if not field_added:
                # Check if this line contains visual field indicators that should be converted
                converted_line = self._convert_visual_indicators_to_inputs(line, fields)
                
                # Apply styling based on line type
                if is_centered:
                    html_content += f'<div class="{style_class}" style="text-align: center;">{converted_line}</div>\n'
                else:
                    html_content += f'<div class="{style_class}">{converted_line}</div>\n'
        
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
    
    def _convert_visual_indicators_to_inputs(self, line: str, fields: List[Field]) -> str:
        """Convert visual field indicators in a line to input fields"""
        converted_line = line
        
        # Use the global field counter (set in _convert_text_to_html_with_fields)
        if not hasattr(self, '_field_counter'):
            self._field_counter = {'underscore': 0, 'dotted': 0, 'bracket': 0, 'blank': 0}
        
        # Replace underscore patterns with input fields
        underscore_patterns = [r'_{3,}', r'_{2,}\s*_{2,}', r'_{4,}']
        for pattern in underscore_patterns:
            matches = list(re.finditer(pattern, converted_line))
            for match in matches:
                # Find the next available underscore field using global counter
                field_id = f"underscore_{self._field_counter['underscore']}"
                field = next((f for f in fields if f.id == field_id), None)
                
                if field:
                    placeholder = field.placeholder
                    field_name = field.name
                else:
                    placeholder = "Enter value"
                    field_name = field_id
                
                # IMPORTANT: Include id and name attributes for AI filling to work!
                replacement = f'<input type="text" class="editable-field" id="{field_id}" name="{field_name}" placeholder="{placeholder}" value="" style="width: {len(match.group()) * 8}px; border-bottom: 1px solid #000; border-top: none; border-left: none; border-right: none; background: transparent;">'
                converted_line = converted_line.replace(match.group(), replacement, 1)
                self._field_counter['underscore'] += 1
        
        # Replace dotted patterns with input fields
        dotted_patterns = [r'\.{3,}', r'\.{2,}\s*\.{2,}', r'\.{4,}']
        for pattern in dotted_patterns:
            matches = list(re.finditer(pattern, converted_line))
            for match in matches:
                # Find the next available dotted field using global counter
                field_id = f"dotted_{self._field_counter['dotted']}"
                field = next((f for f in fields if f.id == field_id), None)
                
                if field:
                    placeholder = field.placeholder
                    field_name = field.name
                else:
                    placeholder = "Enter value"
                    field_name = field_id
                
                replacement = f'<input type="text" class="editable-field" id="{field_id}" name="{field_name}" placeholder="{placeholder}" value="" style="width: {len(match.group()) * 8}px; border-bottom: 1px dotted #000; border-top: none; border-left: none; border-right: none; background: transparent;">'
                converted_line = converted_line.replace(match.group(), replacement, 1)
                self._field_counter['dotted'] += 1
        
        # Replace bracket patterns with input fields
        bracket_patterns = [r'\(\s*\)', r'\(\s*\.{2,}\s*\)', r'\(\s*_{2,}\s*\)']
        for pattern in bracket_patterns:
            matches = list(re.finditer(pattern, converted_line))
            for match in matches:
                # Find the next available bracket field using global counter
                field_id = f"bracket_{self._field_counter['bracket']}"
                field = next((f for f in fields if f.id == field_id), None)
                
                if field:
                    placeholder = field.placeholder
                    field_name = field.name
                else:
                    placeholder = "Enter value"
                    field_name = field_id
                
                replacement = f'<input type="text" class="editable-field" id="{field_id}" name="{field_name}" placeholder="{placeholder}" value="" style="width: 80px; border: 1px solid #000; background: transparent;">'
                converted_line = converted_line.replace(match.group(), replacement, 1)
                self._field_counter['bracket'] += 1
        
        return converted_line
    
    def _convert_table_to_html(self, table: Dict) -> str:
        """Convert a table dictionary to HTML table with form fields"""
        if not table or not table.get('data'):
            return ""
        
        table_id = table.get('id', 'table')
        table_data = table['data']
        table_fields = table.get('fields', [])
        
        # Create a mapping of field positions for quick lookup
        field_map = {}
        for field in table_fields:
            if hasattr(field, 'table_row') and hasattr(field, 'table_col'):
                key = (field.table_row, field.table_col)
                field_map[key] = field
        
        html = f'        <table class="pdf-table" id="{table_id}">\n'
        
        for row_idx, row in enumerate(table_data):
            html += '            <tr>\n'
            
            for col_idx, cell in enumerate(row):
                cell_content = str(cell) if cell is not None else ""
                
                # Check if this cell has a form field
                field_key = (row_idx, col_idx)
                if field_key in field_map:
                    field = field_map[field_key]
                    # Replace cell content with form field
                    if field.field_type == 'checkbox':
                        html += f'                <td class="table-cell"><input type="checkbox" class="table-checkbox" id="{field.id}" name="{field.name}"></td>\n'
                    else:
                        html += f'                <td class="table-cell"><input type="{field.field_type}" class="table-input" id="{field.id}" name="{field.name}" placeholder="{field.placeholder}" value="{field.value}"></td>\n'
                else:
                    # Regular cell content
                    html += f'                <td class="table-cell">{cell_content}</td>\n'
            
            html += '            </tr>\n'
        
        html += '        </table>\n'
        
        return html
    
    def _should_embed_field_in_line(self, line: str, field: Field) -> bool:
        """Check if a field should be embedded in a specific line"""
        line_lower = line.lower()
        field_name_lower = field.name.lower()
        field_placeholder_lower = field.placeholder.lower()
        
        # First, check if the line contains the visual field indicator that this field represents
        if field.id.startswith('dotted'):
            # Check if line contains dotted patterns
            dotted_patterns = [r'\.{3,}', r'\.{2,}\s*\.{2,}', r'\.{4,}']
            for pattern in dotted_patterns:
                if re.search(pattern, line):
                    return True
        
        elif field.id.startswith('underscore'):
            # Check if line contains underscore patterns
            underscore_patterns = [r'_{3,}', r'_{2,}\s*_{2,}', r'_{4,}']
            for pattern in underscore_patterns:
                if re.search(pattern, line):
                    return True
        
        elif field.id.startswith('dash'):
            # Check if line contains dash patterns
            dash_patterns = [r'-{3,}', r'-{2,}\s*-{2,}', r'-{4,}']
            for pattern in dash_patterns:
                if re.search(pattern, line):
                    return True
        
        elif field.id.startswith('bracket'):
            # Check if line contains bracket patterns
            bracket_patterns = [r'\(\s*\)', r'\(\s*\.{2,}\s*\)', r'\(\s*_{2,}\s*\)']
            for pattern in bracket_patterns:
                if re.search(pattern, line):
                    return True
        
        elif field.id.startswith('blank'):
            # Check if line contains blank patterns
            blank_patterns = [r'\s{5,}', r'\t+']
            for pattern in blank_patterns:
                if re.search(pattern, line):
                    return True
        
        # Fallback: Check for common field patterns in the contract
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
        # Replace the field indicator with an input field based on field type
        
        if field.id.startswith('dotted'):
            # Replace dotted lines with underscore display
            dotted_patterns = [r'\.{3,}', r'\.{2,}\s*\.{2,}', r'\.{4,}']
            for pattern in dotted_patterns:
                if re.search(pattern, line):
                    replacement = f'<span class="underscore-line" id="{field.id}" data-field-name="{field.name}">____________________</span>'
                    return re.sub(pattern, replacement, line, count=1)
        
        elif field.id.startswith('underscore'):
            # Replace underscore lines with proper underscore display
            underscore_patterns = [r'_{3,}', r'_{2,}\s*_{2,}', r'_{4,}']
            for pattern in underscore_patterns:
                if re.search(pattern, line):
                    # Create a span with underscore styling instead of input field
                    replacement = f'<span class="underscore-line" id="{field.id}" data-field-name="{field.name}">____________________</span>'
                    return re.sub(pattern, replacement, line, count=1)
        
        elif field.id.startswith('dash'):
            # Replace dash lines with underscore display
            dash_patterns = [r'-{3,}', r'-{2,}\s*-{2,}', r'-{4,}']
            for pattern in dash_patterns:
                if re.search(pattern, line):
                    replacement = f'<span class="underscore-line" id="{field.id}" data-field-name="{field.name}">____________________</span>'
                    return re.sub(pattern, replacement, line, count=1)
        
        elif field.id.startswith('bracket'):
            # Replace bracket patterns with underscore display
            bracket_patterns = [r'\(\s*\)', r'\(\s*\.{2,}\s*\)', r'\(\s*_{2,}\s*\)']
            for pattern in bracket_patterns:
                if re.search(pattern, line):
                    replacement = f'<span class="underscore-line" id="{field.id}" data-field-name="{field.name}">____________________</span>'
                    return re.sub(pattern, replacement, line, count=1)
        
        elif field.id.startswith('blank'):
            # Replace blank spaces with underscore display
            blank_patterns = [r'\s{5,}', r'\t+']
            for pattern in blank_patterns:
                if re.search(pattern, line):
                    replacement = f'<span class="underscore-line" id="{field.id}" data-field-name="{field.name}">____________________</span>'
                    return re.sub(pattern, replacement, line, count=1)
        
        # Handle colon-based patterns (legacy support)
        elif ':' in line:
            # Split at the colon and add the field after it
            parts = line.split(':', 1)
            if len(parts) == 2:
                label = parts[0] + ':'
                rest = parts[1].strip()
                
                # If there's text after the colon, replace it with the field
                if rest:
                    return f'{label} <span class="underscore-line" id="{field.id}" data-field-name="{field.name}">_________________________</span>'
                else:
                    return f'{label} <span class="underscore-line" id="{field.id}" data-field-name="{field.name}">_________________________</span>'
        
        # Handle specific contract patterns
        if 'employer' in line.lower() and 'hereinafter' in line.lower():
            # Replace the long line with a field
            return line.replace('………………………………………………………', f'<span class="underscore-line" id="{field.id}" data-field-name="{field.name}">_________________________</span>')
        elif 'employee' in line.lower() and 'hereinafter' in line.lower():
            # Replace the long line with a field
            return line.replace('………………………………………………………', f'<span class="underscore-line" id="{field.id}" data-field-name="{field.name}">_________________________</span>')
        elif 'salary' in line.lower() and 'nu.' in line.lower():
            # Replace the salary blank with a field
            return line.replace('_______', f'<span class="underscore-line" id="{field.id}" data-field-name="{field.name}">_________________________</span>')
        elif 'capacity' in line.lower() and '__________' in line:
            # Replace the capacity blank with a field
            return line.replace('__________', f'<span class="underscore-line" id="{field.id}" data-field-name="{field.name}">_________________________</span>')
        elif 'day' in line.lower() and 'month' in line.lower() and 'year' in line.lower():
            # Replace the date blanks with fields
            line = line.replace('…..day……', f'<span class="underscore-line" id="{field.id}" data-field-name="{field.name}">_________________________</span>')
            return line
        elif 'id no' in line.lower() and '………………' in line:
            # Replace the ID blank with a field
            return line.replace('………………', f'<span class="underscore-line" id="{field.id}" data-field-name="{field.name}">_________________________</span>')
        elif 'contact no' in line.lower() and '………………' in line:
            # Replace the contact blank with a field
            return line.replace('………………', f'<span class="underscore-line" id="{field.id}" data-field-name="{field.name}">_________________________</span>')
        elif 'name:' in line.lower() and '………………' in line:
            # Replace the name blank with a field
            return line.replace('………………', f'<span class="underscore-line" id="{field.id}" data-field-name="{field.name}">_________________________</span>')
        elif 'at' in line.lower() and '………………………' in line:
            # Replace the location blank with a field
            return line.replace('………………………', f'<span class="underscore-line" id="{field.id}" data-field-name="{field.name}">_________________________</span>')
        elif 'responsible to' in line.lower() and '…………………………' in line:
            # Replace the responsibility blank with a field
            return line.replace('…………………………', f'<span class="underscore-line" id="{field.id}" data-field-name="{field.name}">_________________________</span>')
        elif 'job responsibilities' in line.lower() and '________________' in line:
            # Replace the job responsibilities blank with a field
            return line.replace('________________', f'<span class="underscore-line" id="{field.id}" data-field-name="{field.name}">_________________________</span>')
        
        # If no specific pattern, just add the field at the end
        return f'{line} <span class="underscore-line" id="{field.id}" data-field-name="{field.name}">_________________________</span>'
    
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
        """Get default value based on field type - return underscore lines for form fields"""
        # For form fields, return underscore lines instead of placeholder text
        underscore_lengths = {
            'text': '____________________',
            'email': '____________________',
            'phone': '____________________',
            'date': '____________________',
            'number': '____________________',
            'checkbox': '☐',
            'select': '____________________'
        }
        return underscore_lengths.get(field_type, '_________________________')
    
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
                
                # Then, handle underscore-line spans with the specific field_id
                pattern = rf'(<span[^>]*class="underscore-line"[^>]*id="{re.escape(field_id)}"[^>]*data-field-name="([^"]*)"[^>]*>)([^<]*)(</span>)'
                
                def replace_underscore_span(match):
                    field_name = match.group(2)
                    # Keep it as a span but replace the content with underscore lines
                    return f'<span class="underscore-line" id="{field_id}" data-field-name="{field_name}">____________________</span>'
                
                filled_html = re.sub(pattern, replace_underscore_span, filled_html)
                
                # Also handle input-line spans (legacy)
                pattern2 = rf'(<span[^>]*class="input-line"[^>]*id="{re.escape(field_id)}"[^>]*data-field-name="([^"]*)"[^>]*>)([^<]*)(</span>)'
                
                def replace_input_span(match):
                    field_name = match.group(2)
                    # Keep it as a span but replace the content with underscore lines
                    return f'<span class="underscore-line" id="{field_id}" data-field-name="{field_name}">____________________</span>'
                
                filled_html = re.sub(pattern2, replace_input_span, filled_html)
                
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
    
    def _html_to_pdf_simple(self, html_content: str, output_path: str):
        """Simple fallback PDF creation method"""
        try:
            # Try to use WeasyPrint as a simple fallback
            from weasyprint import HTML
            HTML(string=html_content).write_pdf(output_path)
            print(f"Successfully created PDF with WeasyPrint fallback: {output_path}")
        except Exception as e:
            print(f"Simple PDF creation also failed: {e}")
            # Create a basic text file as last resort
            text_path = output_path.replace('.pdf', '.txt')
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write("PDF generation failed. HTML content:\n\n")
                f.write(html_content)
            print(f"Created text file instead: {text_path}")
            raise Exception(f"All PDF generation methods failed. Last error: {e}")
    
    def _optimize_html_for_pdf(self, html_content: str) -> str:
        """Optimize HTML for better PDF rendering with improved spacing"""
        import re
        
        # Remove extra whitespace and normalize spacing
        html_content = re.sub(r'\s+', ' ', html_content)
        html_content = re.sub(r'>\s+<', '><', html_content)
        
        # Fix line breaks in text content
        html_content = re.sub(r'(\S)\n(\S)', r'\1 \2', html_content)
        
        # Replace editable input fields with PDF-friendly structure
        def replace_editable_field(match):
            field_id = match.group(1) if match.group(1) else ""
            field_name = match.group(2) if match.group(2) else ""
            value = match.group(3) if match.group(3) else ""
            
            # Create a more robust structure for PDF with better spacing
            return f'''<span class="pdf-field-container" style="display: inline-block; position: relative; min-width: 100px; height: 16px; border-bottom: 1px solid #000; margin: 0 1px; padding: 0 2px; box-sizing: border-box;">
                <span class="pdf-field-text" style="position: absolute; top: 0; left: 2px; right: 2px; height: 16px; line-height: 16px; font-family: inherit; font-size: 11pt; background: transparent; white-space: nowrap;">{value}</span>
            </span>'''
        
        # Pattern to match editable input fields
        editable_pattern = r'<input[^>]*class="editable-field"[^>]*id="([^"]*)"[^>]*name="([^"]*)"[^>]*value="([^"]*)"[^>]*>'
        optimized_html = re.sub(editable_pattern, replace_editable_field, html_content)
        
        # Also handle input-line spans for backward compatibility
        def replace_input_line(match):
            field_id = match.group(1) if match.group(1) else ""
            field_name = match.group(2) if match.group(2) else ""
            content = match.group(3) if match.group(3) else ""
            
            # Create a more robust structure for PDF with better spacing
            return f'''<span class="pdf-field-container" style="display: inline-block; position: relative; min-width: 100px; height: 16px; border-bottom: 1px solid #000; margin: 0 1px; padding: 0 2px; box-sizing: border-box;">
                <span class="pdf-field-text" style="position: absolute; top: 0; left: 2px; right: 2px; height: 16px; line-height: 16px; font-family: inherit; font-size: 11pt; background: transparent; white-space: nowrap;">{content}</span>
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
                'margin-top': '0.2in',
                'margin-right': '0.2in',
                'margin-bottom': '0.2in',
                'margin-left': '0.2in',
                'encoding': "UTF-8",
                'no-outline': None,
                'enable-local-file-access': None,
                'print-media-type': None,
                'disable-smart-shrinking': None,
                'disable-external-links': None,
                'disable-forms': None,
                'disable-javascript': None,
                'load-error-handling': 'ignore',
                'load-media-error-handling': 'ignore',
                'zoom': 1.0,
                'quiet': None,
                'lowquality': None
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
