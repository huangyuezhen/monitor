from handler.base import ZabbixBaseHandler


class ZbxHostGroupHandler(ZabbixBaseHandler):
    def get(self):
        argus = self.arguments if self.arguments else {}
        name = argus.pop('name',None) if argus else None
        res = self.zabbix.get_host_group(name=name,**argus)
        self.render_json_response(code=200, msg='OK', res=res)
