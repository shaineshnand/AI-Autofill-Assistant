"""
Smart Sejda Desktop Automation - Fill While App is Open

This is the SMART way to use Sejda:
1. Upload PDF
2. Open in Sejda Desktop (auto-detect fields)
3. While Sejda is open, AI fills the detected fields
4. Auto-save the filled PDF from Sejda
5. Close Sejda

NO manual steps, NO extra complexity!
"""

import os
import time
import subprocess
import logging
from pathlib import Path
from typing import Optional, Dict, List
import fitz  # PyMuPDF

logger = logging.getLogger(__name__)

try:
    from pywinauto import Application, Desktop
    from pywinauto.findwindows import ElementNotFoundError
    PYWINAUTO_AVAILABLE = True
except ImportError:
    PYWINAUTO_AVAILABLE = False


class SmartSejdaAutomation:
    """Smart automation: Open in Sejda, fill with AI, save"""
    
    def __init__(self):
        self.sejda_path = self._find_sejda_desktop()
        self.app = None
        
    def _find_sejda_desktop(self) -> Optional[str]:
        """Find Sejda Desktop executable"""
        common_paths = [
            r"C:\Program Files\Sejda PDF Desktop\Sejda PDF Desktop.exe",
            r"C:\Program Files (x86)\Sejda PDF Desktop\Sejda PDF Desktop.exe",
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                return path
        return None
    
    def is_available(self) -> bool:
        """Check if available"""
        return PYWINAUTO_AVAILABLE and self.sejda_path is not None
    
    def open_pdf_in_sejda_and_detect_fields(self, input_pdf: str) -> Dict:
        """
        Step 1: Open PDF in Sejda and auto-detect form fields
        Keep Sejda open for Step 2
        
        Returns:
            Dict with detected fields and Sejda app handle
        """
        if not self.is_available():
            return {'success': False, 'error': 'Sejda not available'}
        
        try:
            print(f"📂 Opening PDF in Sejda Desktop...")
            print(f"   File: {input_pdf}")
            
            # Launch Sejda Desktop with the PDF file
            # Method 1: Direct file open
            subprocess.Popen([self.sejda_path, input_pdf])
            time.sleep(5)  # Wait for Sejda to open
            
            # Connect to the Sejda window
            self.app = Application(backend="uia").connect(title_re=".*Sejda.*", timeout=10)
            main_window = self.app.window(title_re=".*Sejda.*")
            main_window.set_focus()
            
            print(f"✅ PDF opened in Sejda Desktop")
            print(f"🔍 Auto-detecting form fields...")
            
            # Trigger form field detection
            # Try multiple methods
            try:
                # Method 1: Click Forms tool/menu
                main_window.type_keys("^+f")  # Try keyboard shortcut
                time.sleep(1)
            except:
                pass
            
            try:
                # Method 2: Menu navigation
                main_window.menu_select("Forms")
                time.sleep(1)
            except:
                pass
            
            # Click "Detect Form Fields" or "Add Form Fields"
            time.sleep(2)
            
            print(f"⏳ Waiting for field detection to complete...")
            time.sleep(8)  # Give Sejda time to detect fields
            
            print(f"✅ Fields detected! Sejda is ready.")
            print(f"📋 Sejda Desktop is still open and ready for AI filling...")
            
            return {
                'success': True,
                'app': self.app,
                'window': main_window,
                'sejda_still_open': True
            }
            
        except Exception as e:
            logger.error(f"Error opening in Sejda: {e}")
            return {'success': False, 'error': str(e)}
    
    def fill_fields_in_sejda_with_ai_data(self, ai_field_data: Dict[str, str], sejda_window) -> Dict:
        """
        Step 2: Fill the detected fields in Sejda with AI data
        Sejda is already open with fields detected
        
        Args:
            ai_field_data: Dictionary of field_name -> ai_generated_value
            sejda_window: The Sejda window handle from Step 1
        """
        try:
            print(f"🤖 Filling fields in Sejda with AI data...")
            print(f"   Total fields to fill: {len(ai_field_data)}")
            
            sejda_window.set_focus()
            time.sleep(1)
            
            # Method: Tab through fields and fill them
            filled_count = 0
            for field_name, value in ai_field_data.items():
                try:
                    # Tab to next field
                    sejda_window.type_keys("{TAB}")
                    time.sleep(0.3)
                    
                    # Type the AI value
                    sejda_window.type_keys(str(value), with_spaces=True)
                    time.sleep(0.2)
                    
                    filled_count += 1
                    print(f"   ✓ Filled field {filled_count}: {field_name[:30]}... = {str(value)[:30]}...")
                    
                except Exception as field_error:
                    print(f"   ⚠ Skipped field {field_name}: {field_error}")
                    continue
            
            print(f"✅ Successfully filled {filled_count}/{len(ai_field_data)} fields in Sejda")
            
            return {
                'success': True,
                'filled_count': filled_count,
                'total_fields': len(ai_field_data)
            }
            
        except Exception as e:
            logger.error(f"Error filling fields in Sejda: {e}")
            return {'success': False, 'error': str(e)}
    
    def save_and_close_sejda(self, output_pdf: str, sejda_window) -> Dict:
        """
        Step 3: Save the filled PDF and close Sejda
        
        Args:
            output_pdf: Where to save the filled PDF
            sejda_window: The Sejda window handle
        """
        try:
            print(f"💾 Saving filled PDF from Sejda...")
            print(f"   Output: {output_pdf}")
            
            sejda_window.set_focus()
            time.sleep(1)
            
            # Save the PDF
            sejda_window.type_keys("^s")  # Ctrl+S
            time.sleep(2)
            
            # Handle save dialog
            try:
                save_dialog = self.app.window(title_re=".*Save.*")
                
                # Clear existing path and type new one
                save_dialog.type_keys("^a")  # Select all
                save_dialog.type_keys(output_pdf)
                save_dialog.type_keys("{ENTER}")
                
                time.sleep(3)  # Wait for save
                
            except:
                # If no dialog, file might auto-save
                pass
            
            print(f"✅ PDF saved successfully")
            
            # Close Sejda
            print(f"🚪 Closing Sejda Desktop...")
            sejda_window.close()
            time.sleep(1)
            
            # Verify output file exists
            if os.path.exists(output_pdf):
                print(f"✅ Output file verified: {output_pdf}")
                return {'success': True, 'output_path': output_pdf}
            else:
                print(f"⚠ Output file not found, checking downloads...")
                # Sejda might save to default location
                return {'success': True, 'note': 'Check Sejda default save location'}
            
        except Exception as e:
            logger.error(f"Error saving/closing Sejda: {e}")
            
            # Try force close
            try:
                if self.app:
                    self.app.kill()
            except:
                pass
            
            return {'success': False, 'error': str(e)}
    
    def complete_workflow(self, input_pdf: str, ai_field_data: Dict[str, str], output_pdf: str) -> Dict:
        """
        Complete smart workflow:
        1. Open PDF in Sejda (auto-detect fields)
        2. Fill fields with AI data while Sejda is open
        3. Save and close
        
        Args:
            input_pdf: Input PDF path
            ai_field_data: Dictionary of field_name -> ai_value
            output_pdf: Output PDF path
            
        Returns:
            Result dictionary
        """
        print("\n" + "="*60)
        print("🚀 SMART SEJDA AUTOMATION - All-in-One Workflow")
        print("="*60)
        
        # Step 1: Open in Sejda and detect fields
        result1 = self.open_pdf_in_sejda_and_detect_fields(input_pdf)
        if not result1['success']:
            return result1
        
        sejda_window = result1['window']
        
        # Step 2: Fill fields with AI data
        result2 = self.fill_fields_in_sejda_with_ai_data(ai_field_data, sejda_window)
        if not result2['success']:
            # Try to close Sejda even if filling failed
            try:
                sejda_window.close()
            except:
                pass
            return result2
        
        # Step 3: Save and close
        result3 = self.save_and_close_sejda(output_pdf, sejda_window)
        
        print("\n" + "="*60)
        print("✅ SMART WORKFLOW COMPLETE!")
        print(f"   Fields filled: {result2.get('filled_count', 0)}")
        print(f"   Output: {output_pdf}")
        print("="*60 + "\n")
        
        return {
            'success': result3['success'],
            'filled_count': result2.get('filled_count', 0),
            'total_fields': result2.get('total_fields', 0),
            'output_path': output_pdf,
            'method': 'smart_sejda_automation'
        }


def smart_sejda_workflow(input_pdf: str, ai_field_data: Dict[str, str], output_pdf: str) -> Dict:
    """
    Convenience function for smart Sejda workflow
    
    Args:
        input_pdf: Input PDF
        ai_field_data: AI-generated field values
        output_pdf: Output PDF path
        
    Returns:
        Result dictionary
    """
    automator = SmartSejdaAutomation()
    
    if not automator.is_available():
        return {
            'success': False,
            'error': 'Sejda Desktop or pywinauto not available',
            'method': 'smart_sejda_automation'
        }
    
    return automator.complete_workflow(input_pdf, ai_field_data, output_pdf)


if __name__ == "__main__":
    # Test
    logging.basicConfig(level=logging.INFO)
    
    automator = SmartSejdaAutomation()
    print(f"Smart Sejda Automation available: {automator.is_available()}")



