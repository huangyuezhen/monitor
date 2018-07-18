from worker.host_filter import get_cmdb_host_filter_options, get_zbx_host_filter_options
from handler.base import BaseHandler, ZabbixBaseHandler


class HostFilterOptionHandler(ZabbixBaseHandler):
    def get(self):
        res = {}
        zbx_options = get_zbx_host_filter_options(self.zbx_sessions)
        res.update(zbx_options)
        # cmdb_options = get_cmdb_host_filter_options()
        # res.update(cmdb_options)
        self.render_json_response(code=200, msg='OK', res=res)
