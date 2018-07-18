from handler.base import ZabbixBaseHandler
from conf import settings
from db.zabbix import ZABBIX
from worker.zbx_screen import screen_filter_by_name


class ZbxScreenHandler(ZabbixBaseHandler):
    def get(self):
        # argus = self.arguments if self.arguments else {}
        # name = argus.pop('name', None)
        # params = {
        #     'selectScreenItems': 'extend'
        # }
        # res = self.zabbix.get_screen(name=name, **params)
        # self.render_json_response(code=200, msg='OK', res=res)
        argus = self.arguments if self.arguments else {}
        name = argus.pop('name', '')
        like = int(argus.pop('like', 0))

        env = self.get_argument('cmdb_env_name', 'product')
        db_env = settings['cmdb_to_zbxdb_env_map'][env]
        zbx_session = self.zbx_sessions[db_env]
        zbx_db = ZABBIX[db_env]

        query = zbx_session.query(zbx_db.screens)
        if name:
            query = screen_filter_by_name(query=query, case_sensitive=None, name=name.split(','), like=like,
                                          zbx_db=zbx_db)
        res = []
        total_count = query.count()
        for ii in query.all():
            ii.__dict__.pop('_sa_instance_state')
            res.append(ii.__dict__)
        self.render_json_response(code=200, msg='OK', res=res,total_count=total_count)

    def post(self):
        argus = self.arguments
        res = self.zabbix.add_screen(**argus)
        self.render_json_response(code=200, msg="OK", res=res)

    def delete(self):
       argus = self.arguments if self.arguments else {}
       screenids = argus.pop('screenids',[])
       res =self.zabbix.delete_screen(screenids)
       self.render_json_response(code=200,msg='OK',res=res)