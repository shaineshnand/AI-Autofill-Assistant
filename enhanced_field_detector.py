#!/usr/bin/env python
"""
Enhanced Field Detector for AI Autofill Assistant
Comprehensive field detection with improved algorithms and better accuracy
"""
import os
import cv2
import numpy as np
import pytesseract
import fitz  # PyMuPDF
import re
from typing import List, Dict, Tuple, Optional, Union
from dataclasses import dataclass
from PIL import Image, ImageDraw, ImageFont
import json
import math

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
    detection_method: str = "unknown"  # Track how field was detected

class EnhancedFieldDetector:
    """Enhanced field detection with comprehensive algorithms"""
    
    def __init__(self):
        # Configure Tesseract path for Windows
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        
        # Enhanced field detection patterns
        self.field_patterns = {
            'name': [
                r'name\s*[:.]?\s*$', r'full\s+name', r'first\s+name', r'last\s+name',
                r'enter\s+your\s+name', r'your\s+name', r'applicant\s+name',
                r'given\s+name', r'surname', r'family\s+name'
            ],
            'email': [
                r'email\s*[:.]?\s*$', r'e-mail\s*[:.]?\s*$', r'email\s+address',
                r'enter\s+email', r'your\s+email', r'contact\s+email',
                r'electronic\s+mail', r'@\s*required'
            ],
            'phone': [
                r'phone\s*[:.]?\s*$', r'telephone\s*[:.]?\s*$', r'phone\s+number',
                r'mobile\s*[:.]?\s*$', r'cell\s+phone', r'contact\s+number',
                r'telephone\s+number', r'phone\s+no', r'tel\s*[:.]?\s*$'
            ],
            'address': [
                r'address\s*[:.]?\s*$', r'street\s+address', r'home\s+address',
                r'residence\s+address', r'postal\s+address', r'mailing\s+address',
                r'location', r'where\s+do\s+you\s+live'
            ],
            'date': [
                r'date\s*[:.]?\s*$', r'birth\s+date', r'date\s+of\s+birth',
                r'dob\s*[:.]?\s*$', r'application\s+date', r'signature\s+date',
                r'today\'?s?\s+date', r'current\s+date'
            ],
            'age': [
                r'age\s*[:.]?\s*$', r'years\s+old', r'your\s+age',
                r'how\s+old\s+are\s+you', r'age\s+in\s+years'
            ],
            'signature': [
                r'signature\s*[:.]?\s*$', r'sign\s*[:.]?\s*$', r'initial\s*[:.]?\s*$',
                r'your\s+signature', r'digital\s+signature', r'signed\s+by'
            ],
            'id_number': [
                r'id\s+number', r'identification\s+number', r'social\s+security',
                r'passport\s+number', r'driver\'?s?\s+license', r'employee\s+id',
                r'reference\s+number', r'account\s+number'
            ],
            'checkbox': [
                r'check\s+all\s+that\s+apply', r'select\s+all\s+applicable',
                r'please\s+check', r'option\s+\d+', r'yes\s+no\s+question'
            ],
            'dropdown': [
                r'select\s+from\s+list', r'choose\s+from\s+options',
                r'please\s+select', r'dropdown\s+menu'
            ]
        }
        
        # Common form field indicators
        self.field_indicators = [
            ':', ':', '___', '____', '_____',  # Colons and underlines
            'please enter', 'please fill', 'required', 'optional',
            'enter your', 'fill in', 'provide'
        ]

    def process_document(self, file_path: str) -> Dict:
        """Process document and detect form fields with enhanced algorithms"""
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.pdf':
                return self._process_pdf_enhanced(file_path)
            elif file_ext in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp']:
                return self._process_image_enhanced(file_path)
            elif file_ext in ['.doc', '.docx']:
                return self._process_word_enhanced(file_path)
            elif file_ext in ['.txt', '.rtf']:
                return self._process_text_enhanced(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")
                
        except Exception as e:
            print(f"Error processing document: {e}")
            import traceback
            traceback.print_exc()
            return {
                'extracted_text': '',
                'fields': [],
                'total_fields': 0,
                'error': str(e)
            }

    def _process_pdf_enhanced(self, file_path: str) -> Dict:
        """Enhanced PDF processing with comprehensive field detection"""
        try:
            doc = fitz.open(file_path)
            all_fields = []
            extracted_text = ""
            
            print(f"Processing PDF with {len(doc)} pages")
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                print(f"  Processing page {page_num + 1}")
                
                # Extract text from page
                page_text = page.get_text()
                extracted_text += f"--- Page {page_num + 1} ---\n{page_text}\n"
                
                # Method 1: AcroForm fields (native PDF form fields)
                acroform_fields = self._extract_acroform_fields(doc, page_num)
                all_fields.extend(acroform_fields)
                print(f"    Found {len(acroform_fields)} AcroForm fields")
                
                # SMART DETECTION: If AcroForm fields exist, ONLY use those (skip visual detection)
                # AcroForm = real PDF form fields, visual detection often creates false positives
                if len(acroform_fields) > 0:
                    print(f"    ✓ AcroForm fields detected - skipping visual/text detection (smart mode)")
                    continue  # Skip to next page, don't run visual detection
                
                # Only run visual/text detection if NO AcroForm fields found
                print(f"    No AcroForm fields - running visual detection")
                
                # Method 2: Convert page to high-quality image
                mat = fitz.Matrix(3.0, 3.0)  # Higher resolution for better detection
                pix = page.get_pixmap(matrix=mat)
                img_data = pix.tobytes("png")
                
                # Convert to OpenCV format
                nparr = np.frombuffer(img_data, np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                
                # Method 3: Enhanced visual field detection
                visual_fields = self._detect_fields_visual_enhanced(gray, page_text, page_num)
                all_fields.extend(visual_fields)
                print(f"    Found {len(visual_fields)} visual fields")
                
                # Method 4: Text pattern analysis
                text_fields = self._detect_text_pattern_fields_enhanced(page_text, page_num)
                all_fields.extend(text_fields)
                print(f"    Found {len(text_fields)} text pattern fields")
                
                # Method 5: Layout analysis
                layout_fields = self._analyze_layout_fields(gray, page_text, page_num)
                all_fields.extend(layout_fields)
                print(f"    Found {len(layout_fields)} layout fields")
            
            # Comprehensive deduplication and merging
            all_fields = self._merge_and_deduplicate_enhanced(all_fields)
            
            doc.close()
            
            print(f"Total fields found: {len(all_fields)}")
            
            return {
                'extracted_text': extracted_text.strip(),
                'fields': all_fields,
                'total_fields': len(all_fields),
                'document_type': 'pdf'
            }
            
        except Exception as e:
            print(f"Error processing PDF: {e}")
            import traceback
            traceback.print_exc()
            return {'extracted_text': '', 'fields': [], 'total_fields': 0, 'error': str(e)}

    def _process_image_enhanced(self, file_path: str) -> Dict:
        """Enhanced image processing"""
        try:
            # Load image
            image = cv2.imread(file_path)
            if image is None:
                raise ValueError(f"Could not load image: {file_path}")
            
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Extract text using OCR
            extracted_text = pytesseract.image_to_string(gray, config='--psm 6')
            
            # Enhanced field detection
            fields = self._detect_fields_visual_enhanced(gray, extracted_text, 0)
            
            return {
                'extracted_text': extracted_text,
                'fields': fields,
                'total_fields': len(fields),
                'document_type': 'image'
            }
            
        except Exception as e:
            print(f"Error processing image: {e}")
            return {'extracted_text': '', 'fields': [], 'total_fields': 0, 'error': str(e)}

    def _detect_fields_visual_enhanced(self, gray_image: np.ndarray, text: str, page_num: int) -> List[FormField]:
        """Enhanced visual field detection using multiple algorithms"""
        fields = []
        
        # Method 1: Enhanced rectangular field detection
        rectangular_fields = self._detect_rectangular_fields_enhanced(gray_image, page_num)
        fields.extend(rectangular_fields)
        
        # Method 2: Underline and line detection
        line_fields = self._detect_underline_fields(gray_image, page_num)
        fields.extend(line_fields)
        
        # Method 3: Box detection
        box_fields = self._detect_box_fields(gray_image, page_num)
        fields.extend(box_fields)
        
        # Method 4: White space detection
        whitespace_fields = self._detect_whitespace_fields(gray_image, page_num)
        fields.extend(whitespace_fields)
        
        # Method 5: Text-based field positioning
        text_positioned_fields = self._detect_text_positioned_fields(gray_image, text, page_num)
        fields.extend(text_positioned_fields)
        
        return fields

    def _detect_rectangular_fields_enhanced(self, gray_image: np.ndarray, page_num: int) -> List[FormField]:
        """Enhanced rectangular field detection with better filtering"""
        fields = []
        
        try:
            # Multiple thresholding approaches
            methods = [
                ('adaptive_gaussian', cv2.adaptiveThreshold(gray_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)),
                ('adaptive_mean', cv2.adaptiveThreshold(gray_image, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 11, 2)),
                ('otsu', cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]),
                ('simple', cv2.threshold(gray_image, 127, 255, cv2.THRESH_BINARY_INV)[1])
            ]
            
            image_height, image_width = gray_image.shape
            
            for method_name, thresh in methods:
                # Find contours
                contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                for i, contour in enumerate(contours):
                    x, y, w, h = cv2.boundingRect(contour)
                    area = w * h
                    aspect_ratio = w / h if h > 0 else 0
                    
                    # Enhanced filtering criteria
                    if self._is_valid_form_field(x, y, w, h, area, aspect_ratio, image_width, image_height):
                        # Check if area is mostly blank (form field characteristic)
                        roi = gray_image[y:y+h, x:x+w]
                        if roi.size > 0:
                            mean_intensity = np.mean(roi)
                            std_intensity = np.std(roi)
                            
                            # Form fields are typically mostly white with low variation
                            if mean_intensity > 200 and std_intensity < 50:
                                # Additional check: ensure no text content
                                dark_pixels = np.sum(roi < 100)
                                total_pixels = roi.size
                                dark_ratio = dark_pixels / total_pixels
                                
                                # Only accept if very few dark pixels (mostly blank)
                                if dark_ratio < 0.05:  # Less than 5% dark pixels
                                    field_type = self._classify_field_by_position(gray_image, x, y, w, h)
                                
                                field = FormField(
                                    id=f"rect_{method_name}_p{page_num}_{i}",
                                    field_type=field_type,
                                    x_position=x,
                                    y_position=y,
                                    width=w,
                                    height=h,
                                    page_number=page_num,
                                    context=field_type,
                                    confidence=0.8,
                                    detection_method=f"rectangular_{method_name}"
                                )
                                fields.append(field)
            
            return fields
            
        except Exception as e:
            print(f"Error in enhanced rectangular field detection: {e}")
            return []

    def _detect_underline_fields(self, gray_image: np.ndarray, page_num: int) -> List[FormField]:
        """Detect fields with underlines (common in forms)"""
        fields = []
        
        try:
            # Detect horizontal lines (underlines)
            horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (50, 1))
            horizontal_lines = cv2.morphologyEx(gray_image, cv2.MORPH_OPEN, horizontal_kernel)
            
            # Find contours of horizontal lines
            contours, _ = cv2.findContours(horizontal_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for i, contour in enumerate(contours):
                x, y, w, h = cv2.boundingRect(contour)
                
                # Look for text above the line
                text_region = gray_image[max(0, y-50):y, x:x+w]
                if text_region.size > 0:
                    # Use OCR to detect text above the line
                    try:
                        text = pytesseract.image_to_string(text_region, config='--psm 8').strip()
                        
                        if text and len(text) > 2:
                            field_type = self._classify_text_to_field_type(text)
                            
                            # Estimate field dimensions
                            field_height = min(30, h * 2)
                            field_width = max(w, 150)
                            
                            field = FormField(
                                id=f"underline_p{page_num}_{i}",
                                field_type=field_type,
                                x_position=x,
                                y_position=y - field_height,
                                width=field_width,
                                height=field_height,
                                page_number=page_num,
                                context=text.lower(),
                                confidence=0.9,
                                detection_method="underline"
                            )
                            fields.append(field)
                    except:
                        continue
            
            return fields
            
        except Exception as e:
            print(f"Error detecting underline fields: {e}")
            return []

    def _detect_box_fields(self, gray_image: np.ndarray, page_num: int) -> List[FormField]:
        """Detect fields that are in boxes or rectangles"""
        fields = []
        
        try:
            # Detect rectangular shapes
            edges = cv2.Canny(gray_image, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            image_height, image_width = gray_image.shape
            
            for i, contour in enumerate(contours):
                # Approximate the contour to a polygon
                epsilon = 0.02 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                
                # Check if it's roughly rectangular (4 corners)
                if len(approx) >= 4:
                    x, y, w, h = cv2.boundingRect(contour)
                    area = w * h
                    aspect_ratio = w / h if h > 0 else 0
                    
                    # Filter for reasonable form field sizes
                    if (500 < area < 50000 and 
                        20 < w < image_width * 0.8 and 
                        15 < h < image_height * 0.3 and
                        1.2 < aspect_ratio < 15):
                        
                        # Check if it's mostly white (form field)
                        roi = gray_image[y:y+h, x:x+w]
                        if roi.size > 0:
                            mean_intensity = np.mean(roi)
                            if mean_intensity > 180:
                                field_type = self._classify_field_by_position(gray_image, x, y, w, h, "")
                                
                                field = FormField(
                                    id=f"box_p{page_num}_{i}",
                                    field_type=field_type,
                                    x_position=x,
                                    y_position=y,
                                    width=w,
                                    height=h,
                                    page_number=page_num,
                                    context=field_type,
                                    confidence=0.7,
                                    detection_method="box"
                                )
                                fields.append(field)
            
            return fields
            
        except Exception as e:
            print(f"Error detecting box fields: {e}")
            return []

    def _detect_whitespace_fields(self, gray_image: np.ndarray, page_num: int) -> List[FormField]:
        """Detect large white spaces that could be form fields"""
        fields = []
        
        try:
            # Find large white regions
            _, white_mask = cv2.threshold(gray_image, 240, 255, cv2.THRESH_BINARY)
            
            # Remove noise
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
            white_mask = cv2.morphologyEx(white_mask, cv2.MORPH_CLOSE, kernel)
            
            contours, _ = cv2.findContours(white_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            image_height, image_width = gray_image.shape
            
            for i, contour in enumerate(contours):
                x, y, w, h = cv2.boundingRect(contour)
                area = w * h
                aspect_ratio = w / h if h > 0 else 0
                
                # Look for reasonably sized white spaces
                if (2000 < area < 20000 and 
                    50 < w < image_width * 0.7 and 
                    20 < h < image_height * 0.25 and
                    2 < aspect_ratio < 20):
                    
                    # Check surrounding area for text (field labels)
                    context_text = self._extract_context_text(gray_image, x, y, w, h)
                    if context_text:
                        field_type = self._classify_text_to_field_type(context_text)
                        
                        field = FormField(
                            id=f"whitespace_p{page_num}_{i}",
                            field_type=field_type,
                            x_position=x,
                            y_position=y,
                            width=w,
                            height=h,
                            page_number=page_num,
                            context=context_text.lower(),
                            confidence=0.6,
                            detection_method="whitespace"
                        )
                        fields.append(field)
            
            return fields
            
        except Exception as e:
            print(f"Error detecting whitespace fields: {e}")
            return []

    def _detect_text_positioned_fields(self, gray_image: np.ndarray, text: str, page_num: int) -> List[FormField]:
        """Detect fields based on text patterns and positioning"""
        fields = []
        
        try:
            # Get text with bounding boxes using OCR
            ocr_data = pytesseract.image_to_data(gray_image, output_type=pytesseract.Output.DICT)
            
            image_height, image_width = gray_image.shape
            
            # Look for field indicators in text
            for i in range(len(ocr_data['text'])):
                detected_text = ocr_data['text'][i].strip().lower()
                conf = int(ocr_data['conf'][i])
                
                if conf > 30 and detected_text:
                    # Check if this text indicates a form field
                    field_type = self._classify_text_to_field_type(detected_text)
                    
                    if field_type != 'text' or any(indicator in detected_text for indicator in self.field_indicators):
                        # Get text position
                        text_x = ocr_data['left'][i]
                        text_y = ocr_data['top'][i]
                        text_w = ocr_data['width'][i]
                        text_h = ocr_data['height'][i]
                        
                        # Estimate field position (usually to the right or below)
                        field_x = text_x + text_w + 10
                        field_y = text_y
                        field_w = max(150, text_w * 2)
                        field_h = max(25, text_h)
                        
                        # Adjust if field would go off page
                        if field_x + field_w > image_width:
                            field_x = text_x
                            field_y = text_y + text_h + 5
                        
                        # Validate that the estimated field area is actually blank
                        if self._is_area_blank(gray_image, field_x, field_y, field_w, field_h):
                            field = FormField(
                                id=f"text_positioned_p{page_num}_{i}",
                                field_type=field_type,
                                x_position=field_x,
                                y_position=field_y,
                                width=field_w,
                                height=field_h,
                                page_number=page_num,
                                context=detected_text,
                                confidence=0.85,
                                detection_method="text_positioned"
                            )
                            fields.append(field)
            
            return fields
            
        except Exception as e:
            print(f"Error detecting text positioned fields: {e}")
            return []

    def _is_valid_form_field(self, x: int, y: int, w: int, h: int, area: int, 
                           aspect_ratio: float, image_width: int, image_height: int) -> bool:
        """Enhanced validation for form field candidates"""
        # Size constraints
        if not (1000 < area < 100000):
            return False
        
        # Dimension constraints
        if not (30 < w < image_width * 0.8):
            return False
        if not (15 < h < image_height * 0.3):
            return False
        
        # Aspect ratio constraints (form fields are usually wider than tall)
        if not (1.5 < aspect_ratio < 25):
            return False
        
        # Position constraints (not too close to edges)
        if x < 10 or y < 10:
            return False
        if x + w > image_width - 10 or y + h > image_height - 10:
            return False
        
        return True

    def _classify_field_by_position(self, gray_image: np.ndarray, x: int, y: int, w: int, h: int, text: str) -> str:
        """Classify field type based on position and context"""
        try:
            # Extract text around the field
            context_region = gray_image[max(0, y-30):min(gray_image.shape[0], y+h+30), 
                                      max(0, x-100):min(gray_image.shape[1], x+w+100)]
            
            if context_region.size > 0:
                context_text = pytesseract.image_to_string(context_region).lower()
                return self._classify_text_to_field_type(context_text)
            
            return 'text'
            
        except Exception as e:
            return 'text'

    def _is_area_blank(self, gray_image: np.ndarray, x: int, y: int, w: int, h: int) -> bool:
        """Check if an area in the image is mostly blank (suitable for form field)"""
        try:
            # Ensure coordinates are within image bounds
            x = max(0, min(x, gray_image.shape[1] - 1))
            y = max(0, min(y, gray_image.shape[0] - 1))
            w = min(w, gray_image.shape[1] - x)
            h = min(h, gray_image.shape[0] - y)
            
            if w <= 0 or h <= 0:
                return False
            
            # Extract the region of interest
            roi = gray_image[y:y+h, x:x+w]
            
            if roi.size == 0:
                return False
            
            # Check if area is mostly white/blank
            mean_intensity = np.mean(roi)
            std_intensity = np.std(roi)
            
            # Count dark pixels (potential text)
            dark_pixels = np.sum(roi < 100)
            total_pixels = roi.size
            dark_ratio = dark_pixels / total_pixels
            
            # Area is considered blank if:
            # 1. High average intensity (bright)
            # 2. Low standard deviation (uniform)
            # 3. Few dark pixels (not much text)
            return (mean_intensity > 200 and 
                   std_intensity < 40 and 
                   dark_ratio < 0.1)  # Less than 10% dark pixels
            
        except Exception as e:
            print(f"Error checking if area is blank: {e}")
            return False

    def _classify_text_to_field_type(self, text: str) -> str:
        """Enhanced field type classification based on text patterns"""
        text_lower = text.lower().strip()
        
        # Check against all field patterns
        for field_type, patterns in self.field_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    return field_type
        
        # Check for field indicators
        if any(indicator in text_lower for indicator in self.field_indicators):
            return 'text'
        
        return 'text'

    def _extract_context_text(self, gray_image: np.ndarray, x: int, y: int, w: int, h: int) -> str:
        """Extract text context around a potential field"""
        try:
            # Look for text in a larger area around the field
            context_region = gray_image[max(0, y-40):min(gray_image.shape[0], y+h+40), 
                                      max(0, x-200):min(gray_image.shape[1], x+w+200)]
            
            if context_region.size > 0:
                return pytesseract.image_to_string(context_region, config='--psm 6').strip()
            
            return ""
            
        except Exception as e:
            return ""

    def _extract_acroform_fields(self, doc, page_num: int) -> List[FormField]:
        """Extract native PDF form fields (AcroForm)"""
        fields = []
        
        try:
            page = doc[page_num]
            form_fields = list(page.widgets())  # Convert generator to list
            
            for i, field in enumerate(form_fields):
                rect = field.rect
                field_type = self._classify_pdf_field_type(field)
                
                # Skip very small or very large fields
                if rect.width < 10 or rect.height < 10 or rect.width > 1000 or rect.height > 100:
                    continue
                
                form_field = FormField(
                    id=f"acroform_{field.field_name or f'field_{i}'}_{page_num}",
                    field_type=field_type,
                    x_position=int(rect.x0),
                    y_position=int(rect.y0),
                    width=int(rect.width),
                    height=int(rect.height),
                    page_number=page_num,
                    context=field.field_name or field_type,
                    confidence=0.95,
                    detection_method="acroform"
                )
                fields.append(form_field)
                
        except Exception as e:
            print(f"Error extracting AcroForm fields: {e}")
        
        return fields

    def _classify_pdf_field_type(self, field) -> str:
        """Classify PDF field type based on field properties"""
        field_type = field.field_type_string.lower()
        
        if field_type == 'text':
            field_name = (field.field_name or "").lower()
            
            if any(keyword in field_name for keyword in ['email', 'e-mail']):
                return 'email'
            elif any(keyword in field_name for keyword in ['phone', 'tel', 'mobile']):
                return 'phone'
            elif any(keyword in field_name for keyword in ['name', 'first', 'last']):
                return 'name'
            elif any(keyword in field_name for keyword in ['address', 'street']):
                return 'address'
            elif any(keyword in field_name for keyword in ['date', 'birth', 'dob']):
                return 'date'
            elif any(keyword in field_name for keyword in ['age', 'years']):
                return 'age'
            else:
                return 'text'
        elif field_type == 'checkbox':
            return 'checkbox'
        elif field_type in ['combobox', 'listbox']:
            return 'dropdown'
        elif field_type == 'signature':
            return 'signature'
        else:
            return field_type

    def _detect_text_pattern_fields_enhanced(self, text: str, page_num: int) -> List[FormField]:
        """Enhanced text pattern field detection"""
        fields = []
        
        try:
            lines = text.split('\n')
            
            for i, line in enumerate(lines):
                line_lower = line.lower().strip()
                if not line_lower:
                    continue
                
                # Check for field patterns
                field_type = self._classify_text_to_field_type(line_lower)
                
                if field_type != 'text' or any(indicator in line_lower for indicator in self.field_indicators):
                    # Create virtual field based on line position
                    y_pos = 50 + (i * 40)  # Approximate positioning
                    
                    # Determine field dimensions based on type
                    if field_type == 'checkbox':
                        field_w, field_h = 20, 20
                    elif field_type == 'signature':
                        field_w, field_h = 300, 50
                    else:
                        field_w, field_h = 250, 30
                    
                    field = FormField(
                        id=f"text_pattern_p{page_num}_{i}",
                        field_type=field_type,
                        x_position=200,  # Default position
                        y_position=y_pos,
                        width=field_w,
                        height=field_h,
                        page_number=page_num,
                        context=line_lower,
                        confidence=0.7,
                        detection_method="text_pattern"
                    )
                    fields.append(field)
            
            return fields
            
        except Exception as e:
            print(f"Error in text pattern field detection: {e}")
            return []

    def _analyze_layout_fields(self, gray_image: np.ndarray, text: str, page_num: int) -> List[FormField]:
        """Analyze document layout to find potential fields"""
        fields = []
        
        try:
            # This is a placeholder for advanced layout analysis
            # Could include table detection, column analysis, etc.
            return fields
            
        except Exception as e:
            print(f"Error in layout analysis: {e}")
            return []

    def _merge_and_deduplicate_enhanced(self, fields: List[FormField]) -> List[FormField]:
        """Enhanced field merging and deduplication"""
        if not fields:
            return []
        
        # Sort by confidence (highest first)
        fields.sort(key=lambda f: f.confidence, reverse=True)
        
        unique_fields = []
        
        for field in fields:
            is_duplicate = False
            
            for existing_field in unique_fields:
                # Check for overlap
                if self._fields_overlap_enhanced(field, existing_field):
                    # If new field has higher confidence, replace existing
                    if field.confidence > existing_field.confidence:
                        unique_fields.remove(existing_field)
                        unique_fields.append(field)
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_fields.append(field)
        
        return unique_fields

    def _fields_overlap_enhanced(self, field1: FormField, field2: FormField, threshold: float = 0.3) -> bool:
        """Enhanced field overlap detection"""
        # Calculate intersection area
        x1 = max(field1.x_position, field2.x_position)
        y1 = max(field1.y_position, field2.y_position)
        x2 = min(field1.x_position + field1.width, field2.x_position + field2.width)
        y2 = min(field1.y_position + field1.height, field2.y_position + field2.height)
        
        if x1 < x2 and y1 < y2:
            intersection_area = (x2 - x1) * (y2 - y1)
            field1_area = field1.width * field1.height
            field2_area = field2.width * field2.height
            
            # Calculate overlap ratio
            overlap_ratio = intersection_area / min(field1_area, field2_area)
            return overlap_ratio > threshold
        
        return False

    def _process_word_enhanced(self, file_path: str) -> Dict:
        """Enhanced Word document processing"""
        try:
            from docx import Document
            
            doc = Document(file_path)
            text_content = []
            
            for paragraph in doc.paragraphs:
                text_content.append(paragraph.text)
            
            extracted_text = '\n'.join(text_content)
            
            # Detect form fields in Word document
            fields = self._detect_text_pattern_fields_enhanced(extracted_text, 0)
            
            return {
                'extracted_text': extracted_text,
                'fields': fields,
                'total_fields': len(fields),
                'document_type': 'word'
            }
            
        except Exception as e:
            print(f"Error processing Word document: {e}")
            return {'extracted_text': '', 'fields': [], 'total_fields': 0, 'error': str(e)}

    def _process_text_enhanced(self, file_path: str) -> Dict:
        """Enhanced text file processing"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Detect form fields in text
            fields = self._detect_text_pattern_fields_enhanced(content, 0)
            
            return {
                'extracted_text': content,
                'fields': fields,
                'total_fields': len(fields),
                'document_type': 'text'
            }
            
        except Exception as e:
            print(f"Error processing text document: {e}")
            return {'extracted_text': '', 'fields': [], 'total_fields': 0, 'error': str(e)}

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
            'page': field.page_number,  # Alias for compatibility
            'context': field.context,
            'initial_content': field.initial_content,
            'confidence': field.confidence,
            'options': field.options,
            'detection_method': field.detection_method,
            # Legacy compatibility
            'x': field.x_position,
            'y': field.y_position,
            'area': field.width * field.height
        }
        for field in fields
    ]
