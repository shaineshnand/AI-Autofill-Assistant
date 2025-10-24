from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from ollama_integration import OllamaChatBot, OllamaClient
from datetime import datetime
import re
from intelligent_field_filler import IntelligentFieldFiller

@api_view(['POST'])
def general_chat(request):
    """Handle general chat messages without document context"""
    try:
        message = request.data.get('message', '')
        
        # Process message with chatbot (no document context)
        chatbot = OllamaChatBot()
        response = chatbot.process_message(message, {})
        
        return Response({
            'success': True,
            'response': response
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def chat_with_bot(request, doc_id):
    """Handle chat messages"""
    try:
        message = request.data.get('message', '')
        
        # Import documents_storage from documents.views
        from documents.views import documents_storage, chat_sessions
        
        # Get document from memory
        document = documents_storage.get(str(doc_id))
        if not document:
            return Response({'error': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get or create chat session
        if str(doc_id) not in chat_sessions:
            chat_sessions[str(doc_id)] = {
                'messages': [],
                'created_at': datetime.now().isoformat()
            }
        
        # Add user message
        user_message = {
            'message_type': 'user',
            'content': message,
            'timestamp': datetime.now().isoformat()
        }
        chat_sessions[str(doc_id)]['messages'].append(user_message)
        
        # Get document context
        doc_context = {
            'document_type': 'form',
            'total_blanks': document['total_blanks'],
            'field_types': [field['field_type'] for field in document['fields']],
            'extracted_text': document['extracted_text']
        }
        
        # Process message with chatbot
        chatbot = OllamaChatBot()
        response = chatbot.process_message(message, doc_context)
        
        # Try to extract and fill fields from the conversation
        filled_fields = extract_and_fill_fields(message, response, document)
        
        # Add bot message
        bot_message = {
            'message_type': 'bot',
            'content': response,
            'timestamp': datetime.now().isoformat(),
            'filled_fields': filled_fields
        }
        chat_sessions[str(doc_id)]['messages'].append(bot_message)
        
        return Response({
            'success': True,
            'response': response,
            'messages': chat_sessions[str(doc_id)]['messages']
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_chat_history(request, doc_id):
    """Get chat history for a document"""
    try:
        from documents.views import chat_sessions
        
        if str(doc_id) not in chat_sessions:
            return Response({'error': 'Chat session not found'}, status=status.HTTP_404_NOT_FOUND)
        
        return Response(chat_sessions[str(doc_id)]['messages'])
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def ollama_status(request):
    """Check Ollama service status"""
    try:
        ollama = OllamaClient()
        is_running = ollama.is_ollama_running()
        models = ollama.list_models() if is_running else []
        
        return Response({
            'running': is_running,
            'models': models,
            'default_model': ollama.model
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def pull_ollama_model(request):
    """Download a specific Ollama model"""
    try:
        model_name = request.data.get('model_name', 'llama2')
        
        ollama = OllamaClient()
        success = ollama.pull_model(model_name)
        
        return Response({
            'success': success,
            'model': model_name,
            'message': f"Model {model_name} {'downloaded successfully' if success else 'download failed'}"
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def suggest_field_content(request, doc_id):
    """Get AI suggestions for a specific field"""
    try:
        field_id = request.data.get('field_id')
        user_input = request.data.get('user_input', '')
        
        from documents.views import documents_storage
        
        document = documents_storage.get(str(doc_id))
        if not document:
            return Response({'error': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Find the field
        field = None
        for f in document['fields']:
            if f['id'] == field_id:
                field = f
                break
        
        if not field:
            return Response({'error': 'Field not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Use intelligent field filler for better suggestions
        intelligent_filler = IntelligentFieldFiller()
        
        # Get document context
        doc_context = {
            'document_type': 'form',
            'total_blanks': document['total_blanks'],
            'field_types': [f['field_type'] for f in document['fields']],
            'extracted_text': document['extracted_text']
        }
        
        # Get suggestions based on user input and field context
        suggestion = intelligent_filler.suggest_field_content(field, user_input, doc_context)
        
        # Also get alternative suggestions
        alternative_suggestions = intelligent_filler.get_field_suggestions(field, doc_context)
        
        return Response({
            'success': True,
            'field_id': field_id,
            'suggestion': suggestion,
            'alternative_suggestions': alternative_suggestions,
            'context': field['context'],
            'field_type': field['field_type']
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def fill_all_fields(request, doc_id):
    """Fill all empty fields with AI suggestions - NOW WITH CLEAN SEJDA!"""
    try:
        # Get document from persistent storage
        from documents.views import get_stored_document, save_document
        document = get_stored_document(doc_id)
        if not document:
            return Response({'error': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if we should use CLEAN Sejda workflow
        from sejda_direct_fill import SejdaDirectFill
        try:
            import pywinauto
            PYWINAUTO_AVAILABLE = True
        except:
            PYWINAUTO_AVAILABLE = False
        
        use_sejda_clean = False
        sejda_processor = None
        
        if document.get('file_path', '').lower().endswith('.pdf'):
            sejda_processor = SejdaDirectFill()
            if sejda_processor.sejda_path and PYWINAUTO_AVAILABLE:
                use_sejda_clean = True
                print("\n" + "="*60)
                print("🎯 CLEAN SEJDA WORKFLOW ACTIVATED!")
                print("="*60)
        
        # Overwrite flag: when true, fill even fields that already have content
        try:
            overwrite = bool(request.data.get('overwrite', False))
        except Exception:
            overwrite = False

        # Get document context
        doc_context = {
            'document_type': 'form',
            'total_blanks': document['total_blanks'],
            'field_types': [field['field_type'] for field in document['fields']],
            'extracted_text': document['extracted_text']
        }
        
        # Use intelligent field filler for better content generation
        intelligent_filler = IntelligentFieldFiller()
        filled_fields = []
        
        for field in document['fields']:
            if overwrite or not field.get('user_content'):
                # Generate intelligent content based on field type and context
                suggested_content = intelligent_filler.generate_field_content(field, doc_context)
                
                filled_fields.append({
                    'id': field.get('id'),
                    'content': suggested_content,
                    'type': field.get('field_type')
                })
                
                # Update the field in the document - store AI content separately
                field['ai_content'] = suggested_content
                field['ai_suggestion'] = suggested_content
                field['ai_enhanced'] = True
                print(f"AI filled field {field.get('id')}: '{suggested_content}'")
        
        # Save the document with AI content to persistent storage
        save_document(document)
        
        # If CLEAN Sejda workflow is available, trigger it NOW!
        if use_sejda_clean and sejda_processor:
            print("\n🚀 Triggering CLEAN Sejda workflow...")
            
            # Prepare AI data for Sejda
            ai_data_for_sejda = {}
            for field in document['fields']:
                ai_value = field.get('ai_content') or field.get('ai_suggestion', '')
                if ai_value:
                    # Use field ID as key
                    ai_data_for_sejda[field['id']] = ai_value
            
            # Get file paths
            input_pdf = document.get('file_path', '')
            output_pdf = input_pdf.replace('uploads/', 'processed/sejda_filled_')
            
            # Make sure paths are absolute
            from django.conf import settings
            import os
            input_pdf_full = os.path.join(settings.MEDIA_ROOT, input_pdf) if not os.path.isabs(input_pdf) else input_pdf
            output_pdf_full = os.path.join(settings.MEDIA_ROOT, output_pdf)
            
            print(f"   📂 Input PDF: {input_pdf_full}")
            print(f"   💾 Output PDF: {output_pdf_full}")
            print(f"   🤖 AI data: {len(ai_data_for_sejda)} fields")
            
            # Execute CLEAN Sejda workflow
            result = sejda_processor.process_pdf_clean(input_pdf_full, ai_data_for_sejda, output_pdf_full)
            
            if result['success']:
                print("✅ CLEAN Sejda workflow completed!")
                print(f"   📄 Filled PDF saved: {output_pdf_full}")
                
                # Update document with Sejda-filled PDF path
                document['sejda_filled_pdf'] = output_pdf
                save_document(document)
                
                return Response({
                    'success': True,
                    'filled_fields': filled_fields,
                    'sejda_filled': True,
                    'sejda_pdf_url': f"/media/{output_pdf}",
                    'message': f'✅ Filled {len(filled_fields)} fields with AI and saved via Sejda!'
                })
            else:
                print(f"⚠️  Sejda workflow failed: {result.get('error')}")
                print("   → Returning AI-filled data without Sejda")
        
        return Response({
            'success': True,
            'filled_fields': filled_fields,
            'message': f'Filled {len(filled_fields)} fields with AI suggestions'
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def extract_and_fill_fields(message, response, document):
    """Extract information from chat and fill relevant fields using intelligent filler"""
    filled_fields = []
    
    # Use intelligent field filler for better extraction
    intelligent_filler = IntelligentFieldFiller()
    
    # Get document context
    doc_context = {
        'document_type': 'form',
        'total_blanks': document['total_blanks'],
        'field_types': [field['field_type'] for field in document['fields']],
        'extracted_text': document['extracted_text']
    }
    
    # Check each field in the document
    for field in document['fields']:
        # Skip if field already has content
        if field['user_content']:
            continue
        
        # Try to extract content from user message first
        extracted_content = intelligent_filler._extract_content_from_input(message, field['field_type'])
        
        # If no content extracted from message, try AI response
        if not extracted_content:
            extracted_content = intelligent_filler._extract_content_from_input(response, field['field_type'])
        
        # If still no content, generate based on field type
        if not extracted_content:
            extracted_content = intelligent_filler.generate_field_content(field, doc_context)
        
        if extracted_content:
            # Validate the content
            if intelligent_filler.validate_field_content(extracted_content, field['field_type']):
                # Update the field
                field['user_content'] = extracted_content
                field['ai_suggestion'] = extracted_content
                field['ai_enhanced'] = True
                
                filled_fields.append({
                    'id': field['id'],
                    'type': field['field_type'],
                    'content': extracted_content
                })
    
    return filled_fields
