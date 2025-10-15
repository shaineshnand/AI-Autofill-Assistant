from django.urls import path
from . import views
from . import universal_views

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.upload_document, name='upload_document'),
    path('upload-fillable/', views.upload_fillable_pdf, name='upload_fillable_pdf'),
    path('upload-sejda/', views.upload_document_with_sejda, name='upload_document_with_sejda'),
    path('clear-session/', views.clear_session, name='clear_session'),
    path('<uuid:doc_id>/', views.get_document, name='get_document'),
    path('<uuid:doc_id>/preview/', views.preview_document, name='preview_document'),
    path('<uuid:doc_id>/regenerate/', views.regenerate_document, name='regenerate_document'),
    path('<uuid:doc_id>/make-fillable/', views.make_fillable_pdf, name='make_fillable_pdf'),
    path('<uuid:doc_id>/update-field/', views.update_field, name='update_field'),
    path('<uuid:doc_id>/delete-field/', views.delete_field, name='delete_field'),
    path('<uuid:doc_id>/generate-pdf/', views.generate_pdf, name='generate_pdf'),
    path('<uuid:doc_id>/train/', views.manual_train, name='manual_train'),
    path('api/training-stats/', views.get_training_stats, name='get_training_stats'),
    path('download/<uuid:doc_id>/', views.download_pdf, name='download_pdf'),
    
    # Universal Document Processing URLs
    path('api/universal/upload/', universal_views.upload_document_universal, name='upload_document_universal'),
    path('api/universal/train/', universal_views.train_model, name='train_model'),
    path('api/universal/template/', universal_views.create_template, name='create_template'),
    path('api/universal/stats/', universal_views.get_system_stats, name='get_system_stats'),
    path('api/universal/patterns/', universal_views.get_field_patterns, name='get_field_patterns'),
    path('api/universal/fill/', universal_views.fill_document_universal, name='fill_document_universal'),
    path('api/universal/document-types/', universal_views.get_document_types, name='get_document_types'),
    path('api/universal/add-sample/', universal_views.add_training_sample, name='add_training_sample'),
    path('api/universal/export/', universal_views.export_training_data, name='export_training_data'),
    path('api/universal/import/', universal_views.import_training_data, name='import_training_data'),
]
