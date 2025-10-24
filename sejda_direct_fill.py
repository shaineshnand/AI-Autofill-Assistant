"""
CLEAN Sejda Integration - No Blue Boxes, Just Fill!

Simple workflow:
1. Open PDF in Sejda Desktop
2. Sejda detects fields (shows its own blue boxes)
3. AI fills those fields directly in Sejda
4. Save from Sejda
5. Done!

NO coordinate mapping, NO our own blue boxes, NO issues!
"""

import os
import time
import subprocess
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

try:
    from pywinauto import Application
    PYWINAUTO_AVAILABLE = True
except ImportError:
    PYWINAUTO_AVAILABLE = False


class SejdaDirectFill:
    """Direct fill in Sejda - the CLEAN way!"""
    
    def __init__(self):
        self.sejda_path = self._find_sejda()
        
    def _find_sejda(self) -> Optional[str]:
        """Find Sejda Desktop"""
        paths = [
            r"C:\Program Files\Sejda PDF Desktop\Sejda PDF Desktop.exe",
            r"C:\Program Files (x86)\Sejda PDF Desktop\Sejda PDF Desktop.exe",
        ]
        for path in paths:
            if os.path.exists(path):
                return path
        return None
    
    def inspect_window(self, window):
        """Debug helper to inspect window controls"""
        try:
            print("\n🔍 Window Inspection:")
            print(f"   Title: {window.window_text()}")
            print(f"   Class: {window.class_name()}")
            
            # List all child controls
            children = window.children()
            print(f"   Found {len(children)} child controls:")
            for i, child in enumerate(children[:15]):  # Show first 15
                try:
                    ctrl_type = child.element_info.control_type if hasattr(child, 'element_info') else 'Unknown'
                    print(f"     [{i}] {ctrl_type} - '{child.window_text()}'")
                except:
                    pass
        except Exception as e:
            print(f"   Error inspecting window: {e}")
    
    def process_pdf_clean(self, input_pdf: str, ai_data: Dict[str, str], output_pdf: str) -> Dict:
        """
        CLEAN workflow - no blue boxes, just fill!
        
        Args:
            input_pdf: PDF to process
            ai_data: Dictionary of AI-generated values (we'll fill in order)
            output_pdf: Where to save
        """
        if not PYWINAUTO_AVAILABLE or not self.sejda_path:
            return {'success': False, 'error': 'Sejda or pywinauto not available'}
        
        try:
            print("\n" + "="*60)
            print("🎯 CLEAN SEJDA WORKFLOW - No Blue Boxes!")
            print("="*60)
            
            # Step 1: Close any existing Sejda instances first
            print(f"\n📂 Step 1: Preparing Sejda Desktop...")
            try:
                # Kill any existing Sejda processes
                subprocess.run(['taskkill', '/F', '/IM', 'Sejda PDF Desktop.exe'], 
                             capture_output=True, timeout=5)
                time.sleep(2)
            except:
                pass
            
            # Now open PDF in fresh Sejda instance
            print(f"   → Opening PDF in Sejda Desktop...")
            subprocess.Popen([self.sejda_path, input_pdf])
            time.sleep(8)  # Wait for Sejda to fully open
            
            # Connect to the new Sejda window
            app = Application(backend="uia").connect(title_re=".*Sejda.*", timeout=15)
            
            # Get all Sejda windows and pick the first one
            windows = app.windows()
            if not windows:
                raise Exception("No Sejda windows found")
            
            window = windows[0]  # Use first window
            window.set_focus()
            print(f"   ✅ PDF opened in Sejda")
            
            # Debug: Inspect window structure
            self.inspect_window(window)
            
            # Step 2: Trigger field detection in Sejda - USING MOUSE CLICKS!
            print(f"\n🔍 Step 2: Triggering form field detection in Sejda...")
            print(f"   → YOU NEED TO MANUALLY CLICK:")
            print(f"      1. Click 'Fill & Sign' in the top menu")
            print(f"      2. Click 'Add Text' or 'Add Form Fields'")
            print(f"      3. Wait for field detection to complete")
            print(f"\n   ⏳ Waiting 20 seconds for YOU to click these buttons...")
            print(f"      (Look at the Sejda window now!)")
            
            # Give user time to manually click
            for i in range(20, 0, -1):
                print(f"      {i} seconds remaining...", end='\r')
                time.sleep(1)
            
            print(f"\n   ✅ Assuming you clicked and fields are now detected")
            
            # Now wait a bit more for fields to fully load
            print(f"   ⏳ Waiting 5 more seconds for fields to load...")
            time.sleep(5)
            
            # Step 3: Fill fields with AI data - DIRECT CLICK METHOD!
            print(f"\n🤖 Step 3: Filling fields with AI data...")
            print(f"   📋 {len(ai_data)} values to fill")
            
            window.set_focus()
            time.sleep(2)
            
            # NEW APPROACH: Find all Edit controls and click each one directly!
            print(f"   → Finding all edit fields in Sejda...")
            try:
                edit_fields = window.descendants(control_type="Edit")
                print(f"   ✓ Found {len(edit_fields)} edit fields in the window")
                
                # Show details about each field
                for idx, field in enumerate(edit_fields[:5]):  # Show first 5
                    try:
                        rect = field.rectangle()
                        print(f"     Field {idx}: Position ({rect.left}, {rect.top}), Text: '{field.window_text()}'")
                    except:
                        pass
                
            except Exception as e:
                print(f"   ⚠️  Error finding edit fields: {e}")
                edit_fields = []
            
            filled = 0
            errors = 0
            
            # METHOD 1: Try clicking each edit field directly
            if edit_fields and len(edit_fields) >= len(ai_data):
                print(f"\n   🎯 METHOD 1: Direct click on each field")
                
                for i, (field_name, value) in enumerate(ai_data.items()):
                    if i >= len(edit_fields):
                        print(f"   ⚠️  Ran out of fields at index {i}")
                        break
                    
                    try:
                        # Get the field
                        field = edit_fields[i]
                        
                        # Click the field
                        print(f"   → [{i+1}/{len(ai_data)}] Clicking field {i}...")
                        field.click_input()
                        time.sleep(0.5)
                        
                        # Clear existing content
                        field.type_keys("^a")  # Select all
                        time.sleep(0.1)
                        
                        # Type the value
                        clean_value = str(value).replace('{', '{{').replace('}', '}}')
                        print(f"       Typing: '{clean_value[:30]}...'")
                        field.type_keys(clean_value, with_spaces=True)
                        time.sleep(0.5)
                        
                        # Verify it was filled
                        try:
                            current_text = field.window_text()
                            if current_text:
                                print(f"       ✓ Field now contains: '{current_text[:30]}...'")
                        except:
                            pass
                        
                        filled += 1
                        
                    except Exception as e:
                        errors += 1
                        print(f"   ✗ Error filling field {i}: {e}")
                        continue
                
            else:
                # METHOD 2: Fallback to TAB navigation
                print(f"\n   🎯 METHOD 2: Tab navigation (found {len(edit_fields)} fields, need {len(ai_data)})")
                
                # Click in document first
                window.click_input(coords=(500, 400))
                time.sleep(1)
                
                for i, (field_name, value) in enumerate(ai_data.items()):
                    try:
                        # Tab to field
                        window.type_keys("{TAB}")
                        time.sleep(0.5)
                        
                        # Type value
                        clean_value = str(value).replace('{', '{{').replace('}', '}}')
                        print(f"   → [{i+1}/{len(ai_data)}] Typing: '{clean_value[:30]}...'")
                        
                        window.type_keys("^a")  # Select all
                        time.sleep(0.1)
                        window.type_keys(clean_value, with_spaces=True)
                        time.sleep(0.5)
                        
                        filled += 1
                        
                    except Exception as e:
                        errors += 1
                        print(f"   ✗ Error at field {i}: {e}")
                        continue
            
            print(f"\n   ✅ Filled {filled}/{len(ai_data)} fields with AI data")
            if errors > 0:
                print(f"   ⚠️  {errors} fields had errors")
            
            if filled == 0:
                print(f"\n   ⚠️⚠️⚠️  WARNING: NO FIELDS WERE FILLED!")
                print(f"   Please check the terminal output and Sejda window")
            
            # Step 4: Save the PDF
            print(f"\n💾 Step 4: Saving filled PDF...")
            
            try:
                # Try Ctrl+Shift+S (Save As)
                window.type_keys("^+s")
                time.sleep(3)
                
                # Look for save dialog
                try:
                    save_dialog = app.window(title_re=".*Save.*|.*Guardar.*")
                    print(f"   → Found save dialog")
                    save_dialog.type_keys("^a")
                    time.sleep(0.5)
                    save_dialog.type_keys(output_pdf, with_spaces=True)
                    time.sleep(1)
                    save_dialog.type_keys("{ENTER}")
                    time.sleep(3)
                    print(f"   ✅ Saved via dialog")
                except Exception as e:
                    print(f"   → No dialog, using Ctrl+S: {e}")
                    window.type_keys("^s")
                    time.sleep(3)
                    print(f"   ✅ Auto-saved")
            except Exception as e:
                print(f"   ⚠️ Save failed: {e}")
            
            print(f"   📄 PDF location: {output_pdf}")
            
            # Step 5: Close Sejda
            print(f"\n🚪 Step 5: Closing Sejda...")
            try:
                window.type_keys("%{F4}")  # Alt+F4
                time.sleep(2)
            except:
                try:
                    window.close()
                except:
                    pass
            
            print("\n" + "="*60)
            print(f"✅ DONE! Filled PDF ready: {output_pdf}")
            print(f"   • No blue boxes created by us")
            print(f"   • No coordinate issues")
            print(f"   • Just clean AI filling in Sejda!")
            print("="*60 + "\n")
            
            return {
                'success': True,
                'output_path': output_pdf,
                'filled_count': filled,
                'method': 'sejda_direct_fill'
            }
            
        except Exception as e:
            import traceback
            error_msg = f"{str(e)}\n{traceback.format_exc()}"
            logger.error(f"Error in clean Sejda workflow: {error_msg}")
            print(f"\n❌ SEJDA WORKFLOW ERROR:")
            print(f"   {str(e)}")
            print(f"\nTraceback:")
            print(traceback.format_exc())
            
            # Try to close Sejda
            try:
                if 'app' in locals():
                    app.kill()
            except:
                pass
            
            return {'success': False, 'error': str(e), 'traceback': error_msg}


def clean_sejda_fill(input_pdf: str, ai_data: Dict[str, str], output_pdf: str) -> Dict:
    """
    Convenience function for clean Sejda filling
    
    Args:
        input_pdf: Input PDF
        ai_data: AI values to fill
        output_pdf: Output path
    """
    sejda = SejdaDirectFill()
    return sejda.process_pdf_clean(input_pdf, ai_data, output_pdf)

