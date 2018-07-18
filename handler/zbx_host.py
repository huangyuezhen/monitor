from conf import settings
from db.zabbix import ZABBIX
from db.mysql import ENGINES

from handler.base import ZabbixBaseHandler
from worker.host_filter import filter_cmdb_host, filter_cmdb_database
from worker.zbx_host import get_cmdb_database
from worker.zbx_host import get_application_items_by_hostid
from worker.host_filter import host_filter_by_cmdb


class ZbxHostHandler(ZabbixBaseHandler):
    # def prepare(self):
    #     super(ZbxHostHandler, self).prepare()
    #     self.zabbix = ZabbixUtil(zabbix_api)
    def parser_params(self, params):
        param = {}
        for k, v in params.items():
            if v:
                param.update({k: v.split()})
            else:
                param.update({k: v})
        return param

    def get(self, *args, **kwargs):

        # env filter
        env = self.get_argument('cmdb_env_name', 'product')
        db_env = settings['cmdb_to_zbxdb_env_map'][env]
        zbx_session = self.zbx_sessions[db_env]
        zbx_db = ZABBIX[db_env]

        # res = dict(hosts=[], total_host=0)
        argus = self.arguments
        cmdb_filters = dict()
        filter_type = int(argus.pop('filter_type', 1))
        cmdb_host_info = dict()
        zbx_host_index = int(argus.pop('zbx_host_index', 1))
        application_item_index = int(argus.pop('application_item_index', 0))

        if filter_type == 3 and zbx_host_index == 0:  # 0: 非监控主机，3：筛选类型 为zabbix
            raise TypeError('zbx_host_index: 0 , cannot use filter_typ ,please use 1 or 2 ')

        if filter_type == 1:
            cmdb_host_info = filter_cmdb_host(self, cmdb_filters)
            if not cmdb_host_info:
                return self.render_json_response(code=200, msg='OK', res=[])
        elif filter_type == 2:
            cmdb_host_info = filter_cmdb_database(self, cmdb_filters)
            if not cmdb_host_info:
                return self.render_json_response(code=200, msg='OK', res=[])
        elif filter_type == 3:
            # else:
            argus = self.parser_params(argus)
            # pass

        host = list(cmdb_host_info.keys()) if cmdb_host_info else None
        argus.update({
            "output": ["hostid", 'name', 'host', 'status', 'proxy_hostid', 'description', 'available'],
            "selectGroups": ["groupid", "name"],
            "selectParentTemplates": [
                "templateid",
                "name"
            ],
            'selectInterfaces': "extend",
            "selectGraphs": ["graphid", "name"],
            # 'selectItems': ["itemid", "name", "key_", "status", "error"],
            'selectItems': 'count',
            'selectApplications': 'count',
            'selectTriggers': 'count',
            'selectMacros': 'count',
            'selectScreens': 'count',
            'sortfield': 'status'
        })
        zbx_res = self.zabbix.get_host(hostid=None, host=host, **argus)

        if zbx_host_index == 1:  # 只返回 zbx监控的数据
            if not cmdb_host_info:
                hostnames = [item['host'] for item in zbx_res]
                cmdb_host_info, total_host = host_filter_by_cmdb(hostname=hostnames)

                cmdb_filters.update({'ip_name': hostnames})
                cmdb_db_info = get_cmdb_database(cmdb_filters)
                cmdb_host_info.update(cmdb_db_info)

            for obj in zbx_res:
                hostname = obj['host']
                if hostname in cmdb_host_info:
                    obj.update(cmdb_host_info[hostname])
            for item in zbx_res:
                item.update({'zbx_index': 1})
            # res = [item['zbx_index']= 1]
            res = zbx_res
        elif zbx_host_index == 0:  # 只返回未监控的数据
            zbx_host = [item['host'] for item in zbx_res]
            for ii in zbx_host:
                cmdb_host_info.pop(ii, None)
            for item in list(cmdb_host_info.values()):
                item.update({'zbx_index': 0})
            res = list(cmdb_host_info.values())
        else:  # 返回全部，包括监控与非监控
            for obj in zbx_res:
                hostname = obj['host']
                if hostname in cmdb_host_info:
                    obj.update(cmdb_host_info[hostname])
                    cmdb_host_info[hostname] = obj

            zbx_host = [item['host'] for item in zbx_res]
            for host_name in cmdb_host_info:
                if host_name in zbx_host:
                    cmdb_host_info[host_name].update({
                        'zbx_index': 1,
                        'cmdb_hostname': host_name
                    })
                else:
                    cmdb_host_info[host_name].update({
                        'zbx_index': 0,
                        'cmdb_hostname': host_name
                    })
            res = list(cmdb_host_info.values())

        if application_item_index:
            zbx_hostids = [item['hostid'] for item in zbx_res]
            applications_items_dict = get_application_items_by_hostid(zbx_session, zbx_db, zbx_hostids)
            for ii in res:
                if "hostid" in ii.keys():
                    hostid = int(ii['hostid'])
                else:
                    ii.update({"application_item": []})
                    break
                # a = applications_items_dict.keys()
                if hostid in applications_items_dict.keys():
                    application_item = applications_items_dict[hostid]
                    ii.update({"application_item": application_item})
                else:
                    ii.update({"application_item": []})
        self.render_json_response(code=200, msg='OK', res=res)

    def post(self):
        argus = self.arguments
        group_names = argus.pop('group_names', None)
        template_names = argus.pop('template_names', None)
        host_info = argus.pop('host_info', [])

        all_res = []
        for ii in host_info:
            host = ii['hostname']
            agent_ip = ii['agent_ip']
            res = self.zabbix.create_host(host, agent_ip=agent_ip, group_names=group_names,
                                          template_names=template_names,
                                          **argus)
            all_res.append(res)
        self.render_json_response(code=200, msg='OK', res=all_res)

    def put(self):
        argus = self.arguments
        operator_type = argus.pop('operator_type', None)
        if not operator_type:
            raise TypeError("missing argument operator_type")

        hostids = argus.pop('hostids', None)
        hostnamse = argus.pop('hostnames', None)
        operator_type = int(operator_type)

        if operator_type == 1:  # mass_update
            proxy_hostid = argus.get('proxy_hostid', None)
            if proxy_hostid == -1:
                argus['proxy_hostid'] = None
            res = self.zabbix.mass_update_host(hostids=hostids, hostnames=hostnamse, **argus)
        elif operator_type == 2:  # mass_add
            res = self.zabbix.mass_add_host(hostids=hostids, hostnames=hostnamse, **argus)
        elif operator_type == 3:  # mass_remove
            res = self.zabbix.mass_remove_host(hostids=hostids, hostnames=hostnamse, **argus)
        else:
            raise TypeError("argument operator_type value error ,should be in [1,2,3]")

        self.render_json_response(code=200, msg='OK', res=res)

    def delete(self, *args, **kwargs):
        argus = self.arguments
        hostids = argus.pop('hostids', None)
        if hostids:
            hostids = hostids.split(',')
        hostnames = argus.pop('hostnames', None)
        if hostnames:
            hostnames = hostnames.split(',')
        res = self.zabbix.delete_host(hostids=hostids, hostnames=hostnames)
        self.render_json_response(code=200, msg='OK', res=res)
