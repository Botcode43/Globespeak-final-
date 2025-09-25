"""
URL configuration for translation app
"""

from django.urls import path
from . import views

urlpatterns = [
    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Main application URLs
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('translate/', views.text_translation, name='text_translation'),
    path('simple-conversation/', views.simple_conversation, name='simple_conversation'),
    path('image/', views.image_translation, name='image_translation'),
    path('history/', views.history, name='history'),
    path('summarize/', views.summarize, name='summarize'),
    
    # Video Summarization URLs
    path('video/upload/', views.video_upload, name='video_upload'),
    path('video/summarize/<int:video_id>/', views.video_summarize, name='video_summarize'),
    path('video/summarize-url/<int:video_id>/', views.video_summarize_url, name='video_summarize_url'),
    path('video/process-url/<int:video_id>/', views.video_process_url, name='video_process_url'),
    path('video/history/', views.video_history, name='video_history'),
    path('video/detail/<int:video_id>/', views.video_detail, name='video_detail'),
    path('video/delete/<int:video_id>/', views.delete_video, name='delete_video'),
    
    # API URLs
    path('api/translate/', views.api_translate, name='api_translate'),
    path('api/tts/', views.api_tts, name='api_tts'),
    path('api/process-conversation-audio/', views.api_process_conversation_audio, name='api_process_conversation_audio'),
    
    
    # Media serving URLs
    path('media/audio/<str:filename>/', views.serve_audio, name='serve_audio'),
    path('media/images/<str:filename>/', views.serve_image, name='serve_image'),
]
