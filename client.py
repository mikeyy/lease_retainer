#!/usr/bin/env python3

import requests
import subprocess
import sys

def get_device_id():
    if sys.platform == "win32":
        output = ssubprocess.check_output('dmidecode.exe -s system-uuid'.split()).decode("ascii")
    else:
        output = "CLIENT1"
    return output


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
            method="POST",
            url=f"http://{self.server}/update",
            json=fields,
        ).prepare()
        # Let's hope the server doesn't experience downtime...
        self.session.send(request)