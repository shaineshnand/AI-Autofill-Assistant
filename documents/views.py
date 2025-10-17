import os
import uuid
import json
import traceback
from datetime import datetime
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt

# Document storage (in-memory for now)
documents_storage = {}

def get_stored_document(doc_id):
    """Get document from storage"""
    # Try persistent storage first
    try:
        storage_file = os.path.join(settings.MEDIA_ROOT, 'documents', f'{doc_id}.json')
        if os.path.exists(storage_file):
            with open(storage_file, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Warning: Could not retrieve from persistent storage: {e}")
    
    # Fall back to memory storage
    return documents_storage.get(doc_id)

def save_document(doc_id, document):
    """Save document to storage"""
    try:
        # Save to persistent storage
        storage_dir = os.path.join(settings.MEDIA_ROOT, 'documents')
        os.makedirs(storage_dir, exist_ok=True)
        storage_file = os.path.join(storage_dir, f'{doc_id}.json')
        
        with open(storage_file, 'w') as f:
            json.dump(document, f, indent=2)
    except Exception as e:
        print(f"Warning: Could not save to persistent storage: {e}")
    
    # Also save to memory for faster access
    documents_storage[doc_id] = document

def index(request):
    """Main page view"""
    document = None
    current_doc_id = None
    
    # Get current document from session if available
    if hasattr(request, 'session') and 'current_document_id' in request.session:
        current_doc_id = request.session['current_document_id']
        document = get_stored_document(current_doc_id)
    
    # Check Ollama status
    try:
        from ollama_integration import OllamaClient
        ollama_client = OllamaClient()
        is_running = ollama_client.is_ollama_running()
        models = ollama_client.list_models() if is_running else []
        ollama_status = {
            'is_running': is_running,
            'models': models
        }
        print(f"DEBUG: Ollama status - is_running: {is_running}, models: {len(models)}")
    except Exception as e:
        print(f"Ollama status check failed: {e}")
        ollama_status = {
            'is_running': False,
            'models': []
        }
    
    context = {
        'document': document,
        'current_doc_id': current_doc_id,
        'ollama_status': ollama_status
    }
    
    return render(request, 'index.html', context)

@api_view(['POST'])
def upload_document(request):
    """Handle document upload and processing - HTML workflow only"""
    try:
        print("=== UPLOAD STARTING ===")
        print("Starting upload_document function - HTML workflow only")
        if 'file' not in request.FILES:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)
        
        file = request.FILES['file']
        if not file.name:
            return Response({'error': 'No file selected'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check file size (limit to 50MB)
        if file.size > 50 * 1024 * 1024:
            return Response({'error': 'File too large. Maximum size is 50MB.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get file extension
        file_ext = os.path.splitext(file.name)[1].lower()
        
        # Only support PDF files for HTML workflow
        if file_ext != '.pdf':
            return Response({'error': 'Only PDF files are supported'}, status=400)
        
        # Generate unique document ID
        doc_id = str(uuid.uuid4())
        
        # Save uploaded file
        filename = f"{doc_id}_{file.name}"
        upload_path = os.path.join(settings.MEDIA_ROOT, 'uploads')
        os.makedirs(upload_path, exist_ok=True)
        filepath = os.path.join(upload_path, filename)
        
        with open(filepath, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        
        # HTML-based PDF processing
        print("Using HTML-based PDF processing...")
        try:
            from html_pdf_processor import HTMLPDFProcessor
            processor = HTMLPDFProcessor()
            
            # Step 1: Extract PDF layout and convert to HTML
            layout = processor.extract_pdf_layout(filepath)
            html_content = processor.create_html_template(layout)
            
            # Save HTML content for display
            html_filename = f"html_{doc_id}_{os.path.basename(filepath)}.html"
            html_path = os.path.join(settings.MEDIA_ROOT, 'processed', html_filename)
            os.makedirs(os.path.dirname(html_path), exist_ok=True)
            
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Convert Field objects to dictionaries for JSON serialization
            fields_data = []
            for field in layout.fields:
                if hasattr(field, '__dict__'):
                    # Convert Field object to dictionary
                    field_dict = {
                        'id': getattr(field, 'id', ''),
                        'name': getattr(field, 'name', ''),
                        'field_type': getattr(field, 'field_type', 'text'),
                        'placeholder': getattr(field, 'placeholder', ''),
                        'context': getattr(field, 'context', ''),
                        'x': getattr(field, 'x', 0),
                        'y': getattr(field, 'y', 0),
                        'width': getattr(field, 'width', 100),
                        'height': getattr(field, 'height', 25),
                        'page': getattr(field, 'page', 0)
                    }
                else:
                    # Already a dictionary
                    field_dict = field
                fields_data.append(field_dict)
            
            # Store document data with HTML info
            document_data = {
                'id': doc_id,
                'filename': file.name,
                'file_path': filepath,
                'total_blanks': len(layout.fields),
                'fields': fields_data,
                'html_path': html_path,
                'html_url': f"/media/processed/{html_filename}",
                'document_type': layout.document_type,
                'extracted_text': layout.extracted_text,
                'html_processed': True,
                'ai_filled': False
            }
            
            # Save to storage
            save_document(doc_id, document_data)
            
            # Store document ID in session so page can find it after reload
            if hasattr(request, 'session'):
                request.session['current_document_id'] = str(doc_id)
            
            print(f"HTML conversion successful: {len(layout.fields)} fields detected")
            return Response({
                'success': True,
                'message': 'PDF converted to HTML successfully',
                'doc_id': doc_id,
                'html_url': document_data['html_url'],
                'total_blanks': len(layout.fields),
                'document_type': layout.document_type,
                'html_processed': True
            })
                
        except Exception as e:
            print(f"HTML processing error: {e}")
            return Response({'error': f'HTML processing failed: {str(e)}'}, status=500)
    
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Upload error: {e}")
        print(error_trace)
        return Response({'error': str(e), 'traceback': error_trace}, status=500)

@api_view(['POST'])
def ai_fill_html_document(request, doc_id):
    """Fill HTML document with AI data"""
    try:
        # Get document from storage
        document = get_stored_document(doc_id)
        if not document or not document.get('html_processed'):
            return Response({'error': 'Document not found or not HTML processed'}, status=404)
        
        # Generate AI data for all fields
        from chat.views import IntelligentFieldFiller
        intelligent_filler = IntelligentFieldFiller()
        
        # Build field types list safely
        field_types = []
        for field in document.get('fields', []):
            if isinstance(field, dict):
                field_types.append(field.get('field_type', 'text'))
            else:
                field_types.append('text')  # Default type for string fields
        
        doc_context = {
            'document_type': document.get('document_type', 'form'),
            'total_blanks': document.get('total_blanks', 0),
            'field_types': field_types,
            'extracted_text': document.get('extracted_text', '')
        }
        
        # Generate AI data for each field
        ai_data = {}
        for field in document.get('fields', []):
            try:
                # Debug: Check field type and content
                print(f"Field type: {type(field)}, Field content: {field}")
                
                # Handle both dict and string field formats
                if isinstance(field, dict):
                    field_id = field.get('id', '')
                    field_context = field.get('context', '')
                else:
                    # If field is a string, create a basic structure
                    field_id = f"field_{len(ai_data)}"
                    field_context = str(field)
                
                ai_content = intelligent_filler.generate_field_content(
                    field,  # Pass the field dictionary, not just the context string
                    doc_context
                )
                ai_data[field_id] = ai_content
            except Exception as e:
                print(f"Failed to generate AI data for field: {e}")
                field_id = f"field_{len(ai_data)}" if not isinstance(field, dict) else field.get('id', '')
                ai_data[field_id] = "Sample Data"
        
        # Fill HTML with AI data
        from html_pdf_processor import HTMLPDFProcessor
        processor = HTMLPDFProcessor()
        
        # Read current HTML content
        with open(document['html_path'], 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Debug: Print AI data
        print(f"Generated AI data: {ai_data}")
        
        # Fill HTML with AI data
        filled_html = processor.fill_html_with_ai_data(html_content, ai_data)
        
        # Debug: Check if HTML was actually filled
        print(f"HTML filling completed. Original length: {len(html_content)}, Filled length: {len(filled_html)}")
        
        # Save filled HTML
        filled_html_filename = f"filled_{os.path.basename(document['html_path'])}"
        filled_html_path = os.path.join(settings.MEDIA_ROOT, 'processed', filled_html_filename)
        
        with open(filled_html_path, 'w', encoding='utf-8') as f:
            f.write(filled_html)
        
        # Update document
        document['ai_filled'] = True
        document['filled_html_path'] = filled_html_path
        document['filled_html_url'] = f"/media/processed/{filled_html_filename}"
        
        save_document(doc_id, document)
        
        return Response({
            'success': True,
            'message': 'AI data filled successfully',
            'filled_html_url': document['filled_html_url']
        })
        
    except Exception as e:
        print(f"AI fill error: {e}")
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
def generate_pdf_from_html(request, doc_id):
    """Generate PDF from filled HTML with current field values"""
    try:
        # Get document from storage
        document = get_stored_document(doc_id)
        if not document or not document.get('ai_filled'):
            return Response({'error': 'Document not found or not AI filled'}, status=404)
        
        # Get current field values from request (user edits)
        field_values = request.data.get('field_values', {})
        print(f"Received field values: {field_values}")
        
        # Generate PDF from filled HTML
        from html_pdf_processor import HTMLPDFProcessor
        processor = HTMLPDFProcessor()
        
        # Read filled HTML content
        with open(document['filled_html_path'], 'r', encoding='utf-8') as f:
            filled_html = f.read()
        
        # If user has edited fields, update the HTML with current values
        if field_values:
            filled_html = processor.fill_html_with_ai_data(filled_html, field_values)
            print("Updated HTML with user edits")
        
        # Convert HTML to PDF
        output_filename = f"ai_filled_{document['filename']}"
        output_path = os.path.join(settings.MEDIA_ROOT, 'processed', output_filename)
        
        processor.html_to_pdf(filled_html, output_path)
        
        # Update document with PDF info
        document['output_pdf_path'] = output_path
        document['output_pdf_url'] = f"/media/processed/{output_filename}"
        
        save_document(doc_id, document)
        
        return Response({
            'success': True,
            'message': 'PDF generated successfully',
            'pdf_url': document['output_pdf_url']
        })
        
    except Exception as e:
        print(f"PDF generation error: {e}")
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
def get_document(request, doc_id):
    """Get document information"""
    try:
        document = get_stored_document(doc_id)
        if not document:
            return Response({'error': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'success': True,
            'document': document
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def clear_session(request):
    """Clear the current document from session"""
    try:
        if hasattr(request, 'session'):
            if 'current_document_id' in request.session:
                del request.session['current_document_id']
        
        return Response({
            'success': True,
            'message': 'Session cleared'
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
