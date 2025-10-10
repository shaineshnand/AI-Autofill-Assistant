#!/usr/bin/env python
"""
Simplified Enhanced Document Processor for AI Autofill Assistant
Provides basic field detection without complex dependencies
"""
import os
import cv2
import numpy as np
import pytesseract
import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from PIL import Image
import json
import random

@dataclass
class FormField:
    """Represents a form field with precise positioning and metadata"""
    id: str
    field_type: str
    x: int
    y: int
    width: int
    height: int
    context: str
    confidence: float
    is_required: bool = False
    placeholder: str = ""
    validation_pattern: str = ""

class SimpleEnhancedProcessor:
    """Simplified enhanced document processor with basic field detection"""
    
    def __init__(self):
        self.extracted_text = ""
        self.document_type = ""
        self.fields = []
        
    def process_document(self, file_path: str) -> Dict:
        """Process document and return enhanced field detection results"""
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.pdf':
                return self._process_pdf_simple(file_path)
            elif file_ext in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
                return self._process_image(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")
                
        except Exception as e:
            raise Exception(f"Error processing document: {str(e)}")
    
    def _process_pdf_simple(self, file_path: str) -> Dict:
        """Process PDF using simple image conversion - handles all pages"""
        try:
            # Convert all PDF pages to images
            images = self._pdf_to_images(file_path)
            if not images:
                raise ValueError("Could not convert PDF to images")
            
            all_fields = []
            extracted_text = []
            
            # Process each page
            for page_num, image in images:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                page_text = pytesseract.image_to_string(gray)
                extracted_text.append(f"--- Page {page_num + 1} ---\n{page_text}")
                
                # Detect fields using simple methods
                fields = self._detect_fields_simple(gray, page_num)
                all_fields.extend(fields)
            
            self.extracted_text = '\n'.join(extracted_text)
            
            return {
                'extracted_text': self.extracted_text,
                'fields': all_fields,
                'total_fields': len(all_fields),
                'document_type': 'pdf',
                'has_acroform': False
            }
            
        except Exception as e:
            raise Exception(f"Error processing PDF: {str(e)}")
    
    def _pdf_to_images(self, pdf_path: str):
        """Convert all PDF pages to images using PyMuPDF"""
        try:
            import fitz
            pdf_document = fitz.open(pdf_path)
            images = []
            
            # Convert each page
            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]
                pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))
                img_data = pix.tobytes("png")
                
                # Convert to OpenCV format
                nparr = np.frombuffer(img_data, np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                images.append((page_num, image))
            
            pdf_document.close()
            return images
        except Exception as e:
            print(f"Error converting PDF to images: {e}")
            return []
    
    def _process_image(self, file_path: str) -> Dict:
        """Process image file"""
        try:
            image = cv2.imread(file_path)
            if image is None:
                raise ValueError(f"Could not load image: {file_path}")
            
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            self.extracted_text = pytesseract.image_to_string(gray)
            
            # Detect fields using simple methods
            fields = self._detect_fields_simple(gray)
            
            return {
                'extracted_text': self.extracted_text,
                'fields': fields,
                'total_fields': len(fields),
                'document_type': 'image'
            }
            
        except Exception as e:
            raise Exception(f"Error processing image: {str(e)}")
    
    def _detect_fields_simple(self, gray_image: np.ndarray, page_num: int = 0) -> List[FormField]:
        """Simple field detection using basic image processing"""
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
                if (1000 < area < 50000 and  # Reasonable size
                    30 < w < image_width * 0.7 and  # Width constraints
                    15 < h < image_height * 0.2 and  # Height constraints
                    0.3 < aspect_ratio < 15):  # Aspect ratio constraints
                    
                    # Check if area is mostly blank
                    roi = gray_image[y:y+h, x:x+w]
                    if roi.size > 0:
                        mean_intensity = np.mean(roi)
                        if mean_intensity > 200:  # Mostly white
                            field_type = self._classify_field_by_context(gray_image, x, y, w, h)
                            
                            field = FormField(
                                id=f"field_p{page_num}_{i}",
                                field_type=field_type,
                                x=x,
                                y=y,
                                width=w,
                                height=h,
                                context=field_type,
                                confidence=0.7
                            )
                            # Store page number as a custom attribute
                            field.page = page_num
                            fields.append(field)
            
            return fields
            
        except Exception as e:
            print(f"Error detecting fields: {e}")
            return []
    
    def _classify_field_by_context(self, gray_image: np.ndarray, x: int, y: int, w: int, h: int) -> str:
        """Classify field type based on surrounding context"""
        try:
            # Extract text around the field
            context_region = gray_image[max(0, y-20):min(gray_image.shape[0], y+h+20), 
                                      max(0, x-50):min(gray_image.shape[1], x+w+50)]
            
            if context_region.size > 0:
                context_text = pytesseract.image_to_string(context_region).lower()
                
                # Classify based on context
                if any(keyword in context_text for keyword in ['name', 'enter your name']):
                    return 'name'
                elif any(keyword in context_text for keyword in ['email', 'e-mail']):
                    return 'email'
                elif any(keyword in context_text for keyword in ['phone', 'telephone', 'tel']):
                    return 'phone'
                elif any(keyword in context_text for keyword in ['address', 'street']):
                    return 'address'
                elif any(keyword in context_text for keyword in ['date', 'birth', 'dob']):
                    return 'date'
                elif any(keyword in context_text for keyword in ['age', 'years']):
                    return 'age'
                elif any(keyword in context_text for keyword in ['signature', 'sign']):
                    return 'signature'
            
            return 'text'
            
        except Exception as e:
            print(f"Error classifying field context: {e}")
            return 'text'

def convert_form_fields_to_dict(fields: List[FormField]) -> List[Dict]:
    """Convert FormField objects to dictionary format for API compatibility"""
    return [
        {
            'id': field.id,
            'field_type': field.field_type,
            'x_position': field.x,
            'y_position': field.y,
            'width': field.width,
            'height': field.height,
            'context': field.context,
            'confidence': field.confidence,
            'is_required': field.is_required,
            'placeholder': field.placeholder,
            'validation_pattern': field.validation_pattern,
            'page': getattr(field, 'page', 0),  # Include page number
            'user_content': '',
            'ai_suggestion': '',
            'ai_enhanced': False
        }
        for field in fields
    ]

