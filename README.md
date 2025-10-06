# AI Autofill Assistant

An intelligent document processing system that uses AI to automatically fill form fields through natural conversation and regenerate documents with filled content.

## Features

- **Multi-Format Support**: PDF, Word, Text, and Image documents
- **AI-Powered Chat**: Natural conversation to fill form fields
- **Smart Field Detection**: Automatically identifies form fields in documents
- **Document Preview**: View original documents before processing
- **Auto-Fill**: AI extracts information from chat and fills relevant fields
- **Document Regeneration**: Creates exact copies of original documents with filled fields
- **Real-time Processing**: Instant field updates and visual feedback

## Installation

### Prerequisites

- Python 3.11+
- Tesseract OCR
- Ollama (for AI functionality)

### 1. Install Tesseract OCR

**Windows:**
```bash
winget install UB-Mannheim.TesseractOCR
```

**macOS:**
```bash
brew install tesseract
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr
```

### 2. Install Ollama

Visit [https://ollama.ai/download](https://ollama.ai/download) and download for your platform.

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Download AI Model

```bash
ollama pull llama3.2:3b
```

## Usage

### Start the Application

```bash
python start_django.py
```

The application will:
- Start Ollama service
- Download AI model (if needed)
- Start Django development server
- Open at `http://localhost:8000`

### How to Use

1. **Upload Document**: Drag and drop or click to upload PDF, Word, Text, or Image files
2. **Preview Document**: Click "Preview Document" to see the original
3. **Chat with AI**: Use the chat panel to provide information:
   - "My name is John Smith"
   - "My email is john@example.com"
   - "I'm 25 years old"
   - "My phone is 555-1234"
4. **Auto-Fill Fields**: AI automatically extracts and fills relevant fields
5. **Regenerate Document**: Click "Regenerate with Filled Fields" to create the final document
6. **Download**: Get your completed form

## Supported Document Types

- **PDF**: Full OCR processing with form field detection
- **Word Documents**: .doc and .docx files with text extraction
- **Text Files**: .txt and .rtf files with content analysis
- **Images**: PNG, JPG, JPEG, GIF, BMP, TIFF, WebP with OCR

## AI Features

- **Smart Pattern Recognition**: Automatically detects names, emails, phones, addresses, ages
- **Context-Aware Chat**: Understands document structure and field types
- **Real-time Field Updates**: Fields fill as you chat
- **Visual Feedback**: Green highlighting for AI-filled fields
- **Natural Conversation**: Chat naturally while filling forms

## API Endpoints

- `POST /upload/` - Upload and process documents
- `GET /api/documents/{id}/preview/` - Preview original document
- `POST /api/documents/{id}/regenerate/` - Regenerate with filled fields
- `POST /api/chat/{id}/` - Chat with AI about document
- `POST /api/chat/general/` - General chat without document
- `POST /api/chat/{id}/fill-all/` - Fill all fields with AI

## Technical Stack

- **Backend**: Django 4.2.7, Django REST Framework
- **AI**: Ollama with Llama 3.2 3B model
- **OCR**: Tesseract with pytesseract
- **Image Processing**: OpenCV, Pillow
- **PDF Processing**: PyMuPDF, ReportLab
- **Word Processing**: python-docx
- **Frontend**: Django Templates, JavaScript, CSS

## File Structure

```
AI-Autofill-Assistant/
├── ai_autofill_project/     # Django project settings
├── documents/               # Document processing app
├── chat/                   # Chat functionality app
├── templates/              # HTML templates
├── static/                 # CSS, JavaScript, images
├── media/                  # Uploaded files
├── ollama_integration.py   # AI integration
├── start_django.py         # Startup script
└── requirements.txt        # Python dependencies
```

## Troubleshooting

### Common Issues

1. **Tesseract not found**: Ensure Tesseract is installed and in PATH
2. **Ollama not responding**: Check if Ollama service is running
3. **Upload errors**: Check file size (max 50MB) and format
4. **Field detection issues**: Try different document formats

### Error Messages

- `"Tesseract not found"`: Install Tesseract OCR
- `"Ollama offline"`: Start Ollama service
- `"Unsupported file type"`: Use supported formats (PDF, Word, Text, Images)
- `"File too large"`: Reduce file size to under 50MB

## Development

### Adding New Field Types

Edit `chat/views.py` and add patterns to the `extract_and_fill_fields` function:

```python
patterns = {
    'new_field_type': [
        r'pattern1 (\w+)',
        r'pattern2 (\w+)',
    ]
}
```

### Customizing AI Responses

Modify `ollama_integration.py` to change AI behavior and prompts.

## License

This project is open source and available under the MIT License.

## Support

For issues and questions, please check the troubleshooting section or create an issue in the repository.