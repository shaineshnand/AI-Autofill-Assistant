#!/usr/bin/env python3
"""
AI Autofill Assistant - Integration Setup Script
This script helps integrate the AI Autofill Assistant into any existing project.
"""

import os
import shutil
import json
import sys
from pathlib import Path

class AIAutofillIntegrator:
    def __init__(self, target_project_path):
        self.target_project_path = Path(target_project_path)
        self.source_path = Path(__file__).parent
        self.integration_config = {}
        
    def setup_integration(self, project_type="django"):
        """Setup AI Autofill Assistant integration"""
        print(f"🚀 Setting up AI Autofill Assistant for {project_type} project...")
        
        # Create integration directory
        self.create_integration_directory()
        
        # Copy core files
        self.copy_core_files()
        
        # Setup project-specific integration
        if project_type == "django":
            self.setup_django_integration()
        elif project_type == "flask":
            self.setup_flask_integration()
        elif project_type == "standalone":
            self.setup_standalone_integration()
        
        # Create configuration files
        self.create_configuration_files()
        
        # Generate integration code
        self.generate_integration_code(project_type)
        
        print("✅ AI Autofill Assistant integration complete!")
        print(f"📁 Integration files created in: {self.target_project_path / 'ai_autofill_integration'}")
        
    def create_integration_directory(self):
        """Create integration directory structure"""
        integration_dir = self.target_project_path / "ai_autofill_integration"
        integration_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (integration_dir / "core").mkdir(exist_ok=True)
        (integration_dir / "static").mkdir(exist_ok=True)
        (integration_dir / "static" / "js").mkdir(exist_ok=True)
        (integration_dir / "static" / "css").mkdir(exist_ok=True)
        (integration_dir / "templates").mkdir(exist_ok=True)
        (integration_dir / "api").mkdir(exist_ok=True)
        
    def copy_core_files(self):
        """Copy core AI Autofill Assistant files"""
        integration_dir = self.target_project_path / "ai_autofill_integration"
        
        # Copy Python files
        python_files = [
            "html_pdf_processor.py",
            "ai_data_generator.py", 
            "field_detector.py"
        ]
        
        for file in python_files:
            source = self.source_path / file
            if source.exists():
                shutil.copy2(source, integration_dir / "core" / file)
        
        # Copy JavaScript files
        js_files = [
            "static/js/main.js",
            "static/js/custom-field-editor.js"
        ]
        
        for file in js_files:
            source = self.source_path / file
            if source.exists():
                target = integration_dir / file
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
        
        # Copy CSS files
        css_files = [
            "static/css/style.css"
        ]
        
        for file in css_files:
            source = self.source_path / file
            if source.exists():
                target = integration_dir / file
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
        
        # Copy templates
        template_files = [
            "templates/index.html"
        ]
        
        for file in template_files:
            source = self.source_path / file
            if source.exists():
                target = integration_dir / file
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
    
    def setup_django_integration(self):
        """Setup Django-specific integration"""
        integration_dir = self.target_project_path / "ai_autofill_integration"
        
        # Create Django app structure
        (integration_dir / "ai_autofill_assistant").mkdir(exist_ok=True)
        
        # Create Django app files
        self.create_django_app_files(integration_dir)
        
        # Create URL configuration
        self.create_django_urls(integration_dir)
        
        # Create views
        self.create_django_views(integration_dir)
        
        # Create models
        self.create_django_models(integration_dir)
        
    def setup_flask_integration(self):
        """Setup Flask-specific integration"""
        integration_dir = self.target_project_path / "ai_autofill_integration"
        
        # Create Flask blueprint
        self.create_flask_blueprint(integration_dir)
        
        # Create Flask routes
        self.create_flask_routes(integration_dir)
        
    def setup_standalone_integration(self):
        """Setup standalone integration"""
        integration_dir = self.target_project_path / "ai_autofill_integration"
        
        # Create standalone server
        self.create_standalone_server(integration_dir)
        
        # Create HTML interface
        self.create_standalone_interface(integration_dir)
    
    def create_django_app_files(self, integration_dir):
        """Create Django app files"""
        app_dir = integration_dir / "ai_autofill_assistant"
        
        # Create __init__.py
        (app_dir / "__init__.py").write_text("")
        
        # Create apps.py
        apps_py = '''from django.apps import AppConfig

class AiAutofillAssistantConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ai_autofill_assistant'
    verbose_name = 'AI Autofill Assistant'
'''
        (app_dir / "apps.py").write_text(apps_py)
        
        # Create admin.py
        admin_py = '''from django.contrib import admin
from .models import Document, CustomField

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['filename', 'created_at', 'processed']
    list_filter = ['processed', 'created_at']
    search_fields = ['filename']

@admin.register(CustomField)
class CustomFieldAdmin(admin.ModelAdmin):
    list_display = ['field_id', 'field_type', 'x', 'y', 'value']
    list_filter = ['field_type', 'created_at']
'''
        (app_dir / "admin.py").write_text(admin_py)
    
    def create_django_urls(self, integration_dir):
        """Create Django URL configuration"""
        app_dir = integration_dir / "ai_autofill_assistant"
        
        urls_py = '''from django.urls import path
from . import views

app_name = 'ai_autofill_assistant'

urlpatterns = [
    path('', views.index, name='index'),
    path('upload-pdf/', views.upload_pdf, name='upload_pdf'),
    path('process-document/<int:document_id>/', views.process_document, name='process_document'),
    path('ai-fill/<int:document_id>/', views.ai_fill, name='ai_fill'),
    path('add-field/', views.add_field, name='add_field'),
    path('update-field/<int:field_id>/', views.update_field, name='update_field'),
    path('delete-field/<int:field_id>/', views.delete_field, name='delete_field'),
    path('chat/', views.chat, name='chat'),
    path('download-pdf/<int:document_id>/', views.download_pdf, name='download_pdf'),
]
'''
        (app_dir / "urls.py").write_text(urls_py)
    
    def create_django_views(self, integration_dir):
        """Create Django views"""
        app_dir = integration_dir / "ai_autofill_assistant"
        
        views_py = '''from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .models import Document, CustomField
from .core.html_pdf_processor import HTMLPDFProcessor
from .core.ai_data_generator import AIDataGenerator

def index(request):
    """Main AI Autofill Assistant interface"""
    return render(request, 'ai_autofill_assistant/index.html')

@csrf_exempt
@require_http_methods(["POST"])
def upload_pdf(request):
    """Handle PDF upload"""
    if 'pdf_file' not in request.FILES:
        return JsonResponse({'error': 'No PDF file provided'}, status=400)
    
    pdf_file = request.FILES['pdf_file']
    document = Document.objects.create(
        filename=pdf_file.name,
        file=pdf_file,
        processed=False
    )
    
    return JsonResponse({
        'document_id': document.id,
        'filename': document.filename
    })

@require_http_methods(["GET"])
def process_document(request, document_id):
    """Process uploaded document"""
    document = get_object_or_404(Document, id=document_id)
    
    # Process document with AI Autofill Assistant
    processor = HTMLPDFProcessor()
    processed_html = processor.process_pdf_to_html(document.file.path)
    
    document.processed_html = processed_html
    document.processed = True
    document.save()
    
    return JsonResponse({
        'document_id': document.id,
        'processed_html': processed_html
    })

@csrf_exempt
@require_http_methods(["POST"])
def ai_fill(request, document_id):
    """Fill document with AI-generated data"""
    document = get_object_or_404(Document, id=document_id)
    data = json.loads(request.body)
    
    # Generate AI data
    ai_generator = AIDataGenerator()
    ai_data = ai_generator.generate_field_data(data.get('fields', []))
    
    return JsonResponse({
        'ai_data': ai_data,
        'document_id': document_id
    })

@csrf_exempt
@require_http_methods(["POST"])
def add_field(request):
    """Add custom field"""
    data = json.loads(request.body)
    
    field = CustomField.objects.create(
        field_id=data.get('field_id'),
        field_type=data.get('field_type', 'text'),
        x=data.get('x', 0),
        y=data.get('y', 0),
        value=data.get('value', ''),
        document_id=data.get('document_id')
    )
    
    return JsonResponse({
        'field_id': field.id,
        'field_id': field.field_id
    })

@csrf_exempt
@require_http_methods(["PUT"])
def update_field(request, field_id):
    """Update custom field"""
    field = get_object_or_404(CustomField, id=field_id)
    data = json.loads(request.body)
    
    field.value = data.get('value', field.value)
    field.x = data.get('x', field.x)
    field.y = data.get('y', field.y)
    field.save()
    
    return JsonResponse({'success': True})

@csrf_exempt
@require_http_methods(["DELETE"])
def delete_field(request, field_id):
    """Delete custom field"""
    field = get_object_or_404(CustomField, id=field_id)
    field.delete()
    
    return JsonResponse({'success': True})

@csrf_exempt
@require_http_methods(["POST"])
def chat(request):
    """Handle chat messages"""
    data = json.loads(request.body)
    message = data.get('message', '')
    
    # Process chat message (implement your chat logic)
    response = f"AI Response to: {message}"
    
    return JsonResponse({
        'response': response,
        'message': message
    })

@require_http_methods(["GET"])
def download_pdf(request, document_id):
    """Download generated PDF"""
    document = get_object_or_404(Document, id=document_id)
    
    # Generate PDF (implement your PDF generation logic)
    processor = HTMLPDFProcessor()
    pdf_content = processor.generate_pdf(document.processed_html)
    
    response = HttpResponse(pdf_content, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{document.filename}"'
    
    return response
'''
        (app_dir / "views.py").write_text(views_py)
    
    def create_django_models(self, integration_dir):
        """Create Django models"""
        app_dir = integration_dir / "ai_autofill_assistant"
        
        models_py = '''from django.db import models
from django.utils import timezone

class Document(models.Model):
    filename = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/')
    processed_html = models.TextField(blank=True)
    processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.filename

class CustomField(models.Model):
    FIELD_TYPES = [
        ('text', 'Text'),
        ('number', 'Number'),
        ('email', 'Email'),
        ('date', 'Date'),
        ('signature', 'Signature'),
    ]
    
    field_id = models.CharField(max_length=100, unique=True)
    field_type = models.CharField(max_length=20, choices=FIELD_TYPES, default='text')
    x = models.IntegerField(default=0)
    y = models.IntegerField(default=0)
    value = models.TextField(blank=True)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.field_id} ({self.field_type})"

class ChatMessage(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField()
    response = models.TextField()
    is_user = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Message: {self.message[:50]}..."
'''
        (app_dir / "models.py").write_text(models_py)
    
    def create_flask_blueprint(self, integration_dir):
        """Create Flask blueprint"""
        api_dir = integration_dir / "api"
        
        blueprint_py = '''from flask import Blueprint, request, jsonify, render_template
from werkzeug.utils import secure_filename
import os
import json

ai_autofill_bp = Blueprint('ai_autofill', __name__, url_prefix='/ai-autofill')

@ai_autofill_bp.route('/')
def index():
    """Main AI Autofill Assistant interface"""
    return render_template('ai_autofill_assistant/index.html')

@ai_autofill_bp.route('/upload-pdf', methods=['POST'])
def upload_pdf():
    """Handle PDF upload"""
    if 'pdf_file' not in request.files:
        return jsonify({'error': 'No PDF file provided'}), 400
    
    pdf_file = request.files['pdf_file']
    if pdf_file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Save file and process
    filename = secure_filename(pdf_file.filename)
    # Implement your file processing logic here
    
    return jsonify({
        'document_id': '123',  # Replace with actual document ID
        'filename': filename
    })

@ai_autofill_bp.route('/process-document/<document_id>')
def process_document(document_id):
    """Process uploaded document"""
    # Implement document processing logic
    return jsonify({
        'document_id': document_id,
        'processed_html': '<html>Processed content</html>'
    })

@ai_autofill_bp.route('/ai-fill/<document_id>', methods=['POST'])
def ai_fill(document_id):
    """Fill document with AI-generated data"""
    data = request.get_json()
    
    # Implement AI data generation logic
    ai_data = {
        'field1': 'AI Generated Value 1',
        'field2': 'AI Generated Value 2'
    }
    
    return jsonify({
        'ai_data': ai_data,
        'document_id': document_id
    })

@ai_autofill_bp.route('/add-field', methods=['POST'])
def add_field():
    """Add custom field"""
    data = request.get_json()
    
    # Implement field creation logic
    field_id = f"custom_field_{data.get('x')}_{data.get('y')}"
    
    return jsonify({
        'field_id': field_id,
        'success': True
    })

@ai_autofill_bp.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    data = request.get_json()
    message = data.get('message', '')
    
    # Implement chat logic
    response = f"AI Response to: {message}"
    
    return jsonify({
        'response': response,
        'message': message
    })
'''
        (api_dir / "blueprint.py").write_text(blueprint_py)
    
    def create_standalone_server(self, integration_dir):
        """Create standalone server"""
        server_py = '''#!/usr/bin/env python3
"""
AI Autofill Assistant - Standalone Server
"""

from flask import Flask, render_template, request, jsonify, send_file
import os
import json
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create upload folder
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# In-memory storage for demo (replace with database in production)
documents = {}
custom_fields = {}
chat_messages = []

@app.route('/')
def index():
    """Main AI Autofill Assistant interface"""
    return render_template('index.html')

@app.route('/api/upload-pdf', methods=['POST'])
def upload_pdf():
    """Handle PDF upload"""
    if 'pdf_file' not in request.files:
        return jsonify({'error': 'No PDF file provided'}), 400
    
    pdf_file = request.files['pdf_file']
    if pdf_file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Save file
    filename = f"{datetime.now().timestamp()}_{pdf_file.filename}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    pdf_file.save(filepath)
    
    # Create document record
    document_id = str(datetime.now().timestamp())
    documents[document_id] = {
        'id': document_id,
        'filename': pdf_file.filename,
        'filepath': filepath,
        'processed': False,
        'created_at': datetime.now().isoformat()
    }
    
    return jsonify({
        'document_id': document_id,
        'filename': pdf_file.filename
    })

@app.route('/api/process-document/<document_id>')
def process_document(document_id):
    """Process uploaded document"""
    if document_id not in documents:
        return jsonify({'error': 'Document not found'}), 404
    
    # Simulate document processing
    documents[document_id]['processed'] = True
    documents[document_id]['processed_html'] = '<html><body>Processed document content</body></html>'
    
    return jsonify({
        'document_id': document_id,
        'processed_html': documents[document_id]['processed_html']
    })

@app.route('/api/ai-fill/<document_id>', methods=['POST'])
def ai_fill(document_id):
    """Fill document with AI-generated data"""
    if document_id not in documents:
        return jsonify({'error': 'Document not found'}), 404
    
    data = request.get_json()
    
    # Simulate AI data generation
    ai_data = {
        'field1': 'AI Generated Value 1',
        'field2': 'AI Generated Value 2',
        'field3': 'AI Generated Value 3'
    }
    
    return jsonify({
        'ai_data': ai_data,
        'document_id': document_id
    })

@app.route('/api/add-field', methods=['POST'])
def add_field():
    """Add custom field"""
    data = request.get_json()
    
    field_id = f"custom_field_{data.get('x')}_{data.get('y')}"
    custom_fields[field_id] = {
        'field_id': field_id,
        'field_type': data.get('field_type', 'text'),
        'x': data.get('x', 0),
        'y': data.get('y', 0),
        'value': data.get('value', ''),
        'created_at': datetime.now().isoformat()
    }
    
    return jsonify({
        'field_id': field_id,
        'success': True
    })

@app.route('/api/update-field/<field_id>', methods=['PUT'])
def update_field(field_id):
    """Update custom field"""
    if field_id not in custom_fields:
        return jsonify({'error': 'Field not found'}), 404
    
    data = request.get_json()
    custom_fields[field_id].update(data)
    
    return jsonify({'success': True})

@app.route('/api/delete-field/<field_id>', methods=['DELETE'])
def delete_field(field_id):
    """Delete custom field"""
    if field_id not in custom_fields:
        return jsonify({'error': 'Field not found'}), 404
    
    del custom_fields[field_id]
    return jsonify({'success': True})

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    data = request.get_json()
    message = data.get('message', '')
    
    # Simulate AI response
    response = f"AI Response to: {message}"
    
    # Store chat message
    chat_messages.append({
        'message': message,
        'response': response,
        'timestamp': datetime.now().isoformat()
    })
    
    return jsonify({
        'response': response,
        'message': message
    })

@app.route('/api/get-fields')
def get_fields():
    """Get all custom fields"""
    return jsonify(list(custom_fields.values()))

@app.route('/api/get-chat-history')
def get_chat_history():
    """Get chat history"""
    return jsonify(chat_messages)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
'''
        (integration_dir / "server.py").write_text(server_py)
    
    def create_standalone_interface(self, integration_dir):
        """Create standalone HTML interface"""
        interface_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Autofill Assistant - Standalone</title>
    <link rel="stylesheet" href="static/css/style.css">
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>AI Autofill Assistant</h1>
            <p>Standalone Integration</p>
        </div>
        
        <div class="main-content">
            <div class="upload-section">
                <h2>Upload PDF Document</h2>
                <input type="file" id="pdfFile" accept=".pdf">
                <button id="uploadBtn">Upload PDF</button>
            </div>
            
            <div class="document-section" id="documentSection" style="display: none;">
                <h2>Document Processing</h2>
                <div id="documentContent"></div>
            </div>
            
            <div class="chat-section">
                <h2>AI Assistant</h2>
                <div id="chatMessages"></div>
                <div class="chat-input">
                    <input type="text" id="chatInput" placeholder="Ask AI assistant...">
                    <button id="sendBtn">Send</button>
                </div>
            </div>
        </div>
    </div>
    
    <script src="static/js/main.js"></script>
    <script>
        // Initialize AI Autofill Assistant
        const aiAssistant = new AIAutofillAssistant({
            apiEndpoint: '/api',
            container: document.getElementById('documentContent')
        });
        
        // Setup event listeners
        document.getElementById('uploadBtn').addEventListener('click', () => {
            const file = document.getElementById('pdfFile').files[0];
            if (file) {
                aiAssistant.uploadPDF(file);
            }
        });
        
        document.getElementById('sendBtn').addEventListener('click', () => {
            const message = document.getElementById('chatInput').value;
            if (message) {
                aiAssistant.sendChatMessage(message);
                document.getElementById('chatInput').value = '';
            }
        });
    </script>
