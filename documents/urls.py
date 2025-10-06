from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.upload_document, name='upload_document'),
    path('clear-session/', views.clear_session, name='clear_session'),
    path('<uuid:doc_id>/', views.get_document, name='get_document'),
    path('<uuid:doc_id>/preview/', views.preview_document, name='preview_document'),
    path('<uuid:doc_id>/regenerate/', views.regenerate_document, name='regenerate_document'),
    path('<uuid:doc_id>/update-field/', views.update_field, name='update_field'),
    path('<uuid:doc_id>/generate-pdf/', views.generate_pdf, name='generate_pdf'),
    path('download/<uuid:doc_id>/', views.download_pdf, name='download_pdf'),
]
