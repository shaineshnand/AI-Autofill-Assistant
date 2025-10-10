#!/usr/bin/env python
"""
Test script for the upload functionality
"""
import os
import sys
import django
import requests
from io import BytesIO

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_autofill_project.settings')
django.setup()

def test_upload():
    """Test the upload endpoint"""
    print("Testing upload endpoint...")
    
    # Check if test file exists
    test_file = 'test_form.png'
    if not os.path.exists(test_file):
        print(f"Test file {test_file} not found. Creating a simple test...")
        return False
    
    # Test the upload
    url = 'http://localhost:8000/upload/'
    
    with open(test_file, 'rb') as f:
        files = {'file': f}
        data = {'csrfmiddlewaretoken': 'test'}  # You might need to get a real CSRF token
        
        try:
            response = requests.post(url, files=files, data=data)
            print(f"Response status: {response.status_code}")
            print(f"Response content: {response.text}")
            
            if response.status_code == 200:
                print("✓ Upload successful!")
                return True
            else:
                print("✗ Upload failed!")
                return False
                
        except Exception as e:
            print(f"Error testing upload: {e}")
            return False

if __name__ == '__main__':
    test_upload()