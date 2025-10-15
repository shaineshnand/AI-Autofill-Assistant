"""
Simple Sejda Desktop Automation
FULLY AUTOMATIC: Opens PDF in Sejda, AI fills fields automatically, saves, closes
"""
import os
import time
import subprocess
from typing import Optional, Dict

try:
    from pywinauto.application import Application
    from pywinauto import Desktop
    PYWINAUTO_AVAILABLE = True
except ImportError:
    PYWINAUTO_AVAILABLE = False
    print("WARNING: pywinauto not available - install with: pip install pywinauto")


class SejdaSimpleAutomation:
    """FULLY AUTOMATIC Sejda automation - AI fills fields, saves, closes"""
    
    def __init__(self):
        self.sejda_path = self._find_sejda()
        
    def _find_sejda(self) -> Optional[str]:
        """Find Sejda Desktop executable"""
        paths = [
            r"C:\Program Files\Sejda PDF Desktop\Sejda PDF Desktop.exe",
            r"C:\Program Files (x86)\Sejda PDF Desktop\Sejda PDF Desktop.exe",
        ]
        for path in paths:
            if os.path.exists(path):
                return path
        return None
    
    def convert_to_fillable(self, input_pdf: str, output_pdf: str, ai_data: dict = None, timeout: int = 60) -> Dict:
        """
        FULLY AUTOMATIC: Open PDF in Sejda, AI fills fields automatically, saves, closes
        
        Args:
            input_pdf: Input PDF path
            output_pdf: Where to save filled PDF
            ai_data: Dictionary of AI-generated field values
            timeout: Maximum time to wait (seconds)
            
        Returns:
            Result dict with success status
        """
        if not PYWINAUTO_AVAILABLE or not self.sejda_path:
            return {'success': False, 'error': 'Sejda Desktop or pywinauto not available'}
        
        try:
            print("\n" + "="*60)
            print("FULLY AUTOMATIC SEJDA CONVERSION - EDIT MODE")
            print("="*60)
            
            # Step 1: Kill any existing Sejda processes
            print("\nStep 1: Closing any open Sejda instances...")
            try:
                subprocess.run(['taskkill', '/F', '/IM', 'Sejda PDF Desktop.exe'], 
                             capture_output=True, timeout=5)
                time.sleep(2)
            except:
                pass
            
            # Step 2: Open PDF in Sejda
            print(f"\nStep 2: Opening PDF in Sejda Desktop...")
            print(f"   File: {input_pdf}")
            subprocess.Popen([self.sejda_path, input_pdf])
            time.sleep(12)  # Wait longer for Sejda to fully load
            
            # Step 3: Connect to Sejda window
            print(f"\nStep 3: Connecting to Sejda window...")
            try:
                # Wait a bit for Sejda to fully load
                time.sleep(3)
                
                # Try multiple connection methods
                app = None
                window = None
                
                # Method 1: Try connecting by title pattern
                try:
                    print(f"   -> Method 1: Connecting by title pattern...")
                    app = Application(backend="uia").connect(title_re=".*Sejda.*", timeout=10)
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
                        app = Application(backend="uia").connect(process="Sejda PDF Desktop.exe", timeout=10)
                        windows = app.windows()
                        if windows:
                            window = windows[0]
                            print(f"   -> Found window: {window.window_text()}")
                        else:
                            print(f"   -> No windows found with process name")
                    except Exception as e:
                        print(f"   -> Method 2 failed: {e}")
                
                # Method 3: Try connecting to any window with "PDF" in title
                if not window:
                    try:
                        print(f"   -> Method 3: Connecting by PDF title...")
                        app = Application(backend="uia").connect(title_re=".*PDF.*", timeout=10)
                        windows = app.windows()
                        if windows:
                            window = windows[0]
                            print(f"   -> Found window: {window.window_text()}")
                        else:
                            print(f"   -> No windows found with PDF title")
                    except Exception as e:
                        print(f"   -> Method 3 failed: {e}")
                
                # Method 4: Try connecting to the most recent window
                if not window:
                    try:
                        print(f"   -> Method 4: Connecting to most recent window...")
                        app = Application(backend="uia").connect(active_only=True, timeout=10)
                        windows = app.windows()
                        if windows:
                            window = windows[0]
                            print(f"   -> Found active window: {window.window_text()}")
                        else:
                            print(f"   -> No active windows found")
                    except Exception as e:
                        print(f"   -> Method 4 failed: {e}")
                
                # Method 5: List all available windows for debugging
                if not window:
                    try:
                        print(f"   -> Method 5: Listing all available windows...")
                        all_apps = Application(backend="uia").connect()
                        all_windows = all_apps.windows()
                        print(f"   -> Found {len(all_windows)} total windows:")
                        for i, w in enumerate(all_windows[:10]):  # Show first 10
                            try:
                                title = w.window_text()
                                print(f"      {i+1}. '{title}'")
                            except:
                                print(f"      {i+1}. [Could not get title]")
                        
                        # Try to find any window that might be Sejda
                        for w in all_windows:
                            try:
                                title = w.window_text().lower()
                                if 'sejda' in title or 'pdf' in title:
                                    window = w
                                    app = all_apps
                                    print(f"   -> Found potential Sejda window: '{w.window_text()}'")
                                    break
                            except:
                                continue
                    except Exception as e:
                        print(f"   -> Method 5 failed: {e}")
                
                if not window:
                    raise Exception("Could not connect to any Sejda window using all methods")
                
                window.set_focus()
                print(f"   Successfully connected to: {window.window_text()}")
                
            except Exception as e:
                print(f"   Window connection failed: {e}")
                raise Exception(f"Sejda window connection failed: {e}")
            
            # Step 4: AUTOMATIC - Switch to Edit mode and detect form fields
            print(f"\nStep 4: Switching to EDIT MODE and detecting form fields...")
            try:
                # Multiple attempts to switch to Edit mode
                print(f"   -> Attempting to switch to Edit mode...")
                for attempt in range(5):  # More attempts
                    print(f"      -> Attempt {attempt + 1}/5: Ctrl+E")
                    window.type_keys("^e")  # Ctrl+E for Edit mode
                    time.sleep(3)  # Longer wait between attempts
                
                # Try clicking on the document to ensure focus
                print(f"   -> Clicking on document to focus...")
                rect = window.rectangle()
                center_x = (rect.left + rect.right) // 2
                center_y = (rect.top + rect.bottom) // 2
                window.click_input(coords=(center_x, center_y))
                time.sleep(3)
                
                # Try to access Forms/Fields section
                print(f"   -> Accessing Forms section...")
                window.type_keys("^+f")  # Ctrl+Shift+F (Forms shortcut)
                time.sleep(5)
                
                # Try clicking Forms menu for field detection
                print(f"   -> Looking for Forms menu...")
                try:
                    # Look for Forms menu
                    forms_menu = window.child_window(title="Forms", control_type="MenuItem")
                    if forms_menu.exists():
                        forms_menu.click()
                        time.sleep(2)
                        # Look for Detect Form Fields or Fill & Sign
                        detect_item = window.child_window(title_re=".*Detect.*|.*Fill.*", control_type="MenuItem")
                        if detect_item.exists():
                            detect_item.click()
                            print(f"   Form fields detection triggered!")
                        else:
                            print(f"   Detect Form Fields menu item not found")
                    else:
                        print(f"   Forms menu not found")
                except Exception as e:
                    print(f"   Menu clicking failed: {e}")
                
                # Wait for field detection to complete
                print(f"   Waiting 20 seconds for form fields to be detected...")
                time.sleep(20)
                
                # Try to verify we're in edit mode by looking for form controls
                print(f"   -> Verifying edit mode by looking for form controls...")
                try:
                    edit_controls = window.descendants(control_type="Edit")
                    print(f"   -> Found {len(edit_controls)} edit controls - edit mode appears active!")
                    
                    # Also look for any text controls
                    text_controls = window.descendants(control_type="Text")
                    print(f"   -> Found {len(text_controls)} text controls")
                    
                except Exception as e:
                    print(f"   -> Could not verify edit mode: {e}")
                
            except Exception as e:
                print(f"   Field detection failed: {e}")
                print(f"   -> Continuing anyway...")
            
            # Step 5: AUTOMATIC - Fill form fields in EDIT MODE with AI data
            if ai_data and len(ai_data) > 0:
                print(f"\nStep 5: Filling {len(ai_data)} form fields in EDIT MODE with AI data...")
                print(f"   AI Data to fill:")
                for i, (field_id, value) in enumerate(ai_data.items()):
                    print(f"      {i+1}. {field_id}: '{value}'")
                
                window.set_focus()
                filled_count = 0
                
                try:
                    # Click in the document area to ensure focus
                    rect = window.rectangle()
                    center_x = (rect.left + rect.right) // 2
                    center_y = (rect.top + rect.bottom) // 2
                    
                    print(f"   -> Clicking at center of Sejda window: ({center_x}, {center_y})")
                    window.click_input(coords=(center_x, center_y))
                    time.sleep(3)  # Wait longer for click to register
                    
                    # Try to navigate to first form field
                    print(f"   -> Navigating to first form field...")
                    window.type_keys("^{HOME}")  # Ctrl+Home to go to beginning
                    time.sleep(2)
                    
                    # Try to find and click on form fields directly
                    print(f"   -> Looking for form fields to click and fill...")
                    try:
                        # Look for text input controls
                        text_controls = window.descendants(control_type="Edit")
                        print(f"      -> Found {len(text_controls)} text input controls")
                        
                        for i, control in enumerate(text_controls[:len(ai_data)]):
                            try:
                                if i < len(list(ai_data.items())):
                                    field_id, value = list(ai_data.items())[i]
                                    print(f"      -> Clicking on control {i+1} for field: {field_id}")
                                    
                                    # Get control position and click on it
                                    control_rect = control.rectangle()
                                    control_center_x = (control_rect.left + control_rect.right) // 2
                                    control_center_y = (control_rect.top + control_rect.bottom) // 2
                                    
                                    window.click_input(coords=(control_center_x, control_center_y))
                                    time.sleep(2)  # Longer wait to see the click
                                    
                                    # Select all and type
                                    print(f"      -> Selecting existing text...")
                                    window.type_keys("^a")
                                    time.sleep(1)
                                    
                                    clean_value = str(value).replace('{', '{{').replace('}', '}}')
                                    print(f"      -> VISIBLY TYPING: '{clean_value}'")
                                    # Type slower so you can see it
                                    window.type_keys(clean_value, with_spaces=True, pause=0.5)
                                    time.sleep(2)  # Wait to see the typing
                                    
                                    # Commit the field
                                    print(f"      -> Committing field...")
                                    window.type_keys("{ENTER}")
                                    time.sleep(1)
                                    
                                    filled_count += 1
                                    print(f"      -> Control {i+1} filled with: '{clean_value}'")
                            except Exception as e:
                                print(f"      -> Error with control {i+1}: {e}")
                                continue
                                
                    except Exception as e:
                        print(f"      -> Direct control clicking failed: {e}")
                    
                    # Method 2: Try tabbing through fields as backup
                    if filled_count < len(ai_data):
                        print(f"   -> Method 2: Tab navigation backup...")
                        window.type_keys("^{HOME}")  # Go to beginning
                        time.sleep(2)
                        
                        for i, (field_id, value) in enumerate(ai_data.items()):
                            try:
                                print(f"      -> Field {i+1}/{len(ai_data)}: {field_id}")
                                
                                # Tab to next field (or stay on first field if i==0)
                                if i > 0:
                                    print(f"         -> Pressing TAB to next field...")
                                    window.type_keys("{TAB}")
                                    time.sleep(3.0)  # Wait longer for tab to register
                                
                                # Select all existing content in the field
                                print(f"         -> Selecting existing content (Ctrl+A)...")
                                window.type_keys("^a")  # Ctrl+A
                                time.sleep(1.5)
                                
                                # Type AI value
                                clean_value = str(value).replace('{', '{{').replace('}', '}}')
                                print(f"         -> VISIBLY TYPING: '{clean_value}'")
                                # Type slower so you can see it
                                window.type_keys(clean_value, with_spaces=True, pause=0.5)
                                time.sleep(2)  # Wait to see the typing
                                
                                # Commit the field by pressing Enter
                                print(f"         -> Committing field...")
                                window.type_keys("{ENTER}")
                                time.sleep(1)
                                
                                filled_count += 1
                                print(f"         Field {i+1} filled and committed successfully!")
                                
                            except Exception as e:
                                print(f"         Error filling field {field_id}: {e}")
                                continue
                    
                    
                    print(f"   AI filled {filled_count} form fields in EDIT MODE!")
                    
                except Exception as e:
                    print(f"   Form field filling failed: {e}")
                    import traceback
                    traceback.print_exc()
                
                if filled_count < len(ai_data):
                    print(f"   Only filled {filled_count}/{len(ai_data)} fields - some may be missing!")
            else:
                print(f"\nStep 5: Skipping AI fill (no data provided)")
            
            # Step 6: AUTOMATIC - Save the filled PDF
            print(f"\nStep 6: AUTOMATICALLY saving filled PDF...")
            try:
                window.set_focus()
                window.type_keys("^s")  # Ctrl+S
                time.sleep(3)
                print(f"   Save completed!")
            except Exception as e:
                print(f"   Save error: {e}")
            
            # Step 7: AUTOMATIC - Close Sejda
            print(f"\nStep 7: AUTOMATICALLY closing Sejda Desktop...")
            try:
                time.sleep(3)
                window.type_keys("%{F4}")  # Alt+F4
                time.sleep(3)
                print(f"   Sejda closed")
            except:
                # Force kill if Alt+F4 didn't work
                subprocess.run(['taskkill', '/F', '/IM', 'Sejda PDF Desktop.exe'], 
                             capture_output=True, timeout=5)
                print(f"   Sejda force-closed")
            
            # Step 8: Check if output exists
            print(f"\nStep 8: Checking for filled PDF...")
            
            # Sejda saves to the same location as input by default
            if os.path.exists(input_pdf):
                print(f"   Found filled PDF: {input_pdf}")
                return {
                    'success': True,
                    'output_path': input_pdf,
                    'message': 'PDF filled automatically and saved successfully'
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
            print(f"\nSejda automation failed: {e}")
            print(f"   Traceback: {error_msg}")
            
            # Try to kill Sejda
            try:
                subprocess.run(['taskkill', '/F', '/IM', 'Sejda PDF Desktop.exe'], 
                             capture_output=True, timeout=5)
            except:
                pass
            
            return {
                'success': False,
                'error': f'Sejda automation failed: {str(e)}'
            }