from django.urls import path
from . import views

urlpatterns = [
    path('general/', views.general_chat, name='general_chat'),
    path('<uuid:doc_id>/', views.chat_with_bot, name='chat_with_bot'),
    path('<uuid:doc_id>/history/', views.get_chat_history, name='get_chat_history'),
    path('<uuid:doc_id>/fill-all/', views.fill_all_fields, name='fill_all_fields'),
    path('ollama/status/', views.ollama_status, name='ollama_status'),
    path('ollama/pull-model/', views.pull_ollama_model, name='pull_ollama_model'),
    path('<uuid:doc_id>/suggest-content/', views.suggest_field_content, name='suggest_field_content'),
]

