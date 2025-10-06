from django.contrib import admin
from .models import Document, DocumentField

class DocumentFieldInline(admin.TabularInline):
    model = DocumentField
    extra = 0
    readonly_fields = ['id', 'area', 'ai_enhanced']

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['filename', 'id', 'uploaded_at', 'status', 'total_blanks']
    list_filter = ['status', 'uploaded_at']
    search_fields = ['filename', 'extracted_text']
    readonly_fields = ['id', 'uploaded_at']
    inlines = [DocumentFieldInline]

@admin.register(DocumentField)
class DocumentFieldAdmin(admin.ModelAdmin):
    list_display = ['id', 'document', 'field_type', 'context', 'user_content']
    list_filter = ['field_type', 'context', 'ai_enhanced']
    search_fields = ['user_content', 'suggested_content', 'ai_suggestion']



