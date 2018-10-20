import cherrypy
import functools
import os
import simplejson
import time

from libs import moments
from libs import utils

from mako.template import Template

def auth_from_remote(func):
    @functools.wraps(func)
    def _auth_from_remote(*args, **kwargs):
        with open('allow.txt') as f:
            whitelist = f.readlines()
        if cherrypy.request.remote.ip not in [
            remote.strip('\n') for remote in whitelist]:
            return "You shall not pass."
        else:
            return func(*args, **kwargs)
    return _auth_from_remote


DEAD_CLIENT_TIMEOUT = 30  # seconds

class Root(object):
    actions = {}
    client_leases = {}
    

    @cherrypy.expose
    def update(self):
        cl = cherrypy.request.headers["Content-Length"]
        rawbody = cherrypy.request.body.read(int(cl))
        body = simplejson.loads(rawbody)
        for key, value in body.items():
            for lease in value:
                if "nickname" not in lease:
                    lease["nickname"] = None
                lease["expiration"] = moments.date(
                    utils.in_datetime(lease["expiration"])
                )
        client_id = next(iter(body.keys()))
        client_data = utils.dedup_dict_list(
            body[client_id]
        )
        if client_id:
            self.client_leases[client_id] = {}
            self.client_leases[client_id]["leases"] = client_data
            if client_id not in self.client_leases.keys()\
               and utils.check_duplicate_leases(self.client_leases, client_data):
               self.client_leases[client_id]["leases"] = client_data
            else:
                if client_id not in self.actions:
                    self.actions[client_id] = {}
            self.client_leases[client_id]["last_active"] = time.time()
        return "success"

    @cherrypy.expose
    @auth_from_remote
    def send_event(self):
        cl = cherrypy.request.headers["Content-Length"]
        rawbody = cherrypy.request.body.read(int(cl))
        body = simplejson.loads(rawbody)
        client_id = body["client_id"]
        action = body["action"]
        self.actions[client_id] = {"event": {"action": "", "value": ""}}
        if action == "set":
            # ssz
            if "value" not in body:
                # Set action requires input
                return
            value = body["value"]
            self.actions[client_id]["event"]["value"] = value
        self.actions[client_id]["event"]["action"] = action
        return "success"

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def listen(self):
        cl = cherrypy.request.headers["Content-Length"]
        rawbody = cherrypy.request.body.read(int(cl))
        body = simplejson.loads(rawbody)
        client_id = body["client_id"]
        if client_id in self.actions:
            if "event" in self.actions[client_id]:
                if len(self.actions[client_id]["event"]):
                    event = self.actions[client_id].copy()
                    self.actions[client_id]["event"] = {}
                    return event

    @cherrypy.expose
    @auth_from_remote
    def index(self):
        client_leases = self.client_leases.copy()
        for key in client_leases.keys():
            print(client_leases[key]["last_active"], time.time() - DEAD_CLIENT_TIMEOUT)
            if client_leases[key]["last_active"] <= time.time() - DEAD_CLIENT_TIMEOUT:
                del self.client_leases[key]
        data = {"client_leases": self.client_leases.copy()}
        mytemplate = Template(filename="template/base.mako")
        return mytemplate.render(**data)


cherrypy.config.update(
    {
        "server.socket_port": 9999,
        "tools.encode.on": True,
        "tools.encode.encoding": "utf-8",
    }
)
cherrypy.tools.authenticate = cherrypy.Tool('before_handler', auth_from_remote)
if __name__ == "__main__":
    cherrypy.server.socket_host = '0.0.0.0'
    cherrypy.quickstart(Root(), "/")
