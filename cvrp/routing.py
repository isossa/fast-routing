from django.urls import path

from . import consumer

websocket_urlpatterns = [
    path(r'ws/upload-files/', consumer.UploadFileConsumer.as_asgi()),
]
