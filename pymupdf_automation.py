import os
import fitz  # PyMuPDF
import json
import time

class PyMuPDFAutomation:
    def __init__(self):
        self.available = self._check_pymupdf()
    
    def _check_pymupdf(self):
        try:
            import fitz
            return True
        except ImportError:
            print("PyMuPDF not available - install with: pip install PyMuPDF")
            return False
    
    def convert_to_fillable(self, input_pdf, output_pdf, ai_data, timeout=60):
        """
        Fill PDF AcroForm fields using PyMuPDF (much more reliable than LibreOffice)
        """
        if not self.available:
            return {'success': False, 'error': 'PyMuPDF not available'}
        
        try:
            print(f"\n=== PYMUPDF ACROFORM FILLING ===")
            print(f"Input PDF: {input_pdf}")
            print(f"Output PDF: {output_pdf}")
            print(f"AI Data: {ai_data}")
            
            # Step 1: Open the PDF
            print(f"\nStep 1: Opening PDF with PyMuPDF...")
            doc = fitz.open(input_pdf)
            print(f"   -> PDF opened successfully")
            
            # Step 2: Check for AcroForm fields
            print(f"\nStep 2: Checking for AcroForm fields...")
            filled_count = 0
            total_fields = 0
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                print(f"   -> Checking page {page_num + 1}...")
                
                # Get AcroForm fields on this page
                widgets = list(page.widgets())  # Convert generator to list
                print(f"      -> Found {len(widgets)} AcroForm fields on page {page_num + 1}")
                total_fields += len(widgets)
                
                # List all fields for debugging
                for i, widget in enumerate(widgets):
                    try:
                        field_name = widget.field_name
                        field_type = widget.field_type_string
                        field_value = widget.field_value
                        print(f"      -> Field {i+1}: '{field_name}' (type: {field_type}, current: '{field_value}')")
                    except Exception as e:
                        print(f"      -> Field {i+1}: Error reading field info: {e}")
                
                # Fill each field
                for i, widget in enumerate(widgets):
                    try:
                        field_name = widget.field_name
                        field_type = widget.field_type_string
                        print(f"      -> Filling field {i+1}: '{field_name}' (type: {field_type})")
                        
                        # Get AI data for this field
                        ai_value = None
                        for field_id, value in ai_data.items():
                            # Try to match field names
                            if (field_name and field_id and 
                                (field_name.lower() in field_id.lower() or 
                                 field_id.lower() in field_name.lower())):
                                ai_value = value
                                break
                        
                        # If no direct match, use the next available AI data
                        if ai_value is None and i < len(list(ai_data.values())):
                            ai_value = list(ai_data.values())[i]
                        
                        if ai_value:
                            print(f"      -> Filling with: '{ai_value}'")
                            
                            # Fill the field based on type
                            if field_type == "text":
                                widget.field_value = str(ai_value)
                            elif field_type == "checkbox":
                                widget.field_value = True if str(ai_value).lower() in ['true', 'yes', '1', 'on'] else False
                            elif field_type == "button":
                                # Skip button fields
                                print(f"      -> Skipping button field")
                                continue
                            else:
                                widget.field_value = str(ai_value)
                            
                            widget.update()
                            filled_count += 1
                            print(f"      -> Field filled successfully")
                        else:
                            print(f"      -> No AI data found for this field")
                            
                    except Exception as e:
                        print(f"      -> Error filling field {i+1}: {e}")
                        continue
            
            print(f"\n   -> Total AcroForm fields found: {total_fields}")
            print(f"   -> Fields filled: {filled_count}")
            
            # Step 3: Save the filled PDF
            print(f"\nStep 3: Saving filled PDF...")
            doc.save(output_pdf)
            doc.close()
            print(f"   -> PDF saved to: {output_pdf}")
            
            # Step 4: Verify the output
            if os.path.exists(output_pdf):
                file_size = os.path.getsize(output_pdf)
                print(f"   -> Output file exists and is {file_size} bytes")
                return {
                    'success': True,
                    'output_path': output_pdf,
                    'message': f'PDF filled successfully with {filled_count}/{total_fields} AcroForm fields',
                    'filled_count': filled_count,
                    'total_fields': total_fields
                }
            else:
                return {
                    'success': False,
                    'error': 'Output PDF was not created'
                }
                
        except Exception as e:
            import traceback
            error_msg = traceback.format_exc()
            print(f"\nPyMuPDF automation failed: {e}")
            print(f"   Traceback: {error_msg}")
            return {'success': False, 'error': f"PyMuPDF automation failed: {e}"}
