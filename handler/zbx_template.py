from handler.base import ZabbixBaseHandler


class ZbxTemplatehaHandler(ZabbixBaseHandler):
    def get(self, *args, **kwargs):
        argus = self.arguments if self.arguments else {}
        name = argus.pop('name', None)
        argus.update({'selectGroups': True})
        output = argus.pop('output',None)
        if output:
            output = output.split(',')
            argus.update({'output':output})
        res = self.zabbix.get_template(name=name, **argus)
        self.render_json_response(code=200, msg='OK', res=res)
