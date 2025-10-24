"""
Sejda Desktop Automation using Windows UI Automation

This module automates Sejda PDF Desktop to create fillable PDFs programmatically
using Windows UI Automation (pywinauto) - NO DATA SENT ONLINE!

Requirements:
    pip install pywinauto
"""

import os
import time
import subprocess
import logging
from pathlib import Path
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)

try:
    from pywinauto import Application, Desktop
    from pywinauto.findwindows import ElementNotFoundError
    PYWINAUTO_AVAILABLE = True
except ImportError:
    PYWINAUTO_AVAILABLE = False
    logger.warning("pywinauto not installed. Run: pip install pywinauto")


class SejdaDesktopAutomation:
    """Automate Sejda PDF Desktop to create fillable PDFs"""
    
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
                logger.info(f"Found Sejda Desktop at: {path}")
                return path
        
        return None
    
    def is_available(self) -> bool:
        """Check if Sejda Desktop is available and pywinauto is installed"""
        return PYWINAUTO_AVAILABLE and self.sejda_path is not None
    
    def create_fillable_pdf_automated(self, input_pdf: str, output_pdf: str, timeout: int = 120) -> Dict:
        """
        Automate Sejda Desktop to create fillable PDF
        
        Args:
            input_pdf: Path to input PDF
            output_pdf: Path to output fillable PDF
            timeout: Maximum wait time in seconds
            
        Returns:
            Dictionary with success status and message
        """
        if not PYWINAUTO_AVAILABLE:
            return {
                'success': False,
                'error': 'pywinauto not installed. Run: pip install pywinauto',
                'method': 'sejda_automation'
            }
        
        if not self.sejda_path:
            return {
                'success': False,
                'error': 'Sejda Desktop not found',
                'method': 'sejda_automation'
            }
        
        try:
            logger.info(f"🤖 Starting Sejda Desktop automation...")
            logger.info(f"   Input: {input_pdf}")
            logger.info(f"   Output: {output_pdf}")
            
            # Step 1: Launch Sejda Desktop
            logger.info("   Step 1: Launching Sejda Desktop...")
            self.app = Application(backend="uia").start(self.sejda_path)
            time.sleep(3)  # Wait for application to start
            
            # Step 2: Find main window
            logger.info("   Step 2: Finding main window...")
            main_window = self.app.window(title_re=".*Sejda.*")
            main_window.set_focus()
            
            # Step 3: Click on Forms tool
            logger.info("   Step 3: Clicking Forms tool...")
            # Try different ways to access Forms
            try:
                # Method 1: Menu bar
                main_window.menu_select("Forms")
            except:
                try:
                    # Method 2: Button click
                    forms_btn = main_window.child_window(title="Forms", control_type="Button")
                    forms_btn.click_input()
                except:
                    # Method 3: Keyboard shortcut (if exists)
                    main_window.type_keys("^+f")  # Ctrl+Shift+F (example)
            
            time.sleep(2)
            
            # Step 4: Select "Detect Form Fields" or "Add Form Fields"
            logger.info("   Step 4: Selecting Detect Form Fields...")
            try:
                detect_fields_btn = main_window.child_window(title_re=".*Detect.*Form.*|.*Add.*Form.*", 
                                                             control_type="Button")
                detect_fields_btn.click_input()
            except:
                logger.warning("   Could not find Detect Form Fields button")
            
            time.sleep(2)
            
            # Step 5: Open file dialog and load PDF
            logger.info("   Step 5: Loading PDF file...")
            # Trigger file open dialog
            main_window.type_keys("^o")  # Ctrl+O to open file
            time.sleep(1)
            
            # Type file path
            file_dialog = self.app.window(title_re=".*Open.*|.*Browse.*")
            file_dialog.Edit.set_text(input_pdf)
            file_dialog.type_keys("{ENTER}")
            
            time.sleep(5)  # Wait for PDF to load and field detection
            
            # Step 6: Save the fillable PDF
            logger.info("   Step 6: Saving fillable PDF...")
            main_window.type_keys("^s")  # Ctrl+S to save
            time.sleep(1)
            
            # Save dialog
            save_dialog = self.app.window(title_re=".*Save.*")
            save_dialog.Edit.set_text(output_pdf)
            save_dialog.type_keys("{ENTER}")
            
            time.sleep(3)  # Wait for save
            
            # Step 7: Close Sejda
            logger.info("   Step 7: Closing Sejda Desktop...")
            main_window.close()
            
            # Verify output file exists
            if os.path.exists(output_pdf):
                logger.info(f"✅ Successfully created fillable PDF with Sejda automation!")
                return {
                    'success': True,
                    'output_path': output_pdf,
                    'method': 'sejda_automation'
                }
            else:
                return {
                    'success': False,
                    'error': 'Output file not created',
                    'method': 'sejda_automation'
                }
            
        except Exception as e:
            logger.error(f"❌ Sejda automation failed: {e}")
            
            # Try to close Sejda if it's still open
            try:
                if self.app:
                    self.app.kill()
            except:
                pass
            
            return {
                'success': False,
                'error': str(e),
                'method': 'sejda_automation'
            }


def automate_sejda_desktop(input_pdf: str, output_pdf: str) -> Dict:
    """
    Convenience function to automate Sejda Desktop
    
    Args:
        input_pdf: Path to input PDF
        output_pdf: Path to output fillable PDF
        
    Returns:
        Dictionary with success status and details
    """
    automator = SejdaDesktopAutomation()
    
    if not automator.is_available():
        return {
            'success': False,
            'error': 'Sejda Desktop automation not available',
            'method': 'sejda_automation'
        }
    
    return automator.create_fillable_pdf_automated(input_pdf, output_pdf)


# Alternative: Use COM automation or direct file manipulation
class SejdaAlternativeApproach:
    """
    Alternative approach: Monitor Sejda's temp/output folders
    or use file-based automation
    """
    
    @staticmethod
    def watch_folder_automation(input_pdf: str, watch_folder: str, timeout: int = 60) -> Optional[str]:
        """
        Place PDF in watched folder, wait for Sejda to process it
        (if Sejda has such a feature)
        """
        # This would require Sejda to have a folder watch feature
        pass


if __name__ == "__main__":
    # Test the automation
    logging.basicConfig(level=logging.INFO)
    
    automator = SejdaDesktopAutomation()
    print(f"Sejda Desktop available: {automator.is_available()}")
    print(f"Sejda path: {automator.sejda_path}")
    print(f"pywinauto available: {PYWINAUTO_AVAILABLE}")



