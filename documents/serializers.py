from rest_framework import serializers
from .models import Document, DocumentField

class DocumentFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentField
        fields = ['id', 'field_type', 'x_position', 'y_position', 'width', 'height', 
                 'area', 'suggested_content', 'user_content', 'ai_suggestion', 
                 'ai_enhanced', 'context']

class DocumentSerializer(serializers.ModelSerializer):
    fields = DocumentFieldSerializer(many=True, read_only=True)
    
    class Meta:
        model = Document
        fields = ['id', 'filename', 'file_path', 'uploaded_at', 'status', 
                 'extracted_text', 'total_blanks', 'fields']



