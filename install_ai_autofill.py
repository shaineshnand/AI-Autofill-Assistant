#!/usr/bin/env python3
"""
AI Autofill Assistant - Easy Installation Script
This script makes it super easy to integrate AI Autofill Assistant into any project.
"""

import os
import sys
import subprocess
from pathlib import Path

def print_banner():
    """Print installation banner"""
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║           AI AUTOFILL ASSISTANT - INTEGRATION               ║
    ║                                                              ║
    ║  🚀 Easy integration into any project                       ║
    ║  📄 PDF processing and AI-powered form filling              ║
    ║  🎯 Custom field editor with drag-and-drop                  ║
    ║  💬 Interactive AI chat assistant                           ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """)

def check_requirements():
    """Check if required tools are installed"""
    print("🔍 Checking requirements...")
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7+ required. Current version:", sys.version)
        return False
    
    print("✅ Python version:", sys.version.split()[0])
    
    # Check if pip is available
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      check=True, capture_output=True)
        print("✅ pip is available")
    except subprocess.CalledProcessError:
        print("❌ pip not found")
        return False
    
    return True

def get_project_info():
    """Get project information from user"""
    print("\n📋 Project Information")
    print("=" * 50)
    
    # Get target project path
    while True:
        target_path = input("Enter target project path: ").strip()
        if target_path:
            target_path = Path(target_path).resolve()
            if target_path.exists():
                break
            else:
                print("❌ Path does not exist. Please enter a valid path.")
        else:
            print("❌ Please enter a valid path.")
    
    # Get project type
    print("\nSelect project type:")
    print("1. Django")
    print("2. Flask") 
    print("3. Standalone")
    
    while True:
        choice = input("Enter choice (1-3): ").strip()
        if choice == "1":
            project_type = "django"
            break
        elif choice == "2":
            project_type = "flask"
            break
        elif choice == "3":
            project_type = "standalone"
            break
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")
    
    # Get API key
    api_key = input("Enter OpenAI API key (optional, can be set later): ").strip()
    
    return target_path, project_type, api_key

def install_dependencies(project_type):
    """Install required dependencies"""
    print(f"\n📦 Installing dependencies for {project_type}...")
    
    dependencies = [
        "pdfkit>=1.0.0",
        "weasyprint>=56.0", 
        "pytesseract>=0.3.8",
        "Pillow>=8.3.0",
        "opencv-python>=4.5.0",
        "python-dotenv>=0.19.0",
        "requests>=2.26.0",
        "reportlab>=3.6.0",
        "PyPDF2>=1.26.0",
        "openai>=0.27.0",
        "PyMuPDF>=1.20.0",
        "python-docx>=0.8.11",
        "pdfplumber>=0.6.0"
    ]
    
    if project_type == "django":
        dependencies.extend([
            "Django>=3.2.0",
            "djangorestframework>=3.14.0",
            "django-cors-headers>=3.13.0"
        ])
    elif project_type == "flask":
        dependencies.extend([
            "Flask>=2.0.0",
            "Flask-CORS>=3.0.10"
        ])
    
    for dep in dependencies:
        try:
            print(f"Installing {dep}...")
            subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                          check=True, capture_output=True)
            print(f"✅ {dep} installed")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {dep}: {e}")
            return False
    
    return True

def run_integration_setup(target_path, project_type, api_key):
    """Run the integration setup"""
    print(f"\n🔧 Setting up AI Autofill Assistant for {project_type}...")
    
    try:
        # Run the integration setup script
        cmd = [sys.executable, "integration_setup.py", str(target_path), project_type]
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Integration setup completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Integration setup failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def create_env_file(target_path, api_key):
    """Create environment file"""
    if api_key:
        env_content = f"""# AI Autofill Assistant Environment Configuration
AI_AUTOFILL_ENABLED=true
AI_AUTOFILL_DEBUG=false
AI_AUTOFILL_API_KEY={api_key}
AI_AUTOFILL_MAX_FILE_SIZE=10485760
AI_AUTOFILL_ALLOWED_EXTENSIONS=pdf,docx,txt
AI_AUTOFILL_CUSTOM_FIELDS_ENABLED=true
AI_AUTOFILL_CHAT_ENABLED=true
AI_AUTOFILL_PDF_GENERATION_ENABLED=true
"""
        env_file = target_path / "ai_autofill_integration" / ".env"
        env_file.write_text(env_content)
        print("✅ Environment file created")

def show_next_steps(project_type, target_path):
    """Show next steps to user"""
    print("\n🎉 Installation Complete!")
    print("=" * 50)
    
    integration_dir = target_path / "ai_autofill_integration"
    
    if project_type == "django":
        print(f"""
📁 Integration files created in: {integration_dir}

🚀 Next Steps:
1. Add to your Django settings.py:
   INSTALLED_APPS = [
       # ... your existing apps
       'ai_autofill_integration.ai_autofill_assistant',
   ]

2. Add to your main urls.py:
   path('ai-autofill/', include('ai_autofill_integration.ai_autofill_assistant.urls')),

3. Run migrations:
   python manage.py makemigrations ai_autofill_assistant
   python manage.py migrate

4. Run your Django server:
   python manage.py runserver

5. Access AI Autofill Assistant at: http://localhost:8000/ai-autofill/
""")
    
    elif project_type == "flask":
        print(f"""
📁 Integration files created in: {integration_dir}

🚀 Next Steps:
1. Add to your Flask app:
   from ai_autofill_integration.api.blueprint import ai_autofill_bp
   app.register_blueprint(ai_autofill_bp)

2. Run your Flask server:
   python app.py

3. Access AI Autofill Assistant at: http://localhost:5000/ai-autofill/
""")
    
    elif project_type == "standalone":
        print(f"""
📁 Integration files created in: {integration_dir}

🚀 Next Steps:
1. Navigate to integration directory:
   cd {integration_dir}

2. Install dependencies:
   pip install -r requirements.txt

3. Run the standalone server:
   python server.py

4. Access AI Autofill Assistant at: http://localhost:5000/
""")
    
    print(f"""
📚 Documentation:
- Integration Guide: {integration_dir}/AI_AUTOFILL_INTEGRATION_PACKAGE.md
- Example Usage: {integration_dir}/static/js/custom-field-example.html

🔧 Configuration:
- Environment file: {integration_dir}/.env
- Settings: {integration_dir}/settings.py

🎯 Features Available:
- PDF Processing & AI Autofill
- Custom Field Editor with Drag & Drop
- Interactive AI Chat Assistant
- PDF Generation & Download
- Export/Import Field Data

Happy coding! 🚀
""")

def main():
    """Main installation function"""
    print_banner()
    
    # Check requirements
    if not check_requirements():
        print("❌ Requirements not met. Please install required tools.")
        sys.exit(1)
    
    # Get project information
    target_path, project_type, api_key = get_project_info()
    
    # Install dependencies
    if not install_dependencies(project_type):
        print("❌ Failed to install dependencies.")
        sys.exit(1)
    
    # Run integration setup
    if not run_integration_setup(target_path, project_type, api_key):
        print("❌ Integration setup failed.")
        sys.exit(1)
    
    # Create environment file
    create_env_file(target_path, api_key)
    
    # Show next steps
    show_next_steps(project_type, target_path)

if __name__ == "__main__":
    main()
