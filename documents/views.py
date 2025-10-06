from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import FileResponse, Http404, JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import os
import json
import uuid
from datetime import datetime
import pytesseract
import cv2
import numpy as np
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from ollama_integration import AIDocumentProcessor, OllamaClient
from PIL import Image
import fitz  # PyMuPDF for PDF processing

# Configure Tesseract path for Windows
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# In-memory storage (no database needed)
documents_storage = {}
chat_sessions = {}

class DocumentProcessor:
    def __init__(self):
        self.blank_spaces = []
        self.extracted_text = ""
        self.ai_processor = AIDocumentProcessor()
        
    def pdf_to_image(self, pdf_path):
        """Convert PDF to image for processing"""
        try:
            # Open PDF
            pdf_document = fitz.open(pdf_path)
            page = pdf_document[0]  # Get first page
            
            # Convert to image
            mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better quality
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("png")
            
            # Convert to OpenCV format
            nparr = np.frombuffer(img_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            pdf_document.close()
            return image
        except Exception as e:
            raise Exception(f"Error converting PDF to image: {str(e)}")
    
    def process_document(self, file_path):
        """Process uploaded document and identify blank spaces"""
        try:
            # Check file extension
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.pdf':
                # Process PDF
                image = self.pdf_to_image(file_path)
            else:
                # Process image file
                image = cv2.imread(file_path)
            
            # Check if image was loaded successfully
            if image is None:
                raise ValueError(f"Could not load image from {file_path}. Please ensure the file is a valid image or PDF format.")
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply OCR to extract text
            self.extracted_text = pytesseract.image_to_string(gray)
            
            # Find blank spaces (white rectangles)
            self.blank_spaces = self.find_blank_spaces(gray)
            
            # If no blank spaces found, create virtual fields based on text analysis
            if not self.blank_spaces:
                self.blank_spaces = self.create_virtual_fields_from_text(self.extracted_text, gray)
            
            return {
                'extracted_text': self.extracted_text,
                'blank_spaces': self.blank_spaces,
                'total_blanks': len(self.blank_spaces)
            }
        except Exception as e:
            raise Exception(f"Error processing document: {str(e)}")
    
    def find_blank_spaces(self, gray_image):
        """Find blank spaces in the document"""
        try:
            # Apply adaptive threshold for better edge detection
            thresh = cv2.adaptiveThreshold(gray_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
            
            # Find contours
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            blank_spaces = []
            image_height, image_width = gray_image.shape
            
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                area = w * h
                
                # More specific filtering for form fields
                # Look for rectangular areas that could be form fields
                aspect_ratio = w / h if h > 0 else 0
                
                # Filter for reasonable form field sizes and shapes
                if (area > 1000 and area < 100000 and  # Larger minimum size to avoid artifacts
                    w > 50 and h > 20 and  # Larger minimum dimensions
                    w < image_width * 0.8 and h < image_height * 0.3 and  # Not too large
                    (aspect_ratio > 0.5 and aspect_ratio < 10)):  # Reasonable aspect ratio
                    
                    # Check if this area is actually blank (mostly white)
                    roi = gray_image[y:y+h, x:x+w]
                    if roi.size > 0:
                        mean_intensity = np.mean(roi)
                        if mean_intensity > 200:  # Mostly white/blank area
                            blank_spaces.append({
                                'x': int(x),
                                'y': int(y),
                                'width': int(w),
                                'height': int(h),
                                'area': int(area),
                                'context': analyze_context(gray_image, x, y, w, h, self.extracted_text)
                            })
            
            # If no blank spaces found with the above method, try a simpler approach
            if not blank_spaces:
                # Look for white rectangular regions
                _, thresh_white = cv2.threshold(gray_image, 240, 255, cv2.THRESH_BINARY)
                contours_white, _ = cv2.findContours(thresh_white, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                for contour in contours_white:
                    x, y, w, h = cv2.boundingRect(contour)
                    area = w * h
                    
                    if (area > 1000 and area < 50000 and
                        w > 50 and h > 20 and
                        w < image_width * 0.6 and h < image_height * 0.2):
                        
                        blank_spaces.append({
                            'x': int(x),
                            'y': int(y),
                            'width': int(w),
                            'height': int(h),
                            'area': int(area),
                            'context': analyze_context(gray_image, x, y, w, h, self.extracted_text)
                        })
            
            return blank_spaces
            
        except Exception as e:
            print(f"Error in find_blank_spaces: {e}")
            return []
    
    def create_virtual_fields_from_text(self, text, gray_image):
        """Create virtual form fields based on text analysis"""
        virtual_fields = []
        lines = text.split('\n')
        
        # Enhanced form field patterns with more specific matching
        field_patterns = {
            'name': ['enter your name', 'please enter your name', 'name of dependent', 'full name'],
            'age': ['age of dependent', 'age:', 'years old'],
            'dropdown': ['select an item', 'dropdown', 'combo', 'choose'],
            'checkbox': ['check all that apply', 'option 1', 'option 2', 'option 3'],
            'email': ['email', 'e-mail', 'email address'],
            'phone': ['phone', 'telephone', 'tel', 'mobile'],
            'address': ['address', 'street', 'location'],
            'date': ['date', 'birth', 'dob'],
            'signature': ['signature', 'sign', 'initial']
        }
        
        # Get image dimensions if available
        if gray_image is not None:
            height, width = gray_image.shape
        else:
            height, width = 800, 600  # Default dimensions
        
        # Create virtual fields based on text content
        field_id = 0
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            
            # Skip empty lines
            if not line_lower:
                continue
                
            # Check if line contains form field indicators
            field_type = None
            for ftype, patterns in field_patterns.items():
                for pattern in patterns:
                    if pattern in line_lower:
                        field_type = ftype
                        break
                if field_type:
                    break
            
            # If we found a field type, create a virtual field
            if field_type:
                virtual_fields.append({
                    'x': 50,  # Default position
                    'y': 100 + (field_id * 60),  # Spread vertically with more space
                    'width': 400,  # Wider default width
                    'height': 40,   # Taller default height
                    'area': 16000,   # Larger default area
                    'context': field_type
                })
                field_id += 1
        
        # If still no fields found, create some default ones based on common form elements
        if not virtual_fields:
            # Look for lines that end with colons (common in forms)
            for i, line in enumerate(lines):
                if line.strip().endswith(':') and len(line.strip()) > 3:
                    field_type = 'general'
                    line_lower = line.lower().strip()
                    
                    # Determine field type
                    for ftype, patterns in field_patterns.items():
                        for pattern in patterns:
                            if pattern in line_lower:
                                field_type = ftype
                                break
                    
                    virtual_fields.append({
                        'x': 50,
                        'y': 100 + (len(virtual_fields) * 60),
                        'width': 400,
                        'height': 40,
                        'area': 16000,
                        'context': field_type
                    })
        
        return virtual_fields
    
    def process_word_document(self, file_path):
        """Process Word documents (.doc, .docx)"""
        try:
            from docx import Document
            
            # Extract text from Word document
            doc = Document(file_path)
            content = ""
            
            for paragraph in doc.paragraphs:
                content += paragraph.text + "\n"
            
            # Also extract text from tables
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        content += cell.text + " "
                    content += "\n"
            
            # Create virtual fields based on text content
            virtual_fields = self.create_virtual_fields_from_text(content, None)
            
            return {
                'extracted_text': content,
                'blank_spaces': virtual_fields,
                'total_blanks': len(virtual_fields)
            }
        except Exception as e:
            # Fallback to simple text extraction if python-docx fails
            try:
                with open(file_path, 'rb') as f:
                    content = f.read().decode('utf-8', errors='ignore')
                
                virtual_fields = self.create_virtual_fields_from_text(content, None)
                
                return {
                    'extracted_text': content,
                    'blank_spaces': virtual_fields,
                    'total_blanks': len(virtual_fields)
                }
            except Exception as e2:
                raise Exception(f"Error processing Word document: {str(e2)}")
    
    def process_text_document(self, file_path):
        """Process text documents (.txt, .rtf)"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Create virtual fields based on text content
            virtual_fields = self.create_virtual_fields_from_text(content, None)
            
            return {
                'extracted_text': content,
                'blank_spaces': virtual_fields,
                'total_blanks': len(virtual_fields)
            }
        except Exception as e:
            raise Exception(f"Error processing text document: {str(e)}")

def index(request):
    """Main page view"""
    document = None
    ollama_status = {'running': False, 'models': []}
    
    # Check if there's a document in session
    if 'current_document_id' in request.session:
        doc_id = request.session['current_document_id']
        document = documents_storage.get(doc_id)
        if not document:
            del request.session['current_document_id']
    
    # Check Ollama status
    try:
        ollama = OllamaClient()
        ollama_status = {
            'running': ollama.is_ollama_running(),
            'models': ollama.list_models() if ollama.is_ollama_running() else []
        }
    except:
        pass
    
    context = {
        'document': document,
        'ollama_status': ollama_status,
        'now': datetime.now()
    }
    
    return render(request, 'index.html', context)

def analyze_context(image, x, y, w, h, full_text=""):
    """Analyze context around blank space to suggest content"""
    # If we have the full extracted text, use it for better analysis
    if full_text:
        lines = full_text.split('\n')
        
        # Look for form field indicators in the text
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            
            # Check for specific field types
            if any(keyword in line_lower for keyword in ['enter your name', 'please enter your name', 'name:']):
                return 'name'
            elif any(keyword in line_lower for keyword in ['dependent', 'name of dependent']):
                return 'name'
            elif any(keyword in line_lower for keyword in ['age', 'age of dependent']):
                return 'age'
            elif any(keyword in line_lower for keyword in ['select', 'dropdown', 'combo']):
                return 'dropdown'
            elif any(keyword in line_lower for keyword in ['check', 'option']):
                return 'checkbox'
            elif any(keyword in line_lower for keyword in ['email', 'e-mail']):
                return 'email'
            elif any(keyword in line_lower for keyword in ['phone', 'telephone', 'tel']):
                return 'phone'
            elif any(keyword in line_lower for keyword in ['address']):
                return 'address'
            elif any(keyword in line_lower for keyword in ['date', 'birth']):
                return 'date'
            elif any(keyword in line_lower for keyword in ['signature', 'sign']):
                return 'signature'
    
    # Fallback to OCR on context region
    try:
        padding = 50
        y1 = max(0, y - padding)
        y2 = min(image.shape[0], y + h + padding)
        x1 = max(0, x - padding)
        x2 = min(image.shape[1], x + w + padding)
        
        context_region = image[y1:y2, x1:x2]
        context_text = pytesseract.image_to_string(context_region)
        context_lower = context_text.lower()
        
        if 'name' in context_lower:
            return 'name'
        elif 'address' in context_lower:
            return 'address'
        elif 'phone' in context_lower or 'tel' in context_lower:
            return 'phone'
        elif 'email' in context_lower:
            return 'email'
        elif 'date' in context_lower:
            return 'date'
        elif 'signature' in context_lower:
            return 'signature'
    except:
        pass
    
    return 'general'

@api_view(['POST'])
def upload_document(request):
    """Handle document upload and processing"""
    try:
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
        
        # Supported file types
        supported_extensions = {
            '.pdf': 'PDF Document',
            '.png': 'PNG Image',
            '.jpg': 'JPEG Image', 
            '.jpeg': 'JPEG Image',
            '.gif': 'GIF Image',
            '.bmp': 'BMP Image',
            '.tiff': 'TIFF Image',
            '.tif': 'TIFF Image',
            '.webp': 'WebP Image',
            '.doc': 'Word Document',
            '.docx': 'Word Document',
            '.txt': 'Text Document',
            '.rtf': 'Rich Text Document'
        }
        
        if file_ext not in supported_extensions:
            return Response({
                'error': f'Unsupported file type: {file_ext}. Supported types: {", ".join(supported_extensions.keys())}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
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
        
        # Process document based on file type
        processor = DocumentProcessor()
        
        # Handle different file types
        if file_ext in ['.doc', '.docx']:
            # For Word documents, we'll extract text and create virtual fields
            result = processor.process_word_document(filepath)
        elif file_ext == '.txt':
            # For text files, create virtual fields based on content
            result = processor.process_text_document(filepath)
        else:
            # For PDFs and images, use the existing OCR processing
            result = processor.process_document(filepath)
        
        # Create document record in memory
        document = {
            'id': doc_id,
            'filename': file.name,
            'file_path': filepath,
            'extracted_text': result['extracted_text'],
            'total_blanks': result['total_blanks'],
            'uploaded_at': datetime.now().isoformat(),
            'status': 'processed',
            'fields': []
        }
        
        # Store document ID in session
        request.session['current_document_id'] = str(doc_id)
        
        # Create field records in memory
        for i, space in enumerate(result['blank_spaces']):
            field = {
                'id': i,
                'field_type': space['context'],
                'x_position': space['x'],
                'y_position': space['y'],
                'width': space['width'],
                'height': space['height'],
                'area': space['area'],
                'context': space['context'],
                'user_content': '',
                'ai_suggestion': '',
                'ai_enhanced': False
            }
            document['fields'].append(field)
        
        # Store in memory
        documents_storage[str(doc_id)] = document
        
        return Response({
            'success': True,
            'document_id': str(doc_id),
            'document': document,
            'result': {
                'extracted_text': result['extracted_text'],
                'total_blanks': result['total_blanks']
            }
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_document(request, doc_id):
    """Get document information"""
    try:
        document = documents_storage.get(str(doc_id))
        if not document:
            return Response({'error': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(document)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def update_field(request, doc_id):
    """Update a specific field in the document"""
    try:
        field_id = request.data.get('field_id')
        content = request.data.get('content', '')
        
        document = documents_storage.get(str(doc_id))
        if not document:
            return Response({'error': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Find and update the field
        for field in document['fields']:
            if field['id'] == field_id:
                field['user_content'] = content
                break
        else:
            return Response({'error': 'Field not found'}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({'success': True})
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def generate_pdf(request, doc_id):
    """Generate final PDF with filled content"""
    try:
        document = documents_storage.get(str(doc_id))
        if not document:
            return Response({'error': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Create PDF
        pdf_filename = f"filled_{doc_id}.pdf"
        processed_path = os.path.join(settings.MEDIA_ROOT, 'processed')
        os.makedirs(processed_path, exist_ok=True)
        pdf_path = os.path.join(processed_path, pdf_filename)
        
        # Create PDF with filled information
        c = canvas.Canvas(pdf_path, pagesize=letter)
        width, height = letter
        
        # Title
        c.setFont("Helvetica-Bold", 16)
        c.drawString(100, height - 100, f"Filled Document: {document['filename']}")
        
        # Document information
        c.setFont("Helvetica", 12)
        y_position = height - 150
        
        c.drawString(100, y_position, f"Document ID: {doc_id}")
        y_position -= 30
        c.drawString(100, y_position, f"Uploaded: {document['uploaded_at']}")
        y_position -= 30
        c.drawString(100, y_position, f"Total Fields: {document['total_blanks']}")
        y_position -= 50
        
        # Filled fields
        c.setFont("Helvetica-Bold", 14)
        c.drawString(100, y_position, "Filled Fields:")
        y_position -= 30
        
        c.setFont("Helvetica", 12)
        for field in document['fields']:
            if field['user_content']:
                c.drawString(120, y_position, f"Field {field['id']} ({field['context']}): {field['user_content']}")
                y_position -= 25
        
        c.save()
        
        return Response({
            'success': True,
            'pdf_path': pdf_path,
            'download_url': f'/api/documents/download/{doc_id}'
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def download_pdf(request, doc_id):
    """Download the generated PDF"""
    try:
        pdf_filename = f"filled_{doc_id}.pdf"
        pdf_path = os.path.join(settings.MEDIA_ROOT, 'processed', pdf_filename)
        
        if not os.path.exists(pdf_path):
            return Response({'error': 'PDF not found'}, status=status.HTTP_404_NOT_FOUND)
        
        return FileResponse(open(pdf_path, 'rb'), as_attachment=True, filename=pdf_filename)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def clear_session(request):
    """Clear the current document from session"""
    try:
        # Clear the current document ID from session
        if 'current_document_id' in request.session:
            doc_id = request.session['current_document_id']
            # Optionally remove the document from memory storage
            if str(doc_id) in documents_storage:
                del documents_storage[str(doc_id)]
            del request.session['current_document_id']
        
        return Response({'success': True, 'message': 'Session cleared successfully'})
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def preview_document(request, doc_id):
    """Preview the original document"""
    try:
        document = documents_storage.get(str(doc_id))
        if not document:
            return Response({'error': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)
        
        file_path = document['file_path']
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.pdf':
            # For PDFs, serve the file directly
            return Response({
                'success': True,
                'preview_type': 'pdf',
                'preview_url': f'/media/uploads/{os.path.basename(file_path)}'
            })
        elif file_ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.tif', '.webp']:
            # For images, serve the file directly
            return Response({
                'success': True,
                'preview_type': 'image',
                'preview_url': f'/media/uploads/{os.path.basename(file_path)}'
            })
        else:
            # For text files, return the content
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                return Response({
                    'success': True,
                    'preview_type': 'text',
                    'content': content
                })
            except:
                return Response({
                    'success': True,
                    'preview_type': 'text',
                    'content': document.get('extracted_text', 'No content available')
                })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def regenerate_document(request, doc_id):
    """Regenerate the original document with filled fields overlaid"""
    try:
        document = documents_storage.get(str(doc_id))
        if not document:
            return Response({'error': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)
        
        file_path = document['file_path']
        file_ext = os.path.splitext(file_path)[1].lower()
        
        # Create output filename
        output_filename = f"filled_{os.path.basename(file_path)}"
        output_path = os.path.join(settings.MEDIA_ROOT, 'processed', output_filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        if file_ext == '.pdf':
            # For PDFs, create a new PDF with filled content
            success = create_filled_pdf(file_path, output_path, document['fields'])
        elif file_ext in ['.doc', '.docx']:
            # For Word documents, create a new Word document with filled content
            success = create_filled_word(file_path, output_path, document['fields'])
        elif file_ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.tif', '.webp']:
            # For images, create a new image with text overlaid
            success = create_filled_image(file_path, output_path, document['fields'])
        else:
            # For text files, create a new text file with filled content
            success = create_filled_text(file_path, output_path, document['fields'])
        
        if success:
            return Response({
                'success': True,
                'output_file': output_filename,
                'download_url': f'/media/processed/{output_filename}',
                'message': 'Document regenerated with filled fields'
            })
        else:
            return Response({'error': 'Failed to regenerate document'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def create_filled_pdf(input_path, output_path, fields):
    """Create a filled PDF with text overlaid on the original"""
    try:
        import fitz  # PyMuPDF
        
        # Open the original PDF
        doc = fitz.open(input_path)
        page = doc[0]
        
        # Create a new PDF document
        new_doc = fitz.open()
        new_page = new_doc.new_page(width=page.rect.width, height=page.rect.height)
        
        # Copy the original page content
        new_page.show_pdf_page(page.rect, doc, 0)
        
        # Add filled text to the fields
        for field in fields:
            if field['user_content']:
                x = field['x_position']
                y = field['y_position']
                width = field['width']
                height = field['height']
                
                # Create a text rectangle
                text_rect = fitz.Rect(x, y, x + width, y + height)
                
                # Insert the text
                new_page.insert_text(
                    (x + 5, y + height/2 + 4),  # Position text in the field
                    field['user_content'],
                    fontsize=12,
                    color=(0, 0, 0),  # Black text
                    fontname="helv"  # Helvetica font
                )
        
        # Save the new document
        new_doc.save(output_path)
        new_doc.close()
        doc.close()
        
        return True
        
    except Exception as e:
        print(f"Error creating filled PDF: {e}")
        return False

def create_filled_word(input_path, output_path, fields):
    """Create a filled Word document with filled content"""
    try:
        from docx import Document
        
        # Open the original Word document
        doc = Document(input_path)
        
        # Create a mapping of field types to their content
        field_content_map = {}
        for field in fields:
            if field['user_content']:
                field_content_map[field['context']] = field['user_content']
        
        # Process each paragraph to fill in the fields
        for paragraph in doc.paragraphs:
            text = paragraph.text
            text_lower = text.lower().strip()
            
            # Look for field indicators and fill them
            for field_type, content in field_content_map.items():
                if field_type in text_lower:
                    # If the paragraph ends with ':' or is empty, add the content
                    if text.strip().endswith(':') or text.strip() == '':
                        paragraph.text = text + f" {content}"
                        break
                    # If there's a blank space after the field name, fill it
                    elif ':' in text and len(text.split(':')[1].strip()) == 0:
                        paragraph.text = text + f" {content}"
                        break
        
        # Process tables as well
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        text = paragraph.text
                        text_lower = text.lower().strip()
                        
                        # Look for field indicators and fill them
                        for field_type, content in field_content_map.items():
                            if field_type in text_lower:
                                # If the paragraph ends with ':' or is empty, add the content
                                if text.strip().endswith(':') or text.strip() == '':
                                    paragraph.text = text + f" {content}"
                                    break
                                # If there's a blank space after the field name, fill it
                                elif ':' in text and len(text.split(':')[1].strip()) == 0:
                                    paragraph.text = text + f" {content}"
                                    break
        
        # Save the filled document
        doc.save(output_path)
        return True
        
    except Exception as e:
        print(f"Error creating filled Word document: {e}")
        return False

def create_filled_image(input_path, output_path, fields):
    """Create a filled image with text overlaid on the original"""
    try:
        import cv2
        import numpy as np
        from PIL import Image, ImageDraw, ImageFont
        
        # Load the original image
        image = cv2.imread(input_path)
        if image is None:
            return False
        
        # Convert to PIL Image for text drawing
        pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(pil_image)
        
        # Try to load a font that matches the form
        try:
            # Try different font sizes to match the form
            font = ImageFont.truetype("arial.ttf", 14)
        except:
            try:
                font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 14)
            except:
                font = ImageFont.load_default()
        
        # Overlay filled text on the fields
        for field in fields:
            if field['user_content']:
                x = field['x_position']
                y = field['y_position']
                width = field['width']
                height = field['height']
                
                # Don't cover the field with white - just add the text
                # This preserves the original form appearance
                text = field['user_content']
                
                # Calculate text position (left-aligned in the field)
                text_bbox = draw.textbbox((0, 0), text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                
                # Position text in the field (left-aligned, vertically centered)
                text_x = x + 5  # Small margin from left edge
                text_y = y + (height - text_height) // 2
                
                # Draw the text with a slight background for readability
                # Draw a semi-transparent background
                bg_rect = [text_x - 2, text_y - 1, text_x + text_width + 2, text_y + text_height + 1]
                draw.rectangle(bg_rect, fill=(255, 255, 255, 200))  # Semi-transparent white
                
                # Draw the text
                draw.text((text_x, text_y), text, fill='black', font=font)
        
        # Save the result
        pil_image.save(output_path)
        return True
        
    except Exception as e:
        print(f"Error creating filled image: {e}")
        return False

def create_filled_text(input_path, output_path, fields):
    """Create a filled text file with filled content"""
    try:
        with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Create a copy of the original content to preserve structure
        filled_content = content
        
        # Replace blank lines or placeholder text with filled content
        lines = filled_content.split('\n')
        
        # Create a mapping of field types to their content
        field_content_map = {}
        for field in fields:
            if field['user_content']:
                field_content_map[field['context']] = field['user_content']
        
        # Process each line to fill in the fields
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            
            # Look for field indicators and fill them
            for field_type, content in field_content_map.items():
                if field_type in line_lower:
                    # If the line ends with ':' or is empty, add the content
                    if line.strip().endswith(':') or line.strip() == '':
                        lines[i] = line + f" {content}"
                        break
                    # If there's a blank space after the field name, fill it
                    elif ':' in line and len(line.split(':')[1].strip()) == 0:
                        lines[i] = line + f" {content}"
                        break
        
        # Join the lines back together
        filled_content = '\n'.join(lines)
        
        # Save the filled content
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(filled_content)
        
        return True
        
    except Exception as e:
        print(f"Error creating filled text: {e}")
        return False
