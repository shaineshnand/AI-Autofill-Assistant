#!/usr/bin/env python
"""
Simple test for upload endpoint
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_autofill_project.settings')
django.setup()

def test_upload_endpoint():
    """Test the upload endpoint directly"""
    print("Testing upload endpoint...")
    
    try:
        from documents.views import upload_document
        from django.test import RequestFactory
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        # Create a test request
        factory = RequestFactory()
        
        # Create a test file
        if os.path.exists('test_form.png'):
            with open('test_form.png', 'rb') as f:
                file_content = f.read()
            
            # Create uploaded file
            uploaded_file = SimpleUploadedFile(
                'test_form.png',
                file_content,
                content_type='image/png'
            )
            
            # Create request
            request = factory.post('/upload/', {'file': uploaded_file})
            
            # Call the view
            response = upload_document(request)
            
            print(f"Response status: {response.status_code}")
            if hasattr(response, 'data'):
                print(f"Response data keys: {list(response.data.keys())}")
                if 'error' in response.data:
                    print(f"Error: {response.data['error']}")
                if 'traceback' in response.data:
                    print(f"Traceback: {response.data['traceback']}")
            else:
                print(f"Response content: {response.content.decode()[:200]}")
                
            return response.status_code == 200
            
        else:
            print("ERROR: No test file available")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    test_upload_endpoint()
