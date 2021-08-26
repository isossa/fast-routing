from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path(r'ws/upload-files/', consumers.UploadFileConsumer.as_asgi()),
    path(r'ws/settings/load/', consumers.LoaderConsumer.as_asgi()),
]
