from handler.base import ZabbixBaseHandler


class ZbxProxyHandler(ZabbixBaseHandler):
    def get(self):
        argus =self.arguments if self.arguments else {}
        output = argus.pop('output',None)
        if output:
            output = output.split(',')
            argus.update({
                'output': output
            })
        res =self.zabbix.get_proxy(**argus)
        self.render_json_response(code=200,msg="OK",res=res)

