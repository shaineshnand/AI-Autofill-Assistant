#!/usr/bin/env python
"""
Improved Field Detector for AI Autofill Assistant
Enhanced field detection with multiple algorithms and better accuracy
"""
import os
import cv2
import numpy as np
import pytesseract
import fitz  # PyMuPDF
import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from PIL import Image, ImageDraw, ImageFont
import json

@dataclass
class FormField:
    """Represents a form field with precise positioning and metadata"""
    id: str
    field_type: str
    x_position: int
    y_position: int
    width: int
    height: int
    page_number: int
    context: str = ""
    initial_content: str = ""
    confidence: float = 0.0
    options: Optional[List[str]] = None

class ImprovedFieldDetector:
    """Enhanced field detection with multiple algorithms"""
    
    def __init__(self):
        # Configure Tesseract path for Windows
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        
        # Field detection patterns
        self.field_patterns = {
            'name': [
                r'name\s*[:.]?\s*$', r'full\s+name', r'first\s+name', r'last\s+name',
                r'enter\s+your\s+name', r'your\s+name', r'applicant\s+name'
            ],
            'email': [
                r'email\s*[:.]?\s*$', r'e-mail\s*[:.]?\s*$', r'email\s+address',
                r'enter\s+email', r'your\s+email', r'contact\s+email'
            ],
            'phone': [
                r'phone\s*[:.]?\s*$', r'telephone\s*[:.]?\s*$', r'phone\s+number',
                r'contact\s+number', r'mobile\s*[:.]?\s*$', r'cell\s+phone'
            ],
            'address': [
                r'address\s*[:.]?\s*$', r'street\s+address', r'home\s+address',
                r'residential\s+address', r'location\s*[:.]?\s*$'
            ],
            'date': [
                r'date\s*[:.]?\s*$', r'birth\s+date', r'dob\s*[:.]?\s*$',
                r'date\s+of\s+birth', r'application\s+date', r'signature\s+date'
            ],
            'age': [
                r'age\s*[:.]?\s*$', r'years\s+old', r'how\s+old', r'current\s+age'
            ],
            'signature': [
                r'signature\s*[:.]?\s*$', r'sign\s+here', r'your\s+signature',
                r'digital\s+signature', r'authorized\s+signature'
            ]
        }
    
    def process_document(self, file_path: str) -> Dict:
        """Process document and detect form fields"""
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.pdf':
                return self._process_pdf(file_path)
            elif file_ext in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']:
                return self._process_image(file_path)
            else:
                # Fallback to text processing
                return self._process_text_file(file_path)
                
        except Exception as e:
            print(f"Error processing document: {e}")
            return {
                'extracted_text': '',
                'fields': [],
                'total_fields': 0
            }
    
    def _process_pdf(self, file_path: str) -> Dict:
        """Process PDF document with enhanced field detection"""
        try:
            doc = fitz.open(file_path)
            all_fields = []
            extracted_text = ""
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Extract text
                page_text = page.get_text()
                extracted_text += page_text + "\n"
                
                # Method 1: Try to extract AcroForm fields first
                acroform_fields = self._extract_acroform_fields(doc, page_num)
                all_fields.extend(acroform_fields)
                
                # Method 2: Convert page to image for visual field detection
                mat = fitz.Matrix(2.0, 2.0)  # Scale up for better detection
                pix = page.get_pixmap(matrix=mat)
                img_data = pix.tobytes("png")
                
                # Convert to OpenCV format
                nparr = np.frombuffer(img_data, np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                
                # Method 3: Detect fields using comprehensive visual analysis
                visual_fields = self._detect_fields_comprehensive(gray, page_text, page_num)
                all_fields.extend(visual_fields)
                
                # Method 4: Detect fields based on text patterns and layout
                text_pattern_fields = self._detect_text_pattern_fields(page_text, page_num)
                all_fields.extend(text_pattern_fields)
            
            # Remove duplicates and merge similar fields
            all_fields = self._merge_and_deduplicate_fields(all_fields)
            
            doc.close()
            
            return {
                'extracted_text': extracted_text.strip(),
                'fields': all_fields,
                'total_fields': len(all_fields)
            }
            
        except Exception as e:
            print(f"Error processing PDF: {e}")
            return {'extracted_text': '', 'fields': [], 'total_fields': 0}
    
    def _process_image(self, file_path: str) -> Dict:
        """Process image document"""
        try:
            # Load image
            image = cv2.imread(file_path)
            if image is None:
                raise Exception("Could not load image")
            
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Extract text using OCR
            extracted_text = pytesseract.image_to_string(image)
            
            # Detect fields
            fields = self._detect_fields_comprehensive(gray, extracted_text, 0)
            
            return {
                'extracted_text': extracted_text.strip(),
                'fields': fields,
                'total_fields': len(fields)
            }
            
        except Exception as e:
            print(f"Error processing image: {e}")
            return {'extracted_text': '', 'fields': [], 'total_fields': 0}
    
    def _process_text_file(self, file_path: str) -> Dict:
        """Process text file with enhanced underline detection"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            # Detect fields from text patterns and underlines
            all_fields = []
            
            # Method 1: Detect underlines in text
            lines = text.split('\n')
            field_id = 0
            for i, line in enumerate(lines):
                underline_fields = self._detect_underlines_in_line(line, i, 0, field_id)
                all_fields.extend(underline_fields)
                field_id += len(underline_fields)
            
            # Method 2: Create virtual fields based on text patterns
            virtual_fields = self._create_virtual_fields_from_text(text)
            all_fields.extend(virtual_fields)
            
            # Remove duplicates
            fields = self._merge_and_deduplicate_fields(all_fields)
            
            return {
                'extracted_text': text,
                'fields': fields,
                'total_fields': len(fields)
            }
            
        except Exception as e:
            print(f"Error processing text file: {e}")
            import traceback
            traceback.print_exc()
            return {'extracted_text': '', 'fields': [], 'total_fields': 0}
    
    def _detect_fields_comprehensive(self, gray_image: np.ndarray, text: str, page_num: int) -> List[FormField]:
        """Comprehensive field detection using multiple methods"""
        fields = []
        
        # Method 1: Detect rectangular form fields
        rectangular_fields = self._detect_rectangular_fields(gray_image, page_num)
        
        # Method 2: Detect fields based on text patterns
        text_based_fields = self._detect_text_based_fields(text, gray_image.shape, page_num)
        
        # Method 3: Detect underlines and form lines
        line_based_fields = self._detect_line_based_fields(gray_image, page_num)
        
        # Method 4: Detect blank spaces
        blank_space_fields = self._detect_blank_spaces(gray_image, page_num)
        
        # Combine all methods
        all_fields = rectangular_fields + text_based_fields + line_based_fields + blank_space_fields
        
        # Remove duplicates and merge similar fields
        fields = self._merge_and_deduplicate_fields(all_fields)
        
        return fields
    
    def _detect_rectangular_fields(self, gray_image: np.ndarray, page_num: int) -> List[FormField]:
        """Detect rectangular form fields using contour detection"""
        fields = []
        
        try:
            # Apply adaptive threshold
            thresh = cv2.adaptiveThreshold(gray_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                         cv2.THRESH_BINARY_INV, 11, 2)
            
            # Find contours
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            image_height, image_width = gray_image.shape
            
            for i, contour in enumerate(contours):
                x, y, w, h = cv2.boundingRect(contour)
                area = w * h
                aspect_ratio = w / h if h > 0 else 0
                
                # Filter for form field characteristics
                if (2000 < area < 100000 and  # Reasonable size
                    50 < w < image_width * 0.8 and  # Width constraints
                    20 < h < image_height * 0.3 and  # Height constraints
                    1.5 < aspect_ratio < 20):  # Aspect ratio constraints
                    
                    # Check if area is mostly blank
                    roi = gray_image[y:y+h, x:x+w]
                    if roi.size > 0:
                        mean_intensity = np.mean(roi)
                        if mean_intensity > 180:  # Mostly white
                            field_type = self._classify_field_by_context(gray_image, x, y, w, h)
                            
                            field = FormField(
                                id=f"rect_field_{i}_{page_num}",
                                field_type=field_type,
                                x_position=x,
                                y_position=y,
                                width=w,
                                height=h,
                                page_number=page_num,
                                context=field_type,
                                confidence=0.8
                            )
                            fields.append(field)
            
        except Exception as e:
            print(f"Error in rectangular field detection: {e}")
        
        return fields
    
    def _detect_text_based_fields(self, text: str, image_shape: Tuple, page_num: int) -> List[FormField]:
        """Detect fields based on text patterns and underlines/blank spaces"""
        fields = []
        
        try:
            lines = text.split('\n')
            field_id = 0
            
            for i, line in enumerate(lines):
                line_lower = line.lower().strip()
                if not line_lower:
                    continue
                
                # Method 1: Detect underlines and blank spaces
                underline_fields = self._detect_underlines_in_line(line, i, page_num, field_id)
                fields.extend(underline_fields)
                field_id += len(underline_fields)
                
                # Method 2: Detect field patterns
                field_type = self._classify_text_to_field_type(line_lower)
                
                if field_type != 'text':
                    # Estimate position based on line number
                    y_pos = 50 + (i * 30)  # Approximate line height
                    if y_pos > image_shape[0]:
                        y_pos = image_shape[0] - 50
                    
                    field = FormField(
                        id=f"text_field_{field_id}_{page_num}",
                        field_type=field_type,
                        x_position=50,
                        y_position=y_pos,
                        width=400,
                        height=30,
                        page_number=page_num,
                        context=line.strip(),
                        confidence=0.9
                    )
                    fields.append(field)
                    field_id += 1
                    
        except Exception as e:
            print(f"Error in text-based field detection: {e}")
        
        return fields
    
    def _detect_underlines_in_line(self, line: str, line_num: int, page_num: int, start_id: int) -> List[FormField]:
        """Detect underlines and blank spaces in a line of text"""
        fields = []
        field_id = start_id
        
        # Pattern to detect underlines (multiple underscores together)
        underline_pattern = r'_{2,}'  # 2 or more underscores
        
        # Also detect "20__" pattern specifically
        year_pattern = r'20_{1,2}'
        
        # Find all underlines
        for match in re.finditer(underline_pattern, line):
            start_pos = match.start()
            end_pos = match.end()
            underline_length = end_pos - start_pos
            
            # Skip very short underlines (just 2 underscores) unless it's a year pattern
            if underline_length <= 2:
                # Check if it's a year pattern (20__)
                if not (start_pos >= 2 and line[start_pos-2:start_pos] == '20'):
                    continue
            
            # Get context before and after the underline
            context_before = line[max(0, start_pos-40):start_pos].strip()
            context_after = line[end_pos:min(len(line), end_pos+40)].strip()
            
            # For debugging - show what was detected
            underline_text = line[start_pos:end_pos]
            full_context = f"{context_before} [{underline_text}] {context_after}"
            
            # Classify field type based on context
            field_type = self._classify_underline_field(context_before, context_after)
            
            # Calculate field width based on underline length
            field_width = min(max(underline_length * 6, 80), 400)  # Minimum 80px, max 400px
            
            # Adjust field type and width based on underline length and context
            if underline_length <= 4:
                # Very short underline (2-4 chars) - likely year component "20__"
                if 'between 20' in context_before.lower() or context_before.endswith('20'):
                    field_type = 'year'
                    field_width = 50
                elif 'day' in context_before.lower() or 'day of' in context_before.lower():
                    field_type = 'day'
                    field_width = 50
            elif underline_length <= 10:
                # Short-medium underline (5-10 chars) - likely day, month, or short field
                if 'day of' in context_before.lower() or 'the' in context_before.lower() and 'day' in context_after.lower():
                    field_type = 'day'
                    field_width = 80
                elif 'of' in context_before.lower() and ('between' in context_after.lower() or 'between 20' in context_after.lower()):
                    field_type = 'month'
                    field_width = 120
            elif underline_length <= 20:
                # Medium underline (11-20 chars) - likely month, date, or medium text
                if 'day of' in context_before.lower() or 'of' in context_before.lower():
                    field_type = 'month'
                    field_width = 150
            elif underline_length > 20:
                # Long underline - likely name, institution, or ID
                if 'student at the' in context_before.lower() or 'at the' in context_before.lower():
                    field_type = 'institution'
                elif ('and' in context_before.lower() or context_before.endswith('AND')) and 'student' in context_after.lower():
                    field_type = 'name'
                elif 'identification number as' in context_before.lower() or 'id number as' in context_before.lower() or 'number as' in context_before.lower():
                    field_type = 'student_id'
            
            field = FormField(
                id=f"underline_{field_id}_{line_num}_{page_num}",
                field_type=field_type,
                x_position=50 + (start_pos * 6),  # Approximate position
                y_position=50 + (line_num * 30),
                width=field_width,
                height=25,
                page_number=page_num,
                context=full_context[:120],
                confidence=0.90
            )
            fields.append(field)
            field_id += 1
        
        return fields
    
    def _classify_underline_field(self, before: str, after: str) -> str:
        """Classify underline field based on surrounding context"""
        before_lower = before.lower()
        after_lower = after.lower()
        combined = (before + " " + after).lower()
        
        # Check for specific field types based on context
        # Priority: More specific patterns first
        
        # Date components
        if 'day of' in before_lower:
            return 'day'
        elif 'of' in before_lower and 'between' in after_lower:
            return 'month'
        elif 'between 20' in combined or after_lower.startswith('20') or '20' in after_lower[:5]:
            return 'year'
        
        # Student/ID related
        elif 'identification number as' in before_lower or 'id number as' in before_lower:
            return 'student_id'
        elif 'student at the' in before_lower or 'at the' in before_lower:
            return 'institution'
        
        # Name fields
        elif 'and' in before_lower and 'student' in after_lower:
            return 'name'
        elif any(keyword in combined for keyword in ['recipient', 'person', 'full name']):
            return 'name'
        
        # Other fields
        elif any(keyword in combined for keyword in ['address', 'located at', 'street']):
            return 'address'
        elif any(keyword in combined for keyword in ['email', 'e-mail']):
            return 'email'
        elif any(keyword in combined for keyword in ['phone', 'telephone', 'contact']):
            return 'phone'
        else:
            return 'text'
    
    def _detect_line_based_fields(self, gray_image: np.ndarray, page_num: int) -> List[FormField]:
        """Detect fields based on underlines and form lines - enhanced for contracts"""
        fields = []
        
        try:
            # Method 1: Detect horizontal lines (underlines)
            horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
            horizontal_lines = cv2.morphologyEx(gray_image, cv2.MORPH_OPEN, horizontal_kernel)
            
            # Find contours of lines
            contours, _ = cv2.findContours(horizontal_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            field_id = 0
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                
                # Check if this looks like an underline (wide and very thin)
                if w > 30 and h < 10:  # Wide and short
                    # Look for text above and around the line
                    context_region = gray_image[max(0, y-30):min(gray_image.shape[0], y+10), 
                                               max(0, x-50):min(gray_image.shape[1], x+w+50)]
                    if context_region.size > 0:
                        text = pytesseract.image_to_string(context_region).strip()
                        if text or w > 50:  # Accept if has context or is long enough
                            field_type = self._classify_text_to_field_type(text.lower()) if text else 'text'
                            
                            # Further classify based on underline length
                            if w < 80:
                                # Short underline - likely date component or short field
                                if 'day' in text.lower():
                                    field_type = 'day'
                                elif 'month' in text.lower() or ('of' in text.lower() and 'between' in text.lower()):
                                    field_type = 'month'
                                elif '20' in text or 'year' in text.lower():
                                    field_type = 'year'
                            elif w > 150:
                                # Long underline - likely name, address, or institution
                                if 'student at' in text.lower() or 'institution' in text.lower():
                                    field_type = 'institution'
                                elif 'student id' in text.lower() or 'identification' in text.lower():
                                    field_type = 'student_id'
                                elif any(keyword in text.lower() for keyword in ['name', 'recipient', 'and ___']):
                                    field_type = 'name'
                            
                            field = FormField(
                                id=f"line_field_{field_id}_{page_num}",
                                field_type=field_type,
                                x_position=x,
                                y_position=y-5,  # Position slightly above the line
                                width=w,
                                height=25,
                                page_number=page_num,
                                context=text[:100] if text else f"underline_{w}px",
                                confidence=0.8
                            )
                            fields.append(field)
                            field_id += 1
                            
        except Exception as e:
            print(f"Error in line-based field detection: {e}")
        
        return fields
    
    def _detect_blank_spaces(self, gray_image: np.ndarray, page_num: int) -> List[FormField]:
        """Detect blank spaces that could be form fields"""
        fields = []
        
        try:
            # Apply threshold to find white regions
            _, thresh = cv2.threshold(gray_image, 200, 255, cv2.THRESH_BINARY)
            
            # Find contours of white regions
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            image_height, image_width = gray_image.shape
            field_id = 0
            
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                area = w * h
                
                # Filter for reasonable blank spaces
                if (5000 < area < 50000 and  # Reasonable size
                    80 < w < image_width * 0.6 and  # Width constraints
                    25 < h < image_height * 0.2):  # Height constraints
                    
                    # Check if this is a blank space
                    roi = gray_image[y:y+h, x:x+w]
                    if roi.size > 0:
                        mean_intensity = np.mean(roi)
                        if mean_intensity > 190:  # Very white
                            field = FormField(
                                id=f"blank_field_{field_id}_{page_num}",
                                field_type='text',
                                x_position=x,
                                y_position=y,
                                width=w,
                                height=h,
                                page_number=page_num,
                                context='blank_space',
                                confidence=0.6
                            )
                            fields.append(field)
                            field_id += 1
                            
        except Exception as e:
            print(f"Error in blank space detection: {e}")
        
        return fields
    
    def _classify_field_by_context(self, gray_image: np.ndarray, x: int, y: int, w: int, h: int) -> str:
        """Classify field type based on surrounding context"""
        try:
            # Extract text around the field
            context_region = gray_image[max(0, y-30):min(gray_image.shape[0], y+h+30), 
                                      max(0, x-100):min(gray_image.shape[1], x+w+100)]
            
            if context_region.size > 0:
                context_text = pytesseract.image_to_string(context_region).lower()
                return self._classify_text_to_field_type(context_text)
            
        except Exception as e:
            print(f"Error classifying field context: {e}")
        
        return 'text'
    
    def _classify_text_to_field_type(self, text: str) -> str:
        """Classify text to field type using pattern matching"""
        for field_type, patterns in self.field_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return field_type
        return 'text'
    
    def _extract_acroform_fields(self, doc, page_num: int) -> List[FormField]:
        """Extract AcroForm fields from PDF - more selective"""
        fields = []
        
        try:
            # Get form fields from the document
            for field in list(doc[page_num].widgets()):  # Convert generator to list
                field_type = 'text'  # Default
                
                # Determine field type based on field properties
                if hasattr(field, 'field_type'):
                    if field.field_type == 1:  # Text field
                        field_type = 'text'
                    elif field.field_type == 2:  # Checkbox
                        field_type = 'checkbox'
                    elif field.field_type == 3:  # Radio button
                        field_type = 'radio'
                    elif field.field_type == 4:  # Combo box
                        field_type = 'dropdown'
                    elif field.field_type == 5:  # List box
                        field_type = 'dropdown'
                
                # Get field position and size
                rect = field.rect
                x = int(rect.x0)
                y = int(rect.y0)
                width = int(rect.x1 - rect.x0)
                height = int(rect.y1 - rect.y0)
                
                # Skip fields that are too small or too large (likely not actual form fields)
                if width < 10 or height < 10 or width > 1000 or height > 100:
                    continue
                
                # Get field name/label
                field_name = getattr(field, 'field_name', '') or getattr(field, 'field_label', '') or 'field'
                
                # Skip fields with generic or empty names
                if not field_name or field_name.lower() in ['field', 'text', '']:
                    continue
                
                field = FormField(
                    id=f"acroform_{field_name}_{page_num}",
                    field_type=field_type,
                    x_position=x,
                    y_position=y,
                    width=width,
                    height=height,
                    page_number=page_num,
                    context=field_name,
                    confidence=0.95
                )
                fields.append(field)
                
        except Exception as e:
            print(f"Error extracting AcroForm fields: {e}")
        
        return fields
    
    def _detect_text_pattern_fields(self, text: str, page_num: int) -> List[FormField]:
        """Detect fields based on text patterns and layout analysis - more selective"""
        fields = []
        
        try:
            lines = text.split('\n')
            field_id = 0
            
            # More specific patterns for actual fillable fields
            fillable_patterns = {
                'name': [
                    r'please\s+enter\s+your\s+name'
                ],
                'dropdown': [
                    r'please\s+select\s+an?\s+item\s+from\s+the\s+combo'
                ],
                'checkbox': [
                    r'check\s+all\s+that\s+apply'
                ],
                'table_field': [
                    r'name\s+of\s+dependent', r'age\s+of\s+dependent'
                ]
            }
            
            # Only process lines that clearly indicate fillable fields
            for i, line in enumerate(lines):
                line_lower = line.lower().strip()
                if not line_lower:
                    continue
                
                # Check for specific fillable field patterns only
                field_type = None
                for ftype, patterns in fillable_patterns.items():
                    for pattern in patterns:
                        if re.search(pattern, line_lower, re.IGNORECASE):
                            field_type = ftype
                            break
                    if field_type:
                        break
                
                # Special handling for option checkboxes (only if they follow "check all that apply")
                if 'option' in line_lower and any(char in line_lower for char in ['1', '2', '3']):
                    # Check if there's a "check all that apply" instruction above
                    has_check_instruction = False
                    for j in range(max(0, i-3), i):
                        if j < len(lines) and 'check all that apply' in lines[j].lower():
                            has_check_instruction = True
                            break
                    
                    if has_check_instruction:
                        field_type = 'checkbox'
                
                # Only create fields for actual fillable areas
                if field_type:
                    # Estimate position based on line number and content
                    y_pos = 50 + (i * 35)  # Approximate line height
                    
                    # Adjust field type and size based on context
                    if field_type == 'checkbox':
                        width, height = 20, 20
                    elif field_type == 'table_field':
                        field_type = 'text'  # Table fields are text inputs
                        width, height = 200, 25
                    else:
                        width, height = 300, 30
                    
                    field = FormField(
                        id=f"pattern_field_{field_id}_{page_num}",
                        field_type=field_type,
                        x_position=50,
                        y_position=y_pos,
                        width=width,
                        height=height,
                        page_number=page_num,
                        context=line.strip(),
                        confidence=0.9  # Higher confidence for specific patterns
                    )
                    fields.append(field)
                    field_id += 1
                    
        except Exception as e:
            print(f"Error in text pattern field detection: {e}")
        
        return fields
    
    def _create_virtual_fields_from_text(self, text: str) -> List[FormField]:
        """Create virtual fields from text patterns"""
        fields = []
        lines = text.split('\n')
        field_id = 0
        
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            if not line_lower:
                continue
            
            field_type = self._classify_text_to_field_type(line_lower)
            if field_type != 'text':
                field = FormField(
                    id=f"virtual_field_{field_id}",
                    field_type=field_type,
                    x_position=50,
                    y_position=100 + (field_id * 60),
                    width=400,
                    height=40,
                    page_number=0,
                    context=line.strip(),
                    confidence=0.8
                )
                fields.append(field)
                field_id += 1
        
        return fields
    
    def _merge_and_deduplicate_fields(self, fields: List[FormField]) -> List[FormField]:
        """Merge and deduplicate overlapping fields with improved logic"""
        if not fields:
            return []
        
        # Sort by confidence (highest first)
        fields.sort(key=lambda x: x.confidence, reverse=True)
        
        merged_fields = []
        for field in fields:
            # Skip fields that are too small or have low confidence
            if field.width < 20 or field.height < 15 or field.confidence < 0.5:
                continue
                
            # Skip fields that are just text labels without actual input areas
            if (field.field_type == 'text' and 
                field.context and 
                any(keyword in field.context.lower() for keyword in ['please', 'select', 'check', 'enter', 'name of', 'age of']) and
                field.width < 100):
                continue
            
            # Skip generic text fields with no meaningful context
            if (field.field_type == 'text' and 
                field.context and 
                field.context.lower().strip() in ['text', 'field', '']):
                continue
            
            # Skip very large text fields that are likely not form inputs
            if field.field_type == 'text' and field.width > 500:
                continue
            
            # Check if this field overlaps with any existing field
            overlaps = False
            for existing_field in merged_fields:
                if self._fields_overlap(field, existing_field):
                    # If overlapping, keep the one with higher confidence or better type
                    if (field.confidence > existing_field.confidence or 
                        (field.field_type in ['checkbox', 'radio', 'dropdown'] and existing_field.field_type == 'text')):
                        # Replace the existing field
                        merged_fields.remove(existing_field)
                        merged_fields.append(field)
                    overlaps = True
                    break
            
            if not overlaps:
                merged_fields.append(field)
        
        # Filter out duplicate context fields
        context_seen = set()
        final_fields = []
        for field in merged_fields:
            context_key = field.context.lower().strip()
            if context_key not in context_seen or field.field_type in ['checkbox', 'radio', 'dropdown']:
                context_seen.add(context_key)
                final_fields.append(field)
        
        return final_fields
    
    def _fields_overlap(self, field1: FormField, field2: FormField) -> bool:
        """Check if two fields overlap significantly"""
        # Calculate overlap area
        x1 = max(field1.x_position, field2.x_position)
        y1 = max(field1.y_position, field2.y_position)
        x2 = min(field1.x_position + field1.width, field2.x_position + field2.width)
        y2 = min(field1.y_position + field1.height, field2.y_position + field2.height)
        
        if x1 < x2 and y1 < y2:
            overlap_area = (x2 - x1) * (y2 - y1)
            field1_area = field1.width * field1.height
            field2_area = field2.width * field2.height
            
            # If overlap is more than 30% of either field, consider them overlapping
            return (overlap_area > 0.3 * field1_area) or (overlap_area > 0.3 * field2_area)
        
        return False

def convert_form_fields_to_dict(fields: List[FormField]) -> List[Dict]:
    """Convert FormField objects to dictionary format for API compatibility"""
    return [
        {
            'id': field.id,
            'field_type': field.field_type,
            'x_position': field.x_position,
            'y_position': field.y_position,
            'width': field.width,
            'height': field.height,
            'page_number': field.page_number,
            'page': field.page_number,  # Alias for compatibility with create_filled_pdf
            'context': field.context,
            'initial_content': field.initial_content,
            'confidence': field.confidence,
            'options': field.options,
            # Legacy compatibility
            'x': field.x_position,
            'y': field.y_position,
            'area': field.width * field.height
        }
        for field in fields
    ]
