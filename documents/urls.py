from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.upload_document, name='upload_document'),
    path('ai-fill/<uuid:doc_id>/', views.ai_fill_html_document, name='ai_fill_html_document'),
    path('generate-pdf/<uuid:doc_id>/', views.generate_pdf_from_html, name='generate_pdf_from_html'),
    path('clear-session/', views.clear_session, name='clear_session'),
    path('<uuid:doc_id>/', views.get_document, name='get_document'),
]
