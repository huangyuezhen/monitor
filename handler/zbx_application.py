from handler.base import ZabbixBaseHandler


class ZbxApplicationHandler(ZabbixBaseHandler):
    def parser_params(self, params):
        param = {}
        for k, v in params.items():
            param.update({k: v.split()})
        return param

    def get(self):
        argus = self.arguments
        name = argus.pop("name", None) if argus else None
        argus.pop('token', None) if argus else None
        argus = self.parser_params(argus) if argus else {}

        param = {
            "output": "extend",
            "sortfield": "name",
            "selectItems": ['name', '_key', "itemid"]
        }
        param.update(argus)
        res = self.zabbix.get_applications(name=name, **param)
        self.render_json_response(code=200, msg="Ok", res=res)
