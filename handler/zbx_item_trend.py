from handler.base import ZabbixBaseHandler
from common.util import query_string_argus_to_list
from worker.zbx_item import get_item_key_by_name
from worker.zbx_item_trend import get_trend_items
from worker.host_filter import host_filter_by_cmdb, database_filter_by_cmdb
from conf import settings
from db.zabbix import ZABBIX
from db.mysql import ENGINES


class ZbxItemTrendHandler(ZabbixBaseHandler):

    def get(self, *args, **kwargs):
        res = dict(hosts=[], total_host=1)
        cmdb_hostname = self.get_argument("cmdb_hostname")

        # cmdb_filters = dict()
        item_filters = dict()
        # host_args_key = ('cmdb_host_status', 'cmdb_zone_name', 'cmdb_ip_name', 'cmdb_ip', 'cmdb_hostname',
        #                  'cmdb_application_name', 'cmdb_department_name', 'cmdb_business_group_name', 'cmdb_like')

        # cmdb api kwargs
        # cmdb_filters.update(self.get_args_dict(*host_args_key, prefix='cmdb_'))
        # cmdb_filters['page'] = int(self.get_argument("page", 1))
        # cmdb_filters['page_size'] = int(self.get_argument("page_size", 20))

        # env filter
        env = self.get_argument('cmdb_env_name', 'product')
        # cmdb_filters['env_name'] = env
        db_env = settings['cmdb_to_zbxdb_env_map'][env]
        zbx_session = self.zbx_sessions[db_env]
        # mc_session = self.zbx_sessions["monitor_center"]
        zbx_db = ZABBIX[db_env]
        zbx_engine = ENGINES[db_env]

        # zabbix kwargs
        # item_args_key = (
        #     'zbx_item_keys'
        # )
        # item_filters.update(self.get_argument('zbx_item_keys'))
        item_filters['item_keys'] = self.get_arguments('zbx_item_keys')
        item_filters['end_clock'] = int(self.get_argument('clock', 0))
        item_filters['trend_value'] = bool(int(self.get_argument('trend_value', 0))) # 是否获取  trend 值
        item_filters['link_ratio_type'] = int(self.get_argument('link_ratio_type', -1)) # 环比类型，-1 是不返回环比



        #  不同资源类型
        # resource_type = self.get_argument('resource_type', 'server')
        # if resource_type == 'DB':
        #     cmdb_host_info, total_host = database_filter_by_cmdb(**cmdb_filters)
        # else:  # server
        #     cmdb_host_info, total_host = host_filter_by_cmdb(**cmdb_filters)

        cmdb_host_info = {cmdb_hostname: {'hostname':cmdb_hostname}}
        if len(cmdb_host_info) > 0:
            # request host item
            # item_group = item_filters.pop('item_group')
            # for g in item_group:
            #     item_filters['item_keys'].extend(get_item_key_by_name(mc_session, g))
            # item_filters['item_keys'] = list(set(item_filters['item_keys']))
            host_items, item_count = get_trend_items(
                zbx_session=zbx_session,
                zbx_db=zbx_db,
                cmdb_host_info=cmdb_host_info,
                zbx_engine=zbx_engine,
                **item_filters)
            res['hosts'] = list(host_items.values())[0]

        self.render_json_response(code=200, msg='OK', res=res)
