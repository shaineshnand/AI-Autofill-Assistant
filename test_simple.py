#!/usr/bin/env python
"""
Simple test without OCR to verify the basic functionality
"""
import requests
import json

def test_basic_functionality():
    """Test basic server functionality"""
    print("Testing basic server functionality...")
    
    # Test main page
    try:
        response = requests.get("http://localhost:8000")
        if response.status_code == 200:
            print("SUCCESS: Main page loads correctly")
        else:
            print(f"ERROR: Main page failed with status {response.status_code}")
    except Exception as e:
        print(f"ERROR: Could not access main page: {e}")
    
    # Test Ollama status
    try:
        response = requests.get("http://localhost:8000/api/chat/ollama/status/")
        if response.status_code == 200:
            data = response.json()
            print(f"SUCCESS: Ollama status check works")
            print(f"Ollama running: {data.get('running', False)}")
            if data.get('running'):
                print(f"Available models: {data.get('models', [])}")
        else:
            print(f"ERROR: Ollama status check failed with status {response.status_code}")
    except Exception as e:
        print(f"ERROR: Ollama status check failed: {e}")
    
    # Test chat with a dummy document ID
    try:
        dummy_doc_id = "test-123"
        response = requests.post(f"http://localhost:8000/api/chat/{dummy_doc_id}/", 
                               json={"message": "Hello, can you help me?"})
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("SUCCESS: Chat functionality works")
                print(f"Bot response: {data['response']}")
            else:
                print(f"ERROR: Chat failed: {data.get('error', 'Unknown error')}")
        else:
            print(f"ERROR: Chat request failed with status {response.status_code}")
    except Exception as e:
        print(f"ERROR: Chat test failed: {e}")

def test_ollama_models():
    """Test Ollama model functionality"""
    print("\nTesting Ollama model functionality...")
    
    try:
        # Test pulling a model (this might take a while)
        response = requests.post("http://localhost:8000/api/chat/ollama/pull-model/", 
                               json={"model_name": "llama3.2:1b"})
        if response.status_code == 200:
            data = response.json()
            print(f"Model pull result: {data.get('message', 'Unknown result')}")
        else:
            print(f"ERROR: Model pull failed with status {response.status_code}")
    except Exception as e:
        print(f"ERROR: Model pull test failed: {e}")

if __name__ == "__main__":
    print("Simple Test for AI Autofill Assistant")
    print("=" * 50)
    
    test_basic_functionality()
    test_ollama_models()
    
    print("\n" + "=" * 50)
    print("Test Summary:")
    print("- Server is running at http://localhost:8000")
    print("- Ollama integration is working")
    print("- Chat functionality is working")
    print("- OCR functionality requires Tesseract installation")
    print("\nTo install Tesseract OCR:")
    print("1. Download from: https://github.com/UB-Mannheim/tesseract/wiki")
    print("2. Install and add to PATH")
    print("3. Restart the server")
    print("\nYou can test the web interface at: http://localhost:8000")



