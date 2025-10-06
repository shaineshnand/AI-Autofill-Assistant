from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from ollama_integration import OllamaChatBot, OllamaClient
from datetime import datetime
import re

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
        
        # Get AI suggestion
        ollama = OllamaClient()
        suggestion = ollama.suggest_field_content(field['context'], user_input)
        
        return Response({
            'success': True,
            'field_id': field_id,
            'suggestion': suggestion,
            'context': field['context']
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def fill_all_fields(request, doc_id):
    """Fill all empty fields with AI suggestions"""
    try:
        # Get document from memory
        from documents.views import documents_storage
        document = documents_storage.get(str(doc_id))
        if not document:
            return Response({'error': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get document context
        doc_context = {
            'document_type': 'form',
            'total_blanks': document['total_blanks'],
            'field_types': [field['field_type'] for field in document['fields']],
            'extracted_text': document['extracted_text']
        }
        
        # Process with chatbot to get suggestions for all fields
        chatbot = OllamaChatBot()
        filled_fields = []
        
        for field in document['fields']:
            if not field['user_content']:  # Only fill empty fields
                # Create a specific prompt for this field
                field_prompt = f"Suggest appropriate content for a {field['context']} field in a form. Provide a realistic example value."
                response = chatbot.process_message(field_prompt, doc_context)
                
                # Extract the suggested content (simple extraction)
                suggested_content = response.strip()
                if len(suggested_content) > 100:  # If response is too long, take first part
                    suggested_content = suggested_content[:100] + "..."
                
                filled_fields.append({
                    'id': field['id'],
                    'content': suggested_content
                })
                
                # Update the field in the document
                field['user_content'] = suggested_content
                field['ai_suggestion'] = suggested_content
                field['ai_enhanced'] = True
        
        return Response({
            'success': True,
            'filled_fields': filled_fields,
            'message': f'Filled {len(filled_fields)} fields with AI suggestions'
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def extract_and_fill_fields(message, response, document):
    """Extract information from chat and fill relevant fields"""
    filled_fields = []
    message_lower = message.lower()
    response_lower = response.lower()
    
    # Define patterns for different field types
    patterns = {
        'name': [
            r'my name is (\w+(?:\s+\w+)*)',
            r'i am (\w+(?:\s+\w+)*)',
            r'call me (\w+(?:\s+\w+)*)',
            r'name:?\s*(\w+(?:\s+\w+)*)',
            r'(\w+(?:\s+\w+)*) is my name'
        ],
        'email': [
            r'my email is ([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
            r'email:?\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
            r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
            r'contact me at ([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
        ],
        'phone': [
            r'my phone is ([\d\s\-\(\)\+]+)',
            r'phone:?\s*([\d\s\-\(\)\+]+)',
            r'call me at ([\d\s\-\(\)\+]+)',
            r'number:?\s*([\d\s\-\(\)\+]+)'
        ],
        'age': [
            r'i am (\d+) years old',
            r'age:?\s*(\d+)',
            r'i\'m (\d+)',
            r'(\d+) years old'
        ],
        'address': [
            r'my address is ([^.!?]+)',
            r'address:?\s*([^.!?]+)',
            r'i live at ([^.!?]+)',
            r'located at ([^.!?]+)'
        ]
    }
    
    # Check each field in the document
    for field in document['fields']:
        field_type = field['context']
        
        # Skip if field already has content
        if field['user_content']:
            continue
            
        # Check patterns for this field type
        if field_type in patterns:
            for pattern in patterns[field_type]:
                # Check both user message and AI response
                for text in [message, response]:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        extracted_value = match.group(1).strip()
                        if extracted_value and len(extracted_value) > 1:
                            # Update the field
                            field['user_content'] = extracted_value
                            field['ai_suggestion'] = extracted_value
                            field['ai_enhanced'] = True
                            
                            filled_fields.append({
                                'id': field['id'],
                                'type': field_type,
                                'content': extracted_value
                            })
                            break
                if field['user_content']:  # If field was filled, break outer loop
                    break
    
    return filled_fields
