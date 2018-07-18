from handler.base import ZabbixBaseHandler
from common.util import query_string_argus_to_list
from worker.zbx_item import get_items, get_item_key, get_item_key_by_name
from conf import settings
from db.zabbix import ZABBIX
from db.mysql import ENGINES
from collections import OrderedDict


class ZbxItemHandler(ZabbixBaseHandler):
    def get_args_dict(self, *args, prefix=""):
        res = {}
        for arg in args:
            a = self.get_arguments(arg)
            try:
                k = arg.split(prefix, 1)[1]
            except IndexError:
                k = arg
            res[k] = query_string_argus_to_list(a)
        return res

    def get(self):
        res = dict(hosts=[], total_host=0)
        item_filters = dict()

        hosts = self.get_arguments('hosts')
        hosts = query_string_argus_to_list(hosts)
        host_info = OrderedDict()
        for h in hosts:
            host_info[h] = {'hostname': h, 'zbx_items': {}}

        # env filter
        env = self.get_argument('cmdb_env_name', 'product')
        db_env = settings['cmdb_to_zbxdb_env_map'][env]
        zbx_session = self.zbx_sessions[db_env]
        mc_session = self.zbx_sessions["monitor_center"]
        zbx_db = ZABBIX[db_env]
        zbx_engine = ENGINES[db_env]

        # zabbix kwargs
        item_args_key = ('zbx_application_name', 'item_group')
        item_filters.update(self.get_args_dict(*item_args_key, prefix='zbx_'))
        item_filters['item_keys'] = self.get_arguments('zbx_item_keys')
        item_filters['problem_trigger'] = bool(int(self.get_argument('problem_trigger', 0)))
        item_filters['last_value'] = bool(int(self.get_argument('last_value', 0)))
        item_filters['time_range_value'] = bool(int(self.get_argument('time_range_value', 0)))
        item_filters['start_clock'] = int(self.get_argument('start_clock', 0))
        item_filters['end_clock'] = int(self.get_argument('end_clock', 0))
        item_filters['mutil_history_value'] = bool(int(self.get_argument('mutil_history_value', 0)))

        if len(host_info) > 0:
            item_group = item_filters.pop('item_group')
            for g in item_group:
                item_filters['item_keys'].extend(get_item_key_by_name(mc_session, g))
            item_filters['item_keys'] = list(set(item_filters['item_keys']))
            host_items, item_count = get_items(
                zbx_session=zbx_session, zbx_db=zbx_db, cmdb_host_info=host_info, zbx_engine=zbx_engine, **item_filters)
            res['hosts'] = list(host_items.values())
            res['total_host'] = len(hosts)

        self.render_json_response(code=200, msg='OK', res=res)


class ItemKey(ZabbixBaseHandler):
    def get(self):
        # env filter
        env = self.get_argument('cmdb_env_name', 'product')
        db_env = settings['cmdb_to_zbxdb_env_map'][env]
        zbx_session = self.zbx_sessions[db_env]
        zbx_db = ZABBIX[db_env]
        like_str = self.get_argument('like', None)

        res, total_count = get_item_key(zbx_session, zbx_db, like=like_str)
        self.render_json_response(code=200, msg='OK', res=res, total_count=total_count)