</body>
</html>
'''
        (integration_dir / "templates" / "index.html").write_text(interface_html)
    
    def create_configuration_files(self):
        """Create configuration files"""
        integration_dir = self.target_project_path / "ai_autofill_integration"
        
        # Create requirements.txt
        requirements = '''# AI Autofill Assistant Requirements
Django>=3.2.0
Flask>=2.0.0
pdfkit>=1.0.0
weasyprint>=56.0
pytesseract>=0.3.8
Pillow>=8.3.0
opencv-python>=4.5.0
python-dotenv>=0.19.0
requests>=2.26.0
reportlab>=3.6.0
PyPDF2>=1.26.0
openai>=0.27.0
PyMuPDF>=1.20.0
python-docx>=0.8.11
pdfplumber>=0.6.0
'''
        (integration_dir / "requirements.txt").write_text(requirements)
        
        # Create environment configuration
        env_config = '''# AI Autofill Assistant Environment Configuration
AI_AUTOFILL_ENABLED=true
AI_AUTOFILL_DEBUG=false
AI_AUTOFILL_API_KEY=your_openai_api_key_here
AI_AUTOFILL_MAX_FILE_SIZE=10485760
AI_AUTOFILL_ALLOWED_EXTENSIONS=pdf,docx,txt
AI_AUTOFILL_CUSTOM_FIELDS_ENABLED=true
AI_AUTOFILL_CHAT_ENABLED=true
AI_AUTOFILL_PDF_GENERATION_ENABLED=true
'''
        (integration_dir / ".env.example").write_text(env_config)
        
        # Create settings configuration
        settings_config = '''# AI Autofill Assistant Settings
