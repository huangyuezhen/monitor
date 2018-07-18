from handler.base import ZabbixBaseHandler
from common.util import query_string_argus_to_list
from worker.zbx_item import get_items, get_item_key_by_name
from worker.host_filter import host_filter_by_cmdb, cmdb_host_filter_order_by_item
from conf import settings
from db.zabbix import ZABBIX
from db.mysql import ENGINES


class ZbxHostItemHandler(ZabbixBaseHandler):
    # def get_args_dict(self, *args, prefix=""):
    #     res = {}
    #     for arg in args:
    #         a = self.get_arguments(arg)
    #         try:
    #             k = arg.split(prefix, 1)[1]
    #         except IndexError:
    #             k = arg
    #         res[k] = query_string_argus_to_list(a)
    #     return res

    def get(self):
        res = dict(hosts=[], total_host=0)
        cmdb_filters = dict()
        item_filters = dict()
        host_args_key = ('cmdb_host_status', 'cmdb_zone_name', 'cmdb_ip_name', 'cmdb_ip', 'cmdb_hostname',
                         'cmdb_application_name', 'cmdb_department_name', 'cmdb_business_group_name', 'cmdb_like')

        # cmdb api kwargs
        cmdb_filters.update(self.get_args_dict(*host_args_key, prefix='cmdb_'))
        cmdb_filters['page'] = int(self.get_argument("page", 1))
        cmdb_filters['page_size'] = int(self.get_argument("page_size", 20))

        # env filter
        env = self.get_argument('cmdb_env_name', 'product')
        cmdb_filters['env_name'] = env
        db_env = settings['cmdb_to_zbxdb_env_map'][env]
        zbx_session = self.zbx_sessions[db_env]
        mc_session = self.zbx_sessions["monitor_center"]
        zbx_db = ZABBIX[db_env]
        zbx_engine = ENGINES[db_env]

        # zabbix kwargs
        item_args_key = (
            'zbx_application_name',
            # 'zbx_item_keys',
            'item_group'
        )
        item_filters.update(self.get_args_dict(*item_args_key, prefix='zbx_'))
        item_filters['problem_trigger'] = bool(int(self.get_argument('problem_trigger', 0)))
        item_filters['last_value'] = bool(int(self.get_argument('last_value', 0)))
        item_filters['time_range_value'] = bool(int(self.get_argument('time_range_value', 0)))
        item_filters['start_clock'] = int(self.get_argument('start_clock', 0))
        item_filters['end_clock'] = int(self.get_argument('end_clock', 0))
        item_filters['mutil_history_value'] = bool(int(self.get_argument('mutil_history_value', 0)))
        item_filters['item_keys'] = self.get_arguments('zbx_item_keys')

        # item sort
        order_by_item_key = self.get_argument("order_by_item_key", None)
        if order_by_item_key is not None:
            order_by_item_desc = bool(int(self.get_argument('order_by_item_desc', 1)))
            cmdb_host_info, total_host = cmdb_host_filter_order_by_item(
                zbx_session=zbx_session,
                zbx_db=zbx_db,
                zbx_engine=zbx_engine,
                order_by_item_key=order_by_item_key,
                order_by_item_desc=order_by_item_desc,
                item_application_name=item_filters['application_name'],
                **cmdb_filters)
        else:
            cmdb_host_info, total_host = host_filter_by_cmdb(**cmdb_filters)

        if len(cmdb_host_info) > 0:
            # request host item
            item_group = item_filters.pop('item_group')
            for g in item_group:
                item_filters['item_keys'].extend(get_item_key_by_name(mc_session, g))
            item_filters['item_keys'] = list(set(item_filters['item_keys']))
            host_items, item_count = get_items(
                zbx_session=zbx_session,
                zbx_db=zbx_db,
                cmdb_host_info=cmdb_host_info,
                zbx_engine=zbx_engine,
                **item_filters)
            res['hosts'] = list(host_items.values())
            res['total_host'] = total_host

        self.render_json_response(code=200, msg='OK', res=res)
