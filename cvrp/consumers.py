import concurrent
import json
import os

import timerit
from channels.generic.websocket import WebsocketConsumer
from django.http import HttpResponseRedirect
from django.urls import reverse

from cvrp.views import update_address_db, update_driver_db, get_matrices
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


def update_matrices(update=False):
    if update:
        get_matrices()
    else:
        filepaths = []
        for f in os.scandir(settings.LOCAL_CACHE_ROOT):
            if f.is_file() and (f.path.find('distance_matrix') != -1 or f.path.find('duration_matrix') != -1):
                filepaths.append(f.path)
        if len(filepaths) == 0 or update:
            get_matrices()


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

        client_data = json.loads(text_data)
        update_matrices(client_data['update_matrix'] == 'on')

        message = 'DONE'
        self.send(text_data=json.dumps({
            'message': message
        }))
        return HttpResponseRedirect(reverse('create_routes'))
