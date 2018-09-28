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
        if client_id not in self.client_leases.keys():
            self.client_leases[client_id] = utils.dedup_dict_list(
                body[client_id]
            )
        else:
            self.client_leases[client_id] = utils.dedup_dict_list(
                body[client_id][:]
            )
            if client_id not in self.actions:
                self.actions[client_id] = {}
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
        if action is "set" and "value" not in body:
            # Set action requires input
            return
        else:
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