AI_AUTOFILL_SETTINGS = {
    'ENABLED': True,
    'DEBUG': False,
    'API_KEY': 'your_openai_api_key_here',
    'MAX_FILE_SIZE': 10 * 1024 * 1024,  # 10MB
    'ALLOWED_EXTENSIONS': ['pdf', 'docx', 'txt'],
    'CUSTOM_FIELDS_ENABLED': True,
    'CHAT_ENABLED': True,
    'PDF_GENERATION_ENABLED': True,
    'SECURITY': {
        'ALLOWED_FILE_TYPES': ['pdf', 'docx', 'txt'],
        'MAX_FILE_SIZE': 10 * 1024 * 1024,
        'SCAN_FOR_VIRUSES': False,
        'ENCRYPT_UPLOADS': False,
        'REQUIRE_AUTHENTICATION': False
    }
}
'''
        (integration_dir / "settings.py").write_text(settings_config)
    
    def generate_integration_code(self, project_type):
        """Generate integration code for the target project"""
        integration_dir = self.target_project_path / "ai_autofill_integration"
        
        if project_type == "django":
            self.generate_django_integration_code(integration_dir)
        elif project_type == "flask":
            self.generate_flask_integration_code(integration_dir)
        elif project_type == "standalone":
            self.generate_standalone_integration_code(integration_dir)
    
    def generate_django_integration_code(self, integration_dir):
        """Generate Django integration code"""
        integration_code = '''# Django Integration Code
