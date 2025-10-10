#!/usr/bin/env python
"""
Complete startup script for AI Autofill Assistant
Handles Django setup, Ollama integration, and everything needed to run the app
"""
import os
import sys
import subprocess
import time
import threading
import requests
import django
from django.core.management import execute_from_command_line

def print_banner():
    """Print startup banner"""
    print("=" * 60)
    print("AI AUTOFILL ASSISTANT - STARTUP")
    print("=" * 60)
    print("Setting up Django + Ollama integration...")
    print()

def setup_django():
    """Setup Django environment"""
    print("Setting up Django environment...")
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_autofill_project.settings')
    django.setup()
    print("Django environment ready")

def run_migrations():
    """Run database migrations"""
    print("Running database migrations...")
    try:
        execute_from_command_line(['manage.py', 'makemigrations'])
        execute_from_command_line(['manage.py', 'migrate'])
        print("Database migrations completed")
    except Exception as e:
        print(f"Migration error: {e}")

def create_superuser():
    """Create superuser if it doesn't exist"""
    print("Setting up admin user...")
    try:
        from django.contrib.auth.models import User
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            print("Superuser created: username=admin, password=admin123")
        else:
            print("Superuser already exists")
    except Exception as e:
        print(f"Superuser creation error: {e}")

def check_ollama_installation():
    """Check if Ollama is installed"""
    print("Checking Ollama installation...")
    try:
        result = subprocess.run(['ollama', '--version'], 
                              capture_output=True, text=True, 
                              encoding='utf-8', errors='ignore', timeout=5)
        if result.returncode == 0:
            print("Ollama is installed")
            return True
        else:
            print("Ollama not found")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("Ollama not found")
        return False

def start_ollama_service():
    """Start Ollama service in background"""
    print("Starting Ollama service...")
    try:
        # Start Ollama in background with proper encoding handling
        process = subprocess.Popen(['ollama', 'serve'], 
                                 stdout=subprocess.DEVNULL, 
                                 stderr=subprocess.DEVNULL,
                                 encoding='utf-8', errors='ignore')
        
        # Wait a bit for Ollama to start
        time.sleep(3)
        
        # Check if Ollama is running
        if check_ollama_running():
            print("Ollama service started successfully")
            return process
        else:
            print("Failed to start Ollama service")
            return None
    except Exception as e:
        print(f"Error starting Ollama: {e}")
        return None

def check_ollama_running():
    """Check if Ollama service is running"""
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=2)
        return response.status_code == 200
    except:
        return False

def download_ollama_model():
    """Download a default Ollama model"""
    print("Downloading Ollama model (llama2)...")
    try:
        result = subprocess.run(['ollama', 'pull', 'llama2'], 
                              capture_output=True, text=True, 
                              encoding='utf-8', errors='ignore', timeout=300)
        if result.returncode == 0:
            print("Model downloaded successfully")
        else:
            print("Model download failed, but continuing...")
    except subprocess.TimeoutExpired:
        print("Model download timed out, but continuing...")
    except Exception as e:
        print(f"Model download error: {e}")

def start_django_server():
    """Start Django development server"""
    print("Starting Django development server...")
    print("=" * 60)
    print("AI AUTOFILL ASSISTANT IS READY!")
    print("=" * 60)
    print("Access the application at: http://localhost:8000")
    print("=" * 60)
    print("Press Ctrl+C to stop the server")
    print()
    
    try:
        execute_from_command_line(['manage.py', 'runserver', '0.0.0.0:8000'])
    except KeyboardInterrupt:
        print("\nShutting down AI Autofill Assistant...")
        sys.exit(0)

def main():
    """Main startup function"""
    print_banner()
    
    # Setup Django (minimal setup)
    setup_django()
    
    # Handle Ollama
    ollama_process = None
    if check_ollama_installation():
        if not check_ollama_running():
            ollama_process = start_ollama_service()
            if ollama_process:
                # Download model in background
                model_thread = threading.Thread(target=download_ollama_model)
                model_thread.daemon = True
                model_thread.start()
    else:
        print("WARNING: Ollama not installed. AI features will use fallback responses.")
        print("   To install Ollama: https://ollama.ai/download")
    
    # Start Django server
    start_django_server()

if __name__ == '__main__':
    main()
