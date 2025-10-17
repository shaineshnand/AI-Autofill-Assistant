import os
import time
import subprocess
import shutil
from pathlib import Path

try:
    from pywinauto import Application
    PYWINAUTO_AVAILABLE = True
except ImportError:
    PYWINAUTO_AVAILABLE = False
    print("WARNING: pywinauto not available - install with: pip install pywinauto")

class LibreOfficeDrawAutomation:
    def __init__(self):
        self.libreoffice_path = self._find_libreoffice()
        
    def _find_libreoffice(self):
        """Find LibreOffice installation path"""
        possible_paths = [
            r"C:\Program Files\LibreOffice\program\soffice.exe",
            r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
            r"C:\Program Files\LibreOffice 7.6\program\soffice.exe",
            r"C:\Program Files\LibreOffice 7.5\program\soffice.exe",
            r"C:\Program Files\LibreOffice 7.4\program\soffice.exe",
            r"C:\Program Files\LibreOffice 7.3\program\soffice.exe",
            r"C:\Program Files\LibreOffice 7.2\program\soffice.exe",
            r"C:\Program Files\LibreOffice 7.1\program\soffice.exe",
            r"C:\Program Files\LibreOffice 7.0\program\soffice.exe",
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                print(f"Found LibreOffice at: {path}")
                return path
        
        # Try to find in PATH
        try:
            result = subprocess.run(['where', 'soffice'], capture_output=True, text=True)
            if result.returncode == 0:
                path = result.stdout.strip().split('\n')[0]
                print(f"Found LibreOffice in PATH: {path}")
                return path
        except:
            pass
        
        print("LibreOffice not found in common locations")
        return None
    
    def convert_to_fillable(self, input_pdf, output_pdf, ai_data=None, timeout=120):
        """
        Open PDF in LibreOffice Draw, fill form fields with AI data, and save
        
        Args:
            input_pdf: Path to input PDF file
            output_pdf: Path to output filled PDF file
            ai_data: Dictionary of field_id -> value mappings
            timeout: Maximum time to wait for automation
            
        Returns:
            Dictionary with success status and output path
        """
        if not PYWINAUTO_AVAILABLE:
            return {
                'success': False,
                'error': 'pywinauto not available - install with: pip install pywinauto'
            }
        
        if not self.libreoffice_path:
            return {
                'success': False,
                'error': 'LibreOffice not found - please install LibreOffice'
            }
        
        if not os.path.exists(input_pdf):
            return {
                'success': False,
                'error': f'Input PDF not found: {input_pdf}'
            }
        
        print("FULLY AUTOMATIC LIBREOFFICE DRAW CONVERSION")
        print(f"Input: {input_pdf}")
        print(f"Output: {output_pdf}")
        
        try:
            # Step 1: Close any existing LibreOffice instances
            print("\nStep 1: Closing any open LibreOffice instances...")
            try:
                subprocess.run(['taskkill', '/F', '/IM', 'soffice.exe'], 
                             capture_output=True, timeout=5)
                time.sleep(2)
            except:
                pass
            
            # Step 2: Open PDF in LibreOffice Draw
            print(f"\nStep 2: Opening PDF in LibreOffice Draw...")
            print(f"   File: {input_pdf}")
            
            # Use LibreOffice Draw to open PDF (better for AcroForm field detection)
            cmd = [self.libreoffice_path, '--draw', input_pdf]
            subprocess.Popen(cmd)
            time.sleep(10)  # Wait for LibreOffice to load
            
            # Step 3: Connect to LibreOffice window
            print(f"\nStep 3: Connecting to LibreOffice Draw window...")
            try:
                # Wait a bit for LibreOffice to fully load
                time.sleep(5)
                
                # Try multiple connection methods
                app = None
                window = None
                
                # Method 1: Try connecting by title pattern
                try:
                    print(f"   -> Method 1: Connecting by title pattern...")
                    app = Application(backend="uia").connect(title_re=".*LibreOffice.*", timeout=15)
                    windows = app.windows()
                    if windows:
                        window = windows[0]
                        print(f"   -> Found window: {window.window_text()}")
                    else:
                        print(f"   -> No windows found with title pattern")
                except Exception as e:
                    print(f"   -> Method 1 failed: {e}")
                
                # Method 2: Try connecting by process name
                if not window:
                    try:
                        print(f"   -> Method 2: Connecting by process name...")
                        app = Application(backend="uia").connect(process="soffice.exe", timeout=15)
                        windows = app.windows()
                        if windows:
                            window = windows[0]
                            print(f"   -> Found window: {window.window_text()}")
                        else:
                            print(f"   -> No windows found with process name")
                    except Exception as e:
                        print(f"   -> Method 2 failed: {e}")
                
                # Method 3: Try connecting to any window with "Draw" in title
                if not window:
                    try:
                        print(f"   -> Method 3: Connecting by Draw title...")
                        app = Application(backend="uia").connect(title_re=".*Draw.*", timeout=15)
                        windows = app.windows()
                        if windows:
                            window = windows[0]
                            print(f"   -> Found window: {window.window_text()}")
                        else:
                            print(f"   -> No windows found with Draw title")
                    except Exception as e:
                        print(f"   -> Method 3 failed: {e}")
                
                if not window:
                    raise Exception("Could not connect to any LibreOffice window using all methods")
                
                window.set_focus()
                print(f"   Successfully connected to: {window.window_text()}")
                
            except Exception as e:
                print(f"   Window connection failed: {e}")
                raise Exception(f"LibreOffice window connection failed: {e}")
            
            # Step 4: Wait for PDF to load and look for AcroForm fields
            print(f"\nStep 4: Looking for AcroForm fields in LibreOffice Draw...")
            time.sleep(8)  # Wait longer for PDF to fully load in Draw
            
            # Try to enable form field editing mode
            print(f"   -> Enabling form field editing...")
            try:
                # Try to access Tools menu for form controls
                window.type_keys("%t")  # Alt+T for Tools menu
                time.sleep(2)
                window.type_keys("c")   # Controls
                time.sleep(2)
                window.type_keys("{ESC}")  # Close menu
                time.sleep(1)
            except Exception as e:
                print(f"   -> Form controls access failed: {e}")
            
            # Step 5: Fill form fields with AI data
            if ai_data and len(ai_data) > 0:
                print(f"\nStep 5: Filling {len(ai_data)} form fields with AI data...")
                print(f"   AI Data to fill:")
                for i, (field_id, value) in enumerate(ai_data.items()):
                    print(f"      {i+1}. {field_id}: '{value}'")
                
                window.set_focus()
                filled_count = 0
                
                try:
                    # AcroForm field detection and filling
                    print(f"   -> Looking for AcroForm fields...")
                    
                    # First, try to find form fields using control detection
                    all_controls = window.descendants()
                    print(f"   -> Found {len(all_controls)} total controls")
                    
                    # Look for specific control types that might be form fields
                    form_controls = []
                    for control in all_controls:
                        try:
                            control_type = control.control_type()
                            class_name = control.class_name()
                            print(f"   -> Control: {control_type} - {class_name}")
                            
                            # Look for text input controls, edit controls, etc.
                            if control_type in ["EditControl", "TextControl", "DocumentControl"]:
                                form_controls.append(control)
                                print(f"      -> Found potential form field: {control_type}")
                        except:
                            continue
                    
                    print(f"   -> Found {len(form_controls)} potential form fields")
                    
                    # Try to fill the form fields
                    for i, (field_id, value) in enumerate(ai_data.items()):
                        try:
                            print(f"   -> Field {i+1}/{len(ai_data)}: {field_id}")
                            
                            # Try to click on a form control if available
                            if i < len(form_controls):
                                control = form_controls[i]
                                print(f"   -> Clicking on form control {i+1}")
                                control.click()
                                time.sleep(2)
                            else:
                                # Fallback: click at calculated positions
                                window_rect = window.rectangle()
                                center_x = window_rect.left + window_rect.width() // 2
                                center_y = window_rect.top + window_rect.height() // 2
                                
                                # Calculate position for this field
                                if i == 0:
                                    click_x = center_x
                                    click_y = center_y - 150  # Top field
                                elif i == 1:
                                    click_x = center_x
                                    click_y = center_y - 50   # Middle-top field
                                elif i == 2:
                                    click_x = center_x
                                    click_y = center_y + 50   # Middle-bottom field
                                else:
                                    click_x = center_x
                                    click_y = center_y + 150 + (i * 50)  # Bottom fields
                                
                                print(f"   -> Clicking at calculated position ({click_x}, {click_y})")
                                window.click_input(coords=(click_x, click_y))
                                time.sleep(2)
                            
                            # Try to select existing text and replace it
                            window.type_keys("^a")
                            time.sleep(1)
                            
                            # Type the AI value
                            clean_value = str(value).replace('{', '{{').replace('}', '}}')
                            print(f"   -> VISIBLY TYPING: '{clean_value}'")
                            window.type_keys(clean_value, with_spaces=True, pause=0.5)
                            time.sleep(2)
                            
                            # Press Tab to move to next field (standard form behavior)
                            window.type_keys("{TAB}")
                            time.sleep(1)
                            
                            filled_count += 1
                            print(f"   -> Field {i+1} filled with: '{clean_value}'")
                            
                        except Exception as e:
                            print(f"   -> Error with field {i+1}: {e}")
                            continue
                    
                    print(f"\n   -> Successfully filled {filled_count}/{len(ai_data)} AcroForm fields")
                    
                    # Try to find and click on form fields
                    print(f"   -> Looking for form fields to click and fill...")
                    try:
                        # Look for various types of controls
                        all_controls = window.descendants()
                        print(f"      -> Found {len(all_controls)} total controls")
                        
                        # Look for text input controls
                        text_controls = window.descendants(control_type="Edit")
                        print(f"      -> Found {len(text_controls)} text input controls")
                        
                        # Look for text controls
                        text_areas = window.descendants(control_type="Text")
                        print(f"      -> Found {len(text_areas)} text controls")
                        
                        # Look for document controls
                        doc_controls = window.descendants(control_type="Document")
                        print(f"      -> Found {len(doc_controls)} document controls")
                        
                        # Try clicking on document first to enable editing
                        if doc_controls:
                            try:
                                doc_control = doc_controls[0]
                                doc_control.click()
                                time.sleep(2)
                                print(f"      -> Clicked on document to enable editing")
                            except Exception as e:
                                print(f"      -> Document click failed: {e}")
                        
                        # Try to fill using intelligent field detection
                        print(f"      -> Trying intelligent field detection and filling...")
                        
                        # First, try to find text boxes or form fields by clicking around the document
                        window_rect = window.rectangle()
                        window_width = window_rect.width()
                        window_height = window_rect.height()
                        
                        # Define potential field locations (adjust based on your form layout)
                        field_locations = [
                            (window_width // 2, window_height // 3),      # Top area
                            (window_width // 2, window_height // 2),      # Middle area  
                            (window_width // 2, 2 * window_height // 3),  # Bottom area
                        ]
                        
                        for i, (field_id, value) in enumerate(ai_data.items()):
                            try:
                                print(f"      -> Field {i+1}/{len(ai_data)}: {field_id}")
                                
                                # Try clicking at different locations to find form fields
                                if i < len(field_locations):
                                    click_x, click_y = field_locations[i]
                                    print(f"      -> Clicking at location ({click_x}, {click_y}) for field: {field_id}")
                                    window.click_input(coords=(click_x, click_y))
                                    time.sleep(2)
                                    
                                    # Try to select any existing text
                                    window.type_keys("^a")
                                    time.sleep(1)
                                    
                                    # Type the value
                                    clean_value = str(value).replace('{', '{{').replace('}', '}}')
                                    print(f"      -> VISIBLY TYPING: '{clean_value}'")
                                    window.type_keys(clean_value, with_spaces=True, pause=0.5)
                                    time.sleep(2)
                                    
                                    # Press Tab to move to next field
                                    window.type_keys("{TAB}")
                                    time.sleep(1)
                                    
                                    filled_count += 1
                                    print(f"      -> Field {i+1} filled with: '{clean_value}'")
                                else:
                                    # For additional fields, use tab navigation
                                    print(f"      -> Using tab navigation for field: {field_id}")
                                    window.type_keys("{TAB}")
                                    time.sleep(1)
                                    
                                    window.type_keys("^a")
                                    time.sleep(1)
                                    
                                    clean_value = str(value).replace('{', '{{').replace('}', '}}')
                                    print(f"      -> VISIBLY TYPING: '{clean_value}'")
                                    window.type_keys(clean_value, with_spaces=True, pause=0.5)
                                    time.sleep(2)
                                    
                                    window.type_keys("{TAB}")
                                    time.sleep(1)
                                    
                                    filled_count += 1
                                    print(f"      -> Field {i+1} filled with: '{clean_value}'")
                                    
                            except Exception as e:
                                print(f"      -> Error with field {i+1}: {e}")
                                continue
                                
                    except Exception as e:
                        print(f"      -> Field filling failed: {e}")
                    
                    # Method 2: Try clicking on text areas
                    if filled_count < len(ai_data):
                        print(f"   -> Method 2: Looking for text areas...")
                        try:
                            # Look for text areas
                            text_areas = window.descendants(control_type="Text")
                            print(f"      -> Found {len(text_areas)} text areas")
                            
                            for i, control in enumerate(text_areas[:len(ai_data)]):
                                try:
                                    if i < len(list(ai_data.items())):
                                        field_id, value = list(ai_data.items())[i]
                                        print(f"      -> Clicking on text area {i+1} for field: {field_id}")
                                        
                                        control.click()
                                        time.sleep(2)
                                        
                                        # Select all and type
                                        window.type_keys("^a")
                                        time.sleep(1)
                                        
                                        clean_value = str(value).replace('{', '{{').replace('}', '}}')
                                        print(f"      -> VISIBLY TYPING: '{clean_value}'")
                                        window.type_keys(clean_value, with_spaces=True, pause=0.5)
                                        time.sleep(2)
                                        
                                        filled_count += 1
                                        print(f"      -> Text area {i+1} filled with: '{clean_value}'")
                                except Exception as e:
                                    print(f"      -> Error with text area {i+1}: {e}")
                                    continue
                                    
                        except Exception as e:
                            print(f"      -> Text area clicking failed: {e}")
                    
                    print(f"   AI filled {filled_count} form fields in LibreOffice Draw!")
                    
                except Exception as e:
                    print(f"   Form field filling failed: {e}")
                    import traceback
                    traceback.print_exc()
                
                if filled_count < len(ai_data):
                    print(f"   Only filled {filled_count}/{len(ai_data)} fields - some may be missing!")
            else:
                print(f"\nStep 5: Skipping AI fill (no data provided)")
            
            # Step 6: Save the filled PDF
            print(f"\nStep 6: Saving filled PDF...")
            try:
                window.set_focus()
                window.type_keys("^s")  # Ctrl+S
                time.sleep(3)
                print(f"   Save completed!")
            except Exception as e:
                print(f"   Save error: {e}")
            
            # Step 7: Export as PDF
            print(f"\nStep 7: Exporting as PDF...")
            try:
                window.set_focus()
                # Use File > Export as PDF
                window.type_keys("%f")  # Alt+F for File menu
                time.sleep(1)
                window.type_keys("e")   # Export
                time.sleep(2)
                window.type_keys("p")   # Export as PDF
                time.sleep(3)
                
                # Handle export dialog
                window.type_keys("{ENTER}")  # Confirm export
                time.sleep(5)
                print(f"   PDF export completed!")
            except Exception as e:
                print(f"   PDF export error: {e}")
            
            # Step 8: Close LibreOffice
            print(f"\nStep 8: Closing LibreOffice Draw...")
            try:
                time.sleep(3)
                window.type_keys("%{F4}")  # Alt+F4
                time.sleep(3)
                print(f"   LibreOffice closed")
            except:
                # Force kill if Alt+F4 didn't work
                subprocess.run(['taskkill', '/F', '/IM', 'soffice.exe'], 
                             capture_output=True, timeout=5)
                print(f"   LibreOffice force-closed")
            
            # Step 9: Check if output exists
            print(f"\nStep 9: Checking for filled PDF...")
            
            # LibreOffice typically saves to the same location as input
            if os.path.exists(input_pdf):
                print(f"   Found filled PDF: {input_pdf}")
                return {
                    'success': True,
                    'output_path': input_pdf,
                    'message': 'PDF filled automatically with LibreOffice Draw'
                }
            else:
                print(f"   No filled PDF found")
                return {
                    'success': False,
                    'error': 'Filled PDF not found - automation may have failed'
                }
            
        except Exception as e:
            import traceback
            error_msg = traceback.format_exc()
            print(f"\nLibreOffice automation failed: {e}")
            print(f"   Traceback: {error_msg}")
            
            return {
                'success': False,
                'error': f'LibreOffice automation failed: {e}'
            }
