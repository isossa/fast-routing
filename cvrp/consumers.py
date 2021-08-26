import concurrent
import json
import os
import time
from pprint import pprint

import pandas as pd
import timerit
from channels.generic.websocket import WebsocketConsumer
from django.core.files.storage import FileSystemStorage

from cvrp.views import update_address_db
from routing import settings


def handle_file_upload(filepath):
    data = pd.read_excel(filepath)
    update_address_db(filepath)


def load_files(filepaths):
    timer = timerit.Timerit(verbose=2)
    for time in timer:
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
        self.accept()

    def disconnect(self, code):
        pass

    def receive(self, text_data=None, bytes_data=None):
        start_time = time.time()
        print(start_time)
        # end_time = start_time + 100000
        text_data_json = json.loads(text_data)
        message = text_data_json['counter']
        print('Received ' + str(message))

        self.send(text_data=json.dumps({
            'message': message
        }))
