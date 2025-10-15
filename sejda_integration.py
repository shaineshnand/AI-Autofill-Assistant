"""
Sejda PDF Integration Module

This module provides integration with Sejda PDF tools to create fillable PDFs
and populate them with AI-generated data. It supports both Sejda SDK (Java)
and Sejda Desktop for offline processing.

Features:
- Create fillable PDFs from regular PDFs
- Detect and create form fields automatically
- Fill form fields with AI-generated data
- Maintain data privacy through offline processing
"""

import os
import subprocess
import tempfile
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import fitz  # PyMuPDF

logger = logging.getLogger(__name__)

class SejdaIntegration:
    """Integration class for Sejda PDF tools"""
    
    def __init__(self, sejda_jar_path: Optional[str] = None, sejda_desktop_path: Optional[str] = None):
        """
        Initialize Sejda integration
        
        Args:
            sejda_jar_path: Path to Sejda SDK JAR file
            sejda_desktop_path: Path to Sejda Desktop executable
        """
        self.sejda_jar_path = sejda_jar_path or self._find_sejda_jar()
        self.sejda_desktop_path = sejda_desktop_path or self._find_sejda_desktop()
        
    def _find_sejda_jar(self) -> Optional[str]:
        """Find Sejda SDK JAR file in common locations"""
        common_paths = [
            "sejda-console-3.2.86.jar",
            "lib/sejda-console.jar",
            "sejda/sejda-console.jar",
            "/usr/local/bin/sejda-console.jar",
            "C:\\Program Files\\Sejda\\sejda-console.jar"
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                return path
        return None
    
    def _find_sejda_desktop(self) -> Optional[str]:
        """Find Sejda Desktop executable in common locations"""
        common_paths = [
            "sejda-desktop",
            "SejdaDesktop.exe",
            "/usr/local/bin/sejda-desktop",
            "C:\\Program Files\\Sejda\\SejdaDesktop.exe",
            "C:\\Program Files (x86)\\Sejda\\SejdaDesktop.exe"
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                return path
        return None
    
    def create_fillable_pdf_with_sejda_sdk(self, input_pdf_path: str, output_pdf_path: str) -> bool:
        """
        Create fillable PDF using Sejda SDK
        
        Args:
            input_pdf_path: Path to input PDF
            output_pdf_path: Path to output fillable PDF
            
        Returns:
            True if successful, False otherwise
        """
        if not self.sejda_jar_path:
            logger.error("Sejda SDK JAR not found")
            return False
            
        try:
            # Create a temporary configuration file for Sejda
            config = {
                "tasks": [
                    {
                        "type": "add_form_fields",
                        "input": input_pdf_path,
                        "output": output_pdf_path,
                        "auto_detect_fields": True,
                        "field_detection": {
                            "detect_blanks": True,
                            "detect_dotted_lines": True,
                            "min_field_width": 30,
                            "min_field_height": 15
                        }
                    }
                ]
            }
            
            config_path = tempfile.mktemp(suffix='.json')
            with open(config_path, 'w') as f:
                json.dump(config, f)
            
            # Run Sejda SDK
            cmd = [
                'java', '-jar', self.sejda_jar_path,
                '--config', config_path
            ]
            
            logger.info(f"Running Sejda SDK: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            # Clean up config file
            os.unlink(config_path)
            
            if result.returncode == 0:
                logger.info("Sejda SDK successfully created fillable PDF")
                return True
            else:
                logger.error(f"Sejda SDK failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error running Sejda SDK: {e}")
            return False
    
    def create_fillable_pdf_with_pymupdf(self, input_pdf_path: str, output_pdf_path: str) -> bool:
        """
        Create fillable PDF using PyMuPDF (fallback method)
        This is our existing enhanced detection method
        
        Args:
            input_pdf_path: Path to input PDF
            output_pdf_path: Path to output fillable PDF
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Import our existing enhanced field detector
            from enhanced_field_detector import EnhancedFieldDetector
            
            # Open PDF
            doc = fitz.open(input_pdf_path)
            
            # Detect fields using our enhanced detector
            detector = EnhancedFieldDetector()
            fields = detector.process_pdf_enhanced(input_pdf_path)
            
            # Create fillable PDF with detected fields
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Get fields for this page
                page_fields = [f for f in fields if f.get('page_number', 0) == page_num]
                
                for field in page_fields:
                    # Create text field widget
                    widget = fitz.Widget()
                    widget.field_type = fitz.WIDGET_TYPE_TEXT
                    widget.field_name = f"field_{field['id']}"
                    widget.field_value = ""
                    widget.field_flags = fitz.PDF_FIELD_IS_MULTILINE
                    
                    # Set field rectangle
                    rect = fitz.Rect(
                        field['x_position'],
                        field['y_position'],
                        field['x_position'] + field['width'],
                        field['y_position'] + field['height']
                    )
                    widget.rect = rect
                    
                    # Add widget to page
                    page.add_widget(widget)
            
            # Save fillable PDF
            doc.save(output_pdf_path, garbage=4, deflate=True, clean=True)
            doc.close()
            
            logger.info(f"Created fillable PDF with {len(fields)} fields using PyMuPDF")
            return True
            
        except Exception as e:
            logger.error(f"Error creating fillable PDF with PyMuPDF: {e}")
            return False
    
    def create_fillable_pdf(self, input_pdf_path: str, output_pdf_path: str) -> bool:
        """
        Create fillable PDF using the best available method
        
        Args:
            input_pdf_path: Path to input PDF
            output_pdf_path: Path to output fillable PDF
            
        Returns:
            True if successful, False otherwise
        """
        # Try Sejda SDK first
        if self.sejda_jar_path:
            logger.info("Attempting to use Sejda SDK for fillable PDF creation")
            if self.create_fillable_pdf_with_sejda_sdk(input_pdf_path, output_pdf_path):
                return True
            else:
                logger.warning("Sejda SDK failed, falling back to PyMuPDF")
        else:
            logger.info("Sejda SDK not available, using PyMuPDF with enhanced detection")
        
        # Fallback to PyMuPDF with enhanced detection
        return self.create_fillable_pdf_with_pymupdf(input_pdf_path, output_pdf_path)
    
    def fill_pdf_with_ai_data(self, fillable_pdf_path: str, ai_data: Dict[str, str], output_pdf_path: str) -> bool:
        """
        Fill PDF form fields with AI-generated data
        
        Args:
            fillable_pdf_path: Path to fillable PDF
            ai_data: Dictionary of field names to values
            output_pdf_path: Path to output filled PDF
            
        Returns:
            True if successful, False otherwise
        """
        try:
            doc = fitz.open(fillable_pdf_path)
            
            # Fill form fields
            for page_num in range(len(doc)):
                page = doc[page_num]
                widgets = page.widgets()
                
                for widget in widgets:
                    field_name = widget.field_name
                    if field_name in ai_data:
                        widget.field_value = ai_data[field_name]
                        widget.update()
            
            # Save filled PDF
            doc.save(output_pdf_path, garbage=4, deflate=True, clean=True)
            doc.close()
            
            logger.info(f"Filled PDF with {len(ai_data)} fields")
            return True
            
        except Exception as e:
            logger.error(f"Error filling PDF: {e}")
            return False
    
    def get_form_fields(self, pdf_path: str) -> List[Dict]:
        """
        Get list of form fields from a PDF
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of field information dictionaries
        """
        fields = []
        try:
            doc = fitz.open(pdf_path)
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                widgets = page.widgets()
                
                for widget in widgets:
                    field_info = {
                        'name': widget.field_name,
                        'type': widget.field_type,
                        'value': widget.field_value,
                        'rect': widget.rect,
                        'page': page_num
                    }
                    fields.append(field_info)
            
            doc.close()
            return fields
            
        except Exception as e:
            logger.error(f"Error getting form fields: {e}")
            return []


def create_fillable_pdf_with_sejda(input_pdf_path: str, output_pdf_path: str) -> bool:
    """
    Convenience function to create fillable PDF using Sejda integration
    
    Args:
        input_pdf_path: Path to input PDF
        output_pdf_path: Path to output fillable PDF
        
    Returns:
        True if successful, False otherwise
    """
    sejda = SejdaIntegration()
    return sejda.create_fillable_pdf(input_pdf_path, output_pdf_path)


def fill_pdf_with_ai_data(fillable_pdf_path: str, ai_data: Dict[str, str], output_pdf_path: str) -> bool:
    """
    Convenience function to fill PDF with AI data
    
    Args:
        fillable_pdf_path: Path to fillable PDF
        ai_data: Dictionary of field names to values
        output_pdf_path: Path to output filled PDF
        
    Returns:
        True if successful, False otherwise
    """
    sejda = SejdaIntegration()
    return sejda.fill_pdf_with_ai_data(fillable_pdf_path, ai_data, output_pdf_path)
