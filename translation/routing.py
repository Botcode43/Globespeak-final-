"""
WebSocket URL routing for translation app
"""

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/translation/(?P<room_name>\w+)/$', consumers.TranslationConsumer.as_asgi()),
    re_path(r'ws/translation/$', consumers.TranslationConsumer.as_asgi()),  # Allow connection without room name
]
