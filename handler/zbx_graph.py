from handler.base import ZabbixBaseHandler
from worker.host_filter import host_db_filter_by_cmdb


class ZbxGraphHandler(ZabbixBaseHandler):
    def parser_params(self, params):
        param = {}
        for k, v in params.items():
            param.update({k: v.split()})
        return param

    def get(self):
        argus = self.arguments if self.arguments else {}

        filter_type = int(argus.pop('filter_type', 3))
        graph_name =None


        if filter_type ==1 or filter_type ==2:
            host = host_db_filter_by_cmdb(self, int(filter_type))
        else:
            graph_name = argus.pop('zabbix_graph_name', None)
            # if graph_name:
            #     graph_name = graph_name.split(',')
            host = None

        if argus:
            argus.pop('token', None)

        argus = self.parser_params(argus)
        params = {
            "output": ['graphid', 'name', "templateid", "flags"],
            "selectItems": ['itemid', 'name', "key_"],
            'selectHosts': ['host', 'hostid', 'name'],
            'selectTemplates': ['name', "tempalteid"],
            "templated": False,
            'inherited': False
        }
        params.update(argus)

        res = self.zabbix.get_graph(host=host,name=graph_name, **params)
        self.render_json_response(code=200, msg='OK', res=res)

    def post(self):
        argus = self.arguments
        if isinstance(argus, list):
            res = []
            for ii in argus:
                ii.update({"width": 900, "height": 200})
                resi = self.zabbix.add_graph(ii)
                res.append(resi)
        else:
            argus.update({
                "width": 900, "height": 200
            })
            res = self.zabbix.add_graph(argus)

        self.render_json_response(code=200, msg="OK", res=res)

    def delete(self):
        argus = self.arguments if self.arguments else {}
        graphids = argus.pop('graphids', None)
        # if not graphids:
        #     raise TypeError("Misiing argument graphids")
        # graphids = graphids.split(",")
        res = self.zabbix.delete_graph(graphids=graphids)
        self.render_json_response(code=200, msg="OK", res=res)
