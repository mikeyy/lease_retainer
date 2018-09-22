#!/usr/bin/env python3

import requests
import subprocess
import sys


def get_device_id():
    if sys.platform == "win32":
        output = ssubprocess.check_output(
            "dmidecode.exe -s system-uuid".split()
        ).decode("ascii")
    else:
        output = "CLIENT6"
    return output



actions = ["set","new","reset"]

class Client(object):
    def __init__(self, server):
        self.client_id = get_device_id()
        self.server = server
        self.session = requests.Session()

    def update(self, changer_data):
        data = [data for data in changer_data]
        fields = {self.client_id: ""}
        fields[self.client_id] = data
        request = requests.Request(
            method="POST", url=f"http://{self.server}/update", json=fields
        ).prepare()
        try:
            self.session.send(request)
        except Exception:
            # Server down? Oh well.
            pass
            
    def recv(self, queue):
        while 1:
            fields = {"client_id": self.client_id}
            request = requests.Request(
                method="POST", url=f"http://{self.server}/listen", json=fields
            ).prepare()
            try:
                resp = self.session.send(request)
                data = resp.json()
                if data['action'] in actions:
                    action = data['action']
                    if action == "set":
                        pass # TODO
                    if action == "new":
                        pass # TODO
                    if action == "reset":
                        pass # TODO
            except Exception:
                # In check-up mode, tolerant delay advised.
                time.sleep(3)
            else:
                time.sleep(0.1)
