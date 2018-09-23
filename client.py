#!/usr/bin/env python3

import requests
import subprocess
import sys
import time

import protocol


def get_device_id():
    output = subprocess.check_output(
        "wmic csproduct get uuid".split()
    ).decode("ascii")
    return output.split("\n")[1][:8]


changer = protocol.IPChanger()
actions = ["set", "new", "reset"]


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

    def recv(self):
        while 1:
            fields = {"client_id": self.client_id}
            request = requests.Request(
                method="POST", url=f"http://{self.server}/listen", json=fields
            ).prepare()
            try:
                resp = self.session.send(request)
                data = resp.json()
                if data["event"]["action"] in actions:
                    action = data["event"]["action"]
                    if action == "set":
                        value = data["event"]["value"]
                        changer.set_existing_address(value)
                    if action == "new":
                        changer.set_new_address()
                    if action == "reset":
                        changer.reset()
            except Exception:
                # In check-up mode, tolerant delay advised.
                time.sleep(3)
            else:
                time.sleep(0.1)
