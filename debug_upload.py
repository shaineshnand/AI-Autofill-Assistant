#!/usr/bin/env python
"""
Debug script for upload functionality
"""
import os
import sys
import django
import traceback

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_autofill_project.settings')
django.setup()

def debug_upload():
    """Debug the upload functionality"""
    print("Debugging upload functionality...")
    
    try:
        from documents.views import DocumentProcessor
        processor = DocumentProcessor()
        print("SUCCESS: DocumentProcessor created successfully")
        
        # Test with a simple image
        if os.path.exists('test_form.png'):
            print("SUCCESS: Test file found")
            try:
                result = processor.process_document('test_form.png')
                print("SUCCESS: Document processing successful")
                print(f"Fields detected: {len(result.get('blank_spaces', []))}")
                return True
            except Exception as e:
                print(f"ERROR: Error processing document: {e}")
                traceback.print_exc()
                return False
        else:
            print("ERROR: No test file available")
            return False
            
    except Exception as e:
        print(f"ERROR: Error creating DocumentProcessor: {e}")
        traceback.print_exc()
        return False

if __name__ == '__main__':
    debug_upload()
