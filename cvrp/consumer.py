import concurrent
import json
import os

import pandas as pd
import timerit
from channels.generic.websocket import WebsocketConsumer
from django.core.files.storage import FileSystemStorage

from cvrp.views import update_address_db


def handle_file_upload(file):
    file_storage = FileSystemStorage()
    filename = file_storage.save(file.name, file)
    filepath = file_storage.path(filename)
    print(filename, filepath)

    data = pd.read_excel(filepath)

    update_address_db(filepath)


def load_files(files):
    timer = timerit.Timerit(verbose=2)
    for time in timer:
        with concurrent.futures.thread.ThreadPoolExecutor(max_workers=os.cpu_count() - 1) as executor:
            executor.map(handle_file_upload, files)


class UploadFileConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, code):
        pass

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        print(text_data_json)
        message = text_data_json['address_location']
        print(message)

        while True:
            self.send(text_data=json.dumps({
                'message': 'Uploading data...'
            }))

