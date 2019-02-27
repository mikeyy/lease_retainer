#!/usr/bin/env python3

import requests
import time

import protocol

from utils import assign_nickname, remove_address

from queue import Queue
from threading import Thread

changer = protocol.IPChanger()
actions = ["set", "new", "reset", "assign_nickname", "remove"]
action_queue = Queue()


def run_actions():
    while 1:
        d = action_queue.get()
        if 'arg' in d:
            d['func'](d['arg'])
        else:
            d['func']()
        time.sleep(60)


def get_location():
    while 1:
        try:
            resp = requests.get("https://ipapi.co/json/")
            data = resp.json()
            return f"{data['city']}, {data['region_code']}"
        except Exception:
            # Server down? Oh well.
            pass
        time.sleep(1)


class Client(object):
    def __init__(self, server):
        self.client_id = get_location()
        self.server = server
        self.session = requests.Session()

    def update(self, changer_data, current_address):
        fields = {self.client_id: "", "current_address": current_address}
        fields[self.client_id] = changer_data
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
                    if action == "remove":
                        address = data["event"]["value"]
                        remove_address(address)
                    if action == "new":
                        action_queue.put({"func": changer.set_new_address})
                    if action == "set":
                        value = data["event"]["value"]
                        action_queue.put({
                                          "func": changer.set_existing_address,
                                          "arg": value
                                          })
                    if action == "reset":
                        changer.reset()
                    if action == "assign_nickname":
                        address = data["event"]["value"]["address"]
                        nickname = data["event"]["value"]["nickname"]
                        assign_nickname(address, nickname)
            except Exception:
                # In check-up mode, tolerant delay advised.
                time.sleep(5)
            else:
                time.sleep(0.1)


Thread(target=run_actions).start()
