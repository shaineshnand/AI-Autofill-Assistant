"""
Sejda Desktop CLI Integration

This module integrates Sejda PDF Desktop CLI to automatically convert PDFs
to fillable forms with accurate field detection - all processed locally with NO data leakage.

Requirements:
- Sejda PDF Desktop installed on the system
- sejda-console CLI accessible from command line
"""

import os
import subprocess
import tempfile
import logging
from pathlib import Path
from typing import Optional, Dict, List
import fitz  # PyMuPDF

logger = logging.getLogger(__name__)

class SejdaDesktopCLI:
    """Integration class for Sejda Desktop CLI"""
    
    def __init__(self):
        """Initialize Sejda Desktop CLI integration"""
        self.sejda_console_path = self._find_sejda_console()
        logger.info(f"Sejda Console Path: {self.sejda_console_path}")
    
    def _find_sejda_console(self) -> Optional[str]:
        """Find sejda-console executable in common locations"""
        # Common installation paths for Sejda Desktop
        common_paths = [
            # Windows paths
            r"C:\Program Files\Sejda PDF Desktop\sejda-console.exe",
            r"C:\Program Files (x86)\Sejda PDF Desktop\sejda-console.exe",
            r"C:\Program Files\Sejda\sejda-console.exe",
            r"C:\Program Files (x86)\Sejda\sejda-console.exe",
            # macOS paths
            "/Applications/Sejda PDF.app/Contents/MacOS/sejda-console",
            "/usr/local/bin/sejda-console",
            # Linux paths
            "/opt/sejda/sejda-console",
            "/usr/bin/sejda-console",
            # Current directory
            "./sejda-console",
            "./sejda-console.exe"
        ]
        
        # First, try to find it in PATH
        try:
            result = subprocess.run(['sejda-console', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                logger.info("Found sejda-console in PATH")
                return 'sejda-console'
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        # Then check common paths
        for path in common_paths:
            if os.path.exists(path):
                logger.info(f"Found sejda-console at: {path}")
                return path
        
        logger.warning("Sejda Console not found in common locations")
        return None
    
    def is_available(self) -> bool:
        """Check if Sejda Desktop CLI is available"""
        if not self.sejda_console_path:
            return False
        
        try:
            result = subprocess.run([self.sejda_console_path, '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Error checking Sejda availability: {e}")
            return False
    
    def add_form_fields(self, input_pdf: str, output_pdf: str) -> bool:
        """
        Use Sejda Desktop CLI to automatically add form fields to a PDF.
        This detects blank spaces, dotted lines, and creates fillable text fields.
        
        Args:
            input_pdf: Path to input PDF
            output_pdf: Path to output fillable PDF
            
        Returns:
            True if successful, False otherwise
        """
        if not self.sejda_console_path:
            logger.error("Sejda Console not available")
            return False
        
        try:
            # Sejda CLI command to add form fields
            # Note: The exact command may vary based on Sejda version
            # We'll try multiple command formats
            
            commands_to_try = [
                # Format 1: addformfields task
                [self.sejda_console_path, 'addformfields', 
                 '-f', input_pdf, '-o', output_pdf],
                
                # Format 2: add-form-fields task
                [self.sejda_console_path, 'add-form-fields', 
                 '-f', input_pdf, '-o', output_pdf],
                
                # Format 3: forms task with detect option
                [self.sejda_console_path, 'forms', '--detect',
                 '-f', input_pdf, '-o', output_pdf],
            ]
            
            for i, cmd in enumerate(commands_to_try):
                try:
                    logger.info(f"Trying Sejda command format {i+1}: {' '.join(cmd)}")
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                    
                    if result.returncode == 0:
                        logger.info(f"✓ Sejda successfully created fillable PDF with command format {i+1}")
                        logger.info(f"Output: {result.stdout}")
                        return True
                    else:
                        logger.warning(f"Command format {i+1} failed: {result.stderr}")
                except Exception as e:
                    logger.warning(f"Command format {i+1} error: {e}")
                    continue
            
            logger.error("All Sejda command formats failed")
            return False
            
        except Exception as e:
            logger.error(f"Error running Sejda CLI: {e}")
            return False
    
    def extract_form_fields(self, pdf_path: str) -> List[Dict]:
        """
        Extract form fields from a fillable PDF created by Sejda
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of field information dictionaries
        """
        fields = []
        try:
            doc = fitz.open(pdf_path)
            field_count = 0
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                widgets = page.widgets()
                
                if widgets:
                    for widget in widgets:
                        field_name = widget.field_name or f"field_{field_count}"
                        field_rect = widget.rect
                        
                        field_info = {
                            'id': f"sejda_{field_name}_{page_num}_{field_count}",
                            'field_type': 'text',
                            'x_position': int(field_rect.x0),
                            'y_position': int(field_rect.y0),
                            'width': int(field_rect.width),
                            'height': int(field_rect.height),
                            'context': f"Sejda field: {field_name}",
                            'page': page_num,
                            'page_number': page_num,
                            'sejda_field_name': field_name,
                            'detection_method': 'sejda_desktop_cli'
                        }
                        fields.append(field_info)
                        field_count += 1
            
            doc.close()
            logger.info(f"Extracted {len(fields)} form fields from Sejda PDF")
            return fields
            
        except Exception as e:
            logger.error(f"Error extracting form fields: {e}")
            return []
    
    def process_pdf_to_fillable(self, input_pdf: str, output_pdf: str) -> Dict:
        """
        Complete workflow: Convert PDF to fillable and extract fields
        
        Args:
            input_pdf: Path to input PDF
            output_pdf: Path to output fillable PDF
            
        Returns:
            Dictionary with success status and fields
        """
        result = {
            'success': False,
            'fields': [],
            'error': None,
            'method': 'sejda_desktop_cli'
        }
        
        # Step 1: Add form fields using Sejda CLI
        logger.info(f"Converting PDF to fillable using Sejda Desktop CLI...")
        if not self.add_form_fields(input_pdf, output_pdf):
            result['error'] = 'Failed to create fillable PDF with Sejda Desktop CLI'
            return result
        
        # Step 2: Extract the form fields
        logger.info(f"Extracting form fields from fillable PDF...")
        fields = self.extract_form_fields(output_pdf)
        
        if not fields:
            result['error'] = 'No form fields detected in output PDF'
            return result
        
        result['success'] = True
        result['fields'] = fields
        logger.info(f"✓ Successfully processed PDF: {len(fields)} fields detected")
        
        return result


def create_fillable_pdf_with_sejda_desktop(input_pdf: str, output_pdf: str) -> Dict:
    """
    Convenience function to create fillable PDF using Sejda Desktop CLI
    
    Args:
        input_pdf: Path to input PDF
        output_pdf: Path to output fillable PDF
        
    Returns:
        Dictionary with success status and fields
    """
    sejda = SejdaDesktopCLI()
    
    if not sejda.is_available():
        return {
            'success': False,
            'fields': [],
            'error': 'Sejda Desktop CLI not available. Please install Sejda PDF Desktop.',
            'method': 'sejda_desktop_cli'
        }
    
    return sejda.process_pdf_to_fillable(input_pdf, output_pdf)



