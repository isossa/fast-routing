import concurrent
import json
import os

import timerit
from channels.generic.websocket import WebsocketConsumer
from django.http import HttpResponseRedirect
from django.urls import reverse

from cvrp.views import update_address_db, update_driver_db, reset_databases
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


class UploadFileConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, code):
        pass

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        print(text_data_json.values())
        filename = text_data_json['address_location']
        print(filename, settings.MEDIA_ROOT)
        filepaths = [os.path.join(settings.MEDIA_ROOT, filename) for filename in text_data_json.values()]
        print(filepaths)
        load_files(filepaths)
        # print('CHANNEL NAME', self.channel_name)
        print('SCOPE', self.scope)
        self.send(text_data=json.dumps({
            'message': 'Uploading data...'
        }))


class LoaderConsumer(WebsocketConsumer):
    def connect(self):
        reset_databases()
        self.accept()

    def disconnect(self, code):
        pass

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
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
