import concurrent
import json
import os

import timerit
from channels.generic.websocket import WebsocketConsumer
from django.http import HttpResponseRedirect
from django.urls import reverse

from cvrp.views import update_address_db, update_driver_db
from routing import settings


def handle_file_upload(filepath):
    try:
        update_address_db(filepath)
    except:
        pass

    try:
        update_driver_db(filepath)
    except:
        pass


def load_files(filepaths):
    print('LOAD FILES', filepaths)
    timer = timerit.Timerit(verbose=2)
    for _ in timer:
        with concurrent.futures.thread.ThreadPoolExecutor(max_workers=os.cpu_count() - 1) as executor:
            executor.map(handle_file_upload, filepaths)


class LoaderConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, code):
        pass

    def receive(self, text_data=None, bytes_data=None):
        filepaths = []
        for f in os.scandir(settings.MEDIA_ROOT):
            if f.is_file():
                filepaths.append(f.path)
        load_files(filepaths)
        for filepath in filepaths:
            os.remove(filepath)
        message = 'DONE'
        self.send(text_data=json.dumps({
            'message': message
        }))
        return HttpResponseRedirect(reverse('create_routes'))
