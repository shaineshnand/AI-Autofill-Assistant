import requests
import json
import os
from typing import Dict, List, Optional

class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.model = "llama3.2:3b"  # Default model
        
    def is_ollama_running(self) -> bool:
        """Check if Ollama service is running"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def list_models(self) -> List[str]:
        """List available models"""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
            return []
        except:
            return []
    
    def pull_model(self, model_name: str) -> bool:
        """Download a model"""
        try:
            response = requests.post(
                f"{self.base_url}/api/pull",
                json={"name": model_name},
                stream=True
            )
            return response.status_code == 200
        except:
            return False
    
    def generate_response(self, prompt: str, model: str = None) -> str:
        """Generate response using Ollama"""
        if not model:
            model = self.model
            
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('response', '')
            return "Error: Could not generate response"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def chat_with_context(self, message: str, context: Dict = None) -> str:
        """Enhanced chat with document context"""
        if not context:
            context = {}
        
        # Build context-aware prompt
        prompt = f"""You are an AI assistant helping users fill out documents. 
        
Context about the document:
- Document type: {context.get('document_type', 'Unknown')}
- Number of blank fields: {context.get('total_blanks', 0)}
- Field types found: {', '.join(context.get('field_types', []))}
- Extracted text: {context.get('extracted_text', '')[:500]}...

User message: {message}

Please provide a helpful response to assist with document filling. Be specific and actionable."""
        
        return self.generate_response(prompt)
    
    def analyze_field_context(self, field_data: Dict) -> str:
        """Analyze field context and suggest content"""
        prompt = f"""Analyze this document field and suggest appropriate content:

Field context: {field_data.get('context', 'Unknown')}
Surrounding text: {field_data.get('surrounding_text', '')}
Field position: x={field_data.get('x', 0)}, y={field_data.get('y', 0)}
Field size: {field_data.get('width', 0)}x{field_data.get('height', 0)}

Based on this information, suggest what type of content should go in this field and provide an example."""
        
        return self.generate_response(prompt)
    
    def suggest_field_content(self, field_context: str, user_input: str = "") -> str:
        """Suggest content for a specific field"""
        prompt = f"""Based on the field context "{field_context}" and user input "{user_input}", 
suggest appropriate content for this document field. 
Provide a specific, realistic example that would be appropriate for this type of field."""
        
        return self.generate_response(prompt)

# Enhanced ChatBot with Ollama integration
class OllamaChatBot:
    def __init__(self):
        self.ollama = OllamaClient()
        self.conversation_history = []
        
    def process_message(self, message: str, document_context: Dict = None) -> str:
        """Process chat message with Ollama enhancement"""
        if not self.ollama.is_ollama_running():
            return self._fallback_response(message, document_context)
        
        # Add to conversation history
        self.conversation_history.append({"role": "user", "content": message})
        
        # Generate response with Ollama
        response = self.ollama.chat_with_context(message, document_context)
        
        # Add to conversation history
        self.conversation_history.append({"role": "assistant", "content": response})
        
        return response
    
    def _fallback_response(self, message: str, document_context: Dict = None) -> str:
        """Fallback responses when Ollama is not available"""
        message_lower = message.lower()
        
        if 'hello' in message_lower or 'hi' in message_lower:
            return "Hello! I'm here to help you fill out your document. Please upload a document and I'll identify the blank spaces that need to be filled."
        
        elif 'upload' in message_lower or 'document' in message_lower:
            return "Great! Please upload your document using the upload button. I'll analyze it and identify all the blank spaces that need to be filled."
        
        elif 'help' in message_lower:
            return "I can help you with:\n1. Upload and analyze documents\n2. Identify blank spaces\n3. Suggest content for each field\n4. Review and edit filled information\n5. Generate final PDF"
        
        elif document_context and 'fill' in message_lower:
            blanks_count = len(document_context.get('blank_spaces', []))
            return f"I found {blanks_count} blank spaces in your document. I'll help you fill them out. What information would you like to provide?"
        
        else:
            return "I'm here to help you with document autofill. Please upload a document or ask me about filling out forms."

# Enhanced Document Processor with AI suggestions
class AIDocumentProcessor:
    def __init__(self):
        self.ollama = OllamaClient()
        
    def enhance_field_analysis(self, field_data: Dict) -> Dict:
        """Enhance field analysis with AI suggestions"""
        if not self.ollama.is_ollama_running():
            return field_data
        
        # Get AI suggestions for the field
        ai_suggestion = self.ollama.analyze_field_context(field_data)
        
        # Enhance field data with AI insights
        field_data['ai_suggestion'] = ai_suggestion
        field_data['ai_enhanced'] = True
        
        return field_data
    
    def suggest_content_for_field(self, field_context: str, user_input: str = "") -> str:
        """Get AI-powered content suggestions"""
        if not self.ollama.is_ollama_running():
            return ""
        
        return self.ollama.suggest_field_content(field_context, user_input)

