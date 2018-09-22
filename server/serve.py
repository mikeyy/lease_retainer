import os
import cherrypy
import simplejson
import pprint

from mako.template import Template

def dedup_dict_list(x):
    y = []
    for a in x:
        if a['ip_address'] not in [b['ip_address'] for b in y]:
            y.append(a)
    return y

class Root(object):
    client_leases = {}
    @cherrypy.expose
    def update(self):
        cl = cherrypy.request.headers['Content-Length']
        rawbody = cherrypy.request.body.read(int(cl))
        body = simplejson.loads(rawbody)
        client_id = next(iter(body.keys()))
        if client_id not in self.client_leases.keys():
            self.client_leases[client_id] = dedup_dict_list(body[client_id])
        else:
            self.client_leases[client_id] = dedup_dict_list(body[client_id][:])
        pp = pprint.PrettyPrinter(indent=2)
        print(pp.pprint(self.client_leases))

    @cherrypy.expose
    def index(self):
        data = {'client_leases': self.client_leases.copy()}
        mytemplate = Template(filename='template/base.mako')
        return mytemplate.render(**data)




cherrypy.config.update({
    'server.socket_port': 9999,
    'tools.encode.on': True,
    'tools.encode.encoding': 'utf-8'
    })
conf = {
    '/': {'tools.staticdir.root': os.path.abspath(os.getcwd())},
    '/static': {
        'tools.staticdir.on':True,
        'tools.staticdir.dir': "static"
    },
}
if __name__ == '__main__':
    cherrypy.tree.mount(Root(), '/', conf)
    cherrypy.engine.start()
    cherrypy.engine.block()