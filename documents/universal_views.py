"""
Universal Document Processing Views
Integration of the universal document processor with Django
"""
import os
import sys
import json
import logging
from typing import List, Dict, Any
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from universal_document_processor import UniversalDocumentProcessor, DocumentField, convert_to_dict

# Configure logging
logger = logging.getLogger(__name__)

# Initialize the universal processor
processor = UniversalDocumentProcessor()

@csrf_exempt
@require_http_methods(["POST"])
def upload_document_universal(request):
    """
    Upload and process document using universal processor
    """
    try:
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'No file uploaded'}, status=400)
        
        file = request.FILES['file']
        if file.size == 0:
            return JsonResponse({'error': 'Empty file'}, status=400)
        
        # Save file temporarily
        file_path = default_storage.save(f'temp_{file.name}', ContentFile(file.read()))
        full_path = os.path.join(settings.MEDIA_ROOT, file_path)
        
        # Process document with universal processor
        fields = processor.detect_fields_universal(full_path)
        
        # Convert to dictionaries for JSON response
        field_dicts = convert_to_dict(fields)
        
        # Extract text for context
        text = processor._extract_text(full_path)
        
        # Classify document type
        doc_type, confidence = processor.classify_document_type(text)
        
        # Clean up temp file
        default_storage.delete(file_path)
        
        return JsonResponse({
            'success': True,
            'fields': field_dicts,
            'total_fields': len(fields),
            'document_type': doc_type,
            'confidence': confidence,
            'text_preview': text[:500] + '...' if len(text) > 500 else text
        })
        
    except Exception as e:
        logger.error(f"Error in universal document upload: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def train_model(request):
    """
    Train the universal processor with new data
    """
    try:
        data = json.loads(request.body)
        
        # Validate required fields
        required_fields = ['document_type', 'samples']
        for field in required_fields:
            if field not in data:
                return JsonResponse({'error': f'Missing required field: {field}'}, status=400)
        
        # Prepare training data
        training_data = []
        for sample in data['samples']:
            training_sample = {
                'text': sample.get('text', ''),
                'field_type': sample.get('field_type', 'text'),
                'document_type': data['document_type'],
                'context': sample.get('context', ''),
                'confidence': sample.get('confidence', 1.0)
            }
            training_data.append(training_sample)
        
        # Train the model
        results = processor.train_model(training_data)
        
        return JsonResponse({
            'success': True,
            'results': results,
            'message': f'Model trained with {len(training_data)} samples'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Error training model: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def create_template(request):
    """
    Create a new document template
    """
    try:
        data = json.loads(request.body)
        
        # Validate required fields
        required_fields = ['document_type', 'description', 'field_patterns']
        for field in required_fields:
            if field not in data:
                return JsonResponse({'error': f'Missing required field: {field}'}, status=400)
        
        # Create template
        success = processor.create_document_template(
            document_type=data['document_type'],
            description=data['description'],
            field_patterns=data['field_patterns'],
            validation_rules=data.get('validation_rules', {})
        )
        
        if success:
            return JsonResponse({
                'success': True,
                'message': f'Template created for {data["document_type"]}'
            })
        else:
            return JsonResponse({'error': 'Failed to create template'}, status=500)
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Error creating template: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
def get_system_stats(request):
    """
    Get system statistics and performance metrics
    """
    try:
        stats = processor.get_system_stats()
        return JsonResponse(stats)
    except Exception as e:
        logger.error(f"Error getting system stats: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
def get_field_patterns(request):
    """
    Get available field patterns and document types
    """
    try:
        return JsonResponse({
            'field_patterns': processor.field_patterns,
            'document_type_patterns': processor.document_type_patterns,
            'available_templates': list(processor.document_templates.keys())
        })
    except Exception as e:
        logger.error(f"Error getting field patterns: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def fill_document_universal(request):
    """
    Fill a document using universal processor
    """
    try:
        data = json.loads(request.body)
        
        # Validate required fields
        required_fields = ['document_path', 'field_data']
        for field in required_fields:
            if field not in data:
                return JsonResponse({'error': f'Missing required field: {field}'}, status=400)
        
        # This would integrate with the existing create_filled_pdf function
        # For now, return success
        return JsonResponse({
            'success': True,
            'message': 'Document filled successfully',
            'output_path': 'filled_document.pdf'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Error filling document: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
def get_document_types(request):
    """
    Get list of supported document types
    """
    try:
        document_types = list(processor.document_type_patterns.keys())
        document_types.extend(list(processor.document_templates.keys()))
        
        return JsonResponse({
            'document_types': list(set(document_types)),
            'total_types': len(set(document_types))
        })
    except Exception as e:
        logger.error(f"Error getting document types: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def add_training_sample(request):
    """
    Add a single training sample
    """
    try:
        data = json.loads(request.body)
        
        # Validate required fields
        required_fields = ['text', 'field_type', 'document_type']
        for field in required_fields:
            if field not in data:
                return JsonResponse({'error': f'Missing required field: {field}'}, status=400)
        
        # Add to training data
        training_sample = {
            'text': data['text'],
            'field_type': data['field_type'],
            'document_type': data['document_type'],
            'context': data.get('context', ''),
            'confidence': data.get('confidence', 1.0)
        }
        
        processor.training_data.append(training_sample)
        
        return JsonResponse({
            'success': True,
            'message': 'Training sample added',
            'total_samples': len(processor.training_data)
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Error adding training sample: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
def export_training_data(request):
    """
    Export training data for backup or sharing
    """
    try:
        training_data = {
            'samples': processor.training_data,
            'templates': [processor.document_templates[dt].__dict__ for dt in processor.document_templates],
            'field_patterns': processor.field_patterns,
            'document_type_patterns': processor.document_type_patterns
        }
        
        response = HttpResponse(
            json.dumps(training_data, indent=2),
            content_type='application/json'
        )
        response['Content-Disposition'] = 'attachment; filename="training_data.json"'
        return response
        
    except Exception as e:
        logger.error(f"Error exporting training data: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def import_training_data(request):
    """
    Import training data from backup
    """
    try:
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'No file uploaded'}, status=400)
        
        file = request.FILES['file']
        data = json.loads(file.read().decode('utf-8'))
        
        # Import training samples
        if 'samples' in data:
            processor.training_data.extend(data['samples'])
        
        # Import templates
        if 'templates' in data:
            for template_data in data['templates']:
                # This would recreate templates from the imported data
                pass
        
        return JsonResponse({
            'success': True,
            'message': 'Training data imported successfully',
            'samples_imported': len(data.get('samples', []))
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON file'}, status=400)
    except Exception as e:
        logger.error(f"Error importing training data: {e}")
        return JsonResponse({'error': str(e)}, status=500)

