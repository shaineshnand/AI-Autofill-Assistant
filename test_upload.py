#!/usr/bin/env python
"""
Test script to upload a document to the AI Autofill Assistant
"""
import requests
import os

def test_upload():
    """Test uploading the test form"""
    url = "http://localhost:8000/api/documents/upload/"
    
    # Check if test form exists
    if not os.path.exists("test_form.png"):
        print("ERROR: Test form not found. Please run create_test_document.py first.")
        return
    
    # Prepare the file for upload
    with open("test_form.png", "rb") as f:
        files = {"file": ("test_form.png", f, "image/png")}
        
        try:
            print("Uploading test form...")
            response = requests.post(url, files=files)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print("SUCCESS: Upload successful!")
                    print(f"Document ID: {data['document_id']}")
                    print(f"Total blank spaces found: {data['result']['total_blanks']}")
                    print(f"Extracted text preview: {data['result']['extracted_text'][:100]}...")
                    
                    # Test chat functionality
                    test_chat(data['document_id'])
                else:
                    print("ERROR: Upload failed:", data.get('error', 'Unknown error'))
            else:
                print(f"ERROR: Upload failed with status code: {response.status_code}")
                print(f"Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("ERROR: Could not connect to server. Make sure the Django server is running.")
        except Exception as e:
            print(f"ERROR: Error during upload: {e}")

def test_chat(doc_id):
    """Test chat functionality"""
    url = f"http://localhost:8000/api/chat/{doc_id}/"
    
    test_messages = [
        "Hello, can you help me fill out this form?",
        "What fields do you see in this document?",
        "Can you suggest content for the name field?"
    ]
    
    print("\nTesting chat functionality...")
    
    for message in test_messages:
        try:
            print(f"User: {message}")
            response = requests.post(url, json={"message": message})
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"Bot: {data['response']}")
                else:
                    print(f"ERROR: Chat failed: {data.get('error', 'Unknown error')}")
            else:
                print(f"ERROR: Chat failed with status code: {response.status_code}")
                
        except Exception as e:
            print(f"ERROR: Error during chat: {e}")
        
        print("-" * 50)

def test_ollama_status():
    """Test Ollama status"""
    url = "http://localhost:8000/api/chat/ollama/status/"
    
    try:
        print("Checking Ollama status...")
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('running'):
                print("SUCCESS: Ollama is running!")
                print(f"Available models: {data.get('models', [])}")
            else:
                print("WARNING: Ollama is not running. AI features will use fallback responses.")
        else:
            print(f"ERROR: Failed to check Ollama status: {response.status_code}")
            
    except Exception as e:
        print(f"ERROR: Error checking Ollama status: {e}")

if __name__ == "__main__":
    print("Testing AI Autofill Assistant")
    print("=" * 50)
    
    # Test Ollama status first
    test_ollama_status()
    print()
    
    # Test upload
    test_upload()
    
    print("\nTesting completed!")
    print("You can also test manually at: http://localhost:8000")
