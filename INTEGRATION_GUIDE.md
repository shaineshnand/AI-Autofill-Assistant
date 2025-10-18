# AI Autofill Integration Guide

## 📁 Essential Files for Integration

### Core Files (Required)
- `html_pdf_processor.py` - Main PDF processing and HTML generation
- `intelligent_field_filler.py` - AI field filling logic
- `requirements.txt` - Python dependencies

### Supporting Files (Optional but Recommended)
- `models/` - Pre-trained models for field detection
- `training_data/` - Training data for AI models
- `chat/views.py` - AI integration views
- `documents/views.py` - Document processing views

## 🚀 Quick Integration Example

```python
from html_pdf_processor import HTMLPDFProcessor
from intelligent_field_filler import IntelligentFieldFiller

# 1. Process PDF to HTML
processor = HTMLPDFProcessor()
layout = processor.extract_pdf_layout('your_document.pdf')

# 2. Generate HTML with fillable fields
html_content = processor.create_html_template(layout)

# 3. Fill fields with AI
intelligent_filler = IntelligentFieldFiller()
ai_data = {}

for field in layout.fields:
    ai_content = intelligent_filler.generate_field_content(field, {
        'document_type': layout.document_type,
        'extracted_text': layout.extracted_text
    })
    ai_data[field.id] = ai_content

# 4. Create filled HTML
filled_html = processor.create_filled_html(html_content, ai_data)

# 5. Generate final PDF (optional)
# Use weasyprint or similar to convert HTML to PDF
```

## 📦 Key Dependencies

```bash
pip install PyMuPDF pdfplumber weasyprint reportlab
pip install openai  # For AI functionality
pip install django  # If using Django integration
```

## 🎯 Key Features You Can Use

1. **PDF to HTML Conversion** - Converts PDFs to fillable HTML forms
2. **Field Detection** - Automatically detects underlines, dotted lines, blanks
3. **AI Field Filling** - Intelligently fills fields based on context
4. **HTML to PDF Generation** - Converts filled HTML back to PDF

## 🔧 Integration Options

### Option 1: Standalone Python Script
- Copy `html_pdf_processor.py` and `intelligent_field_filler.py`
- Install dependencies from `requirements.txt`
- Use the classes directly in your code

### Option 2: Django Integration
- Copy the entire `documents/` and `chat/` apps
- Include the models and training data
- Use the existing Django views and URLs

### Option 3: API Integration
- Use the existing Django REST API endpoints
- Call `/upload/`, `/ai-fill/`, `/generate-pdf/` endpoints
- Handle file uploads and responses

## 💡 Key Classes

- `HTMLPDFProcessor` - Main processor for PDF to HTML conversion
- `IntelligentFieldFiller` - AI field filling logic
- `Field` - Data class for form fields
- `DocumentLayout` - Data class for document structure

## 🎉 What You Get

✅ **Automatic field detection** from underlines, dots, blanks
✅ **AI-powered field filling** with contextual intelligence  
✅ **Professional HTML output** with proper styling
✅ **PDF generation** from filled HTML
✅ **Table support** for complex documents
✅ **Multiple field types** (text, checkbox, select, etc.)

Perfect for integrating into any document processing workflow!