# Add this to your main Django project

# 1. Add to settings.py
INSTALLED_APPS = [
    # ... your existing apps
    'ai_autofill_integration.ai_autofill_assistant',
    'rest_framework',
    'corsheaders',
]

MIDDLEWARE = [
    # ... your existing middleware
    'corsheaders.middleware.CorsMiddleware',
]

# Add AI Autofill Assistant settings
from ai_autofill_integration.settings import AI_AUTOFILL_SETTINGS
AI_AUTOFILL_SETTINGS = AI_AUTOFILL_SETTINGS

# 2. Add to main urls.py
from django.urls import path, include

urlpatterns = [
    # ... your existing URLs
    path('ai-autofill/', include('ai_autofill_integration.ai_autofill_assistant.urls')),
]

# 3. Add to your base template
{% load static %}
<link rel="stylesheet" href="{% static 'ai_autofill_integration/static/css/style.css' %}">
<script src="{% static 'ai_autofill_integration/static/js/main.js' %}"></script>

# 4. Run migrations
python manage.py makemigrations ai_autofill_assistant
python manage.py migrate

# 5. Create superuser (if needed)
python manage.py createsuperuser

# 6. Run server
python manage.py runserver
'''
        (integration_dir / "django_integration.py").write_text(integration_code)
    
    def generate_flask_integration_code(self, integration_dir):
        """Generate Flask integration code"""
        integration_code = '''# Flask Integration Code
