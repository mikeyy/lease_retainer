import cherrypy
import simplejson
import pprint


def dedup_dict_list(x):
    y = []
    for a in x:
        if a['ip_address'] not in [b['ip_address'] for b in y]:
            y.append(a)
    return y


class Root(object):
    clients_data = {}
    @cherrypy.expose
    def update(self):
        cl = cherrypy.request.headers['Content-Length']
        rawbody = cherrypy.request.body.read(int(cl))
        body = simplejson.loads(rawbody)
        client_id = body.keys()[0]
        if client_id not in self.clients_data.keys():
            self.clients_data[client_id] = dedup_dict_list(body[client_id])
        else:
            self.clients_data[client_id] = dedup_dict_list(body[client_id][:])
        pp = pprint.PrettyPrinter(indent=2)
        print(pp.pprint(self.clients_data))

    @cherrypy.tools.mako(template="template/index.mako")
    @cherrypy.expose
    def index(self):
        return

# {"client_id": 123, "mac_address": "021C420EEA2E", "ip_address": "76.170.255.59"}

if __name__ == '__main__':
    from mako.template import Template
    from mako.lookup import TemplateLookup
    
    DEBUG_MODE=False
    lookup = TemplateLookup( directories=['template'], module_directory="cache",
                       output_encoding="utf-8", encoding_errors="replace",
                       filesystem_checks=DEBUG_MODE)
    cherrypy.quickstart(Root())