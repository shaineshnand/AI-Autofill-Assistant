from django.db import models
from django.contrib.auth.models import User
import uuid

class Document(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    filename = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default='uploaded')
    extracted_text = models.TextField(blank=True)
    total_blanks = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.filename} ({self.id})"

class DocumentField(models.Model):
    FIELD_TYPES = [
        ('name', 'Name'),
        ('address', 'Address'),
        ('phone', 'Phone'),
        ('email', 'Email'),
        ('date', 'Date'),
        ('signature', 'Signature'),
        ('general', 'General'),
    ]
    
    id = models.AutoField(primary_key=True)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='fields')
    field_type = models.CharField(max_length=20, choices=FIELD_TYPES, default='general')
    x_position = models.IntegerField()
    y_position = models.IntegerField()
    width = models.IntegerField()
    height = models.IntegerField()
    area = models.IntegerField()
    suggested_content = models.TextField(blank=True)
    user_content = models.TextField(blank=True)
    ai_suggestion = models.TextField(blank=True)
    ai_enhanced = models.BooleanField(default=False)
    context = models.CharField(max_length=100, default='general')
    
    class Meta:
        ordering = ['id']
    
    def __str__(self):
        return f"Field {self.id} ({self.field_type}) - {self.document.filename}"