# Add this to your main Flask project

from flask import Flask
from ai_autofill_integration.api.blueprint import ai_autofill_bp

app = Flask(__name__)

# Register AI Autofill Assistant blueprint
app.register_blueprint(ai_autofill_bp)

# Configure AI Autofill Assistant
app.config['AI_AUTOFILL_ENABLED'] = True
app.config['AI_AUTOFILL_DEBUG'] = False
app.config['AI_AUTOFILL_API_KEY'] = 'your_openai_api_key_here'

# Add to your base template
<link rel="stylesheet" href="{{ url_for('static', filename='ai_autofill_integration/static/css/style.css') }}">
<script src="{{ url_for('static', filename='ai_autofill_integration/static/js/main.js') }}"></script>

# Run server
if __name__ == '__main__':
    app.run(debug=True)
'''
        (integration_dir / "flask_integration.py").write_text(integration_code)
    
    def generate_standalone_integration_code(self, integration_dir):
        """Generate standalone integration code"""
        integration_code = '''# Standalone Integration Code
# Run the AI Autofill Assistant as a standalone server

# 1. Install dependencies
pip install -r requirements.txt

# 2. Set environment variables
export AI_AUTOFILL_ENABLED=true
export AI_AUTOFILL_API_KEY=your_openai_api_key_here

# 3. Run server
python server.py

# 4. Access the application
# Open http://localhost:5000 in your browser

# 5. For production deployment
# Use gunicorn or similar WSGI server
gunicorn -w 4 -b 0.0.0.0:5000 server:app
'''
        (integration_dir / "standalone_integration.py").write_text(integration_code)

def main():
    """Main integration setup function"""
    if len(sys.argv) < 2:
        print("Usage: python integration_setup.py <target_project_path> [project_type]")
        print("Project types: django, flask, standalone")
        sys.exit(1)
    
    target_project_path = sys.argv[1]
    project_type = sys.argv[2] if len(sys.argv) > 2 else "django"
    
    if project_type not in ["django", "flask", "standalone"]:
        print("Invalid project type. Use: django, flask, or standalone")
        sys.exit(1)
    
    integrator = AIAutofillIntegrator(target_project_path)
    integrator.setup_integration(project_type)

if __name__ == "__main__":
    main()
