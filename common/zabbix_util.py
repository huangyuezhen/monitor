from common.sdk.zbx_sdk import ZbxSdkException


class ZbxNotFoundError(ZbxSdkException):
    pass


class ZabbixUtil(object):
    def __init__(self, zabbix_api):
        self.zabbix_api = zabbix_api

    def _diff_filter_count(self, api_result, params, filter_key):
        if 'filter' in params and filter_key in params['filter']:
            filter_name = params['filter'][filter_key]
            if isinstance(filter_name, (tuple, list)):
                temp_count = len(filter_name)
            else:
                filter_name = [filter_name]
                temp_count = 1

            if len(api_result) != temp_count:
                not_found_name = set(filter_name) - set([i[filter_key] for i in api_result])
                raise ZbxNotFoundError('find %s not found: %s' % (filter_key, ','.join(not_found_name)))

    def _param_to_filter(self, params, **kwargs):
        if 'filter' not in params and kwargs:
            filter_params = {k: v for k, v in kwargs.items() if v is not None}
            if filter_params:
                params['filter'] = filter_params
        return params

    def get_host_group(self, name=None, **params):
        params = self._param_to_filter(params, name=name)
        res = self.zabbix_api.run('hostgroup.get', **params)
        self._diff_filter_count(res, params, 'name')
        return res

    def get_proxy(self, host=None, **params):
        params = self._param_to_filter(params, host=host)
        res = self.zabbix_api.run('proxy.get', **params)
        self._diff_filter_count(res, params, 'name')
        return res

    def get_template(self, name=None, **params):
        params = self._param_to_filter(params, host=name)
        res = self.zabbix_api.run('template.get', **params)
        self._diff_filter_count(res, params, 'host')
        return res

    def get_host(self, hostid=None, host=None, ip=None, **params):
        params = self._param_to_filter(params, hostid=hostid, host=host)
        if 'search' not in params:
            if ip is not None:
                params['search'] = {'ip': ip}

        res = self.zabbix_api.run('host.get', **params)
        # self._diff_filter_count(res, params, 'host')
        return res

    def get_screen(self, name=None, **params):
        params = self._param_to_filter(params, name=name)
        res = self.zabbix_api.run('screen.get', **params)
        return res

    def add_screen(self, **params):
        return self.zabbix_api.run('screen.create', **params)

    def delete_screen(self, screenids):
        params = {
            'params': screenids
        }
        return self.zabbix_api.run('screen.delete', **params)

    def get_graph(self, host=None,name=None, **params):
        params = self._param_to_filter(params, host=host)
        if 'search' not in params:
            if name is not None:
                params['search'] = {'name': name}
        res = self.zabbix_api.run('graph.get', **params)
        return res

    def add_graph(self, params):
        # params = {
        #     # "method": "graph.create",
        #     "params": {"name": graphname,
        #                "width": 900, "height": 200,
        #                "gitems": gitems
        #                }
        # }
        return self.zabbix_api.run('graph.create', **params)

    def get_applications(self, name=None, **params):
        params = self._param_to_filter(params, name=name)
        return self.zabbix_api.run('application.get', **params)

    def delete_graph(self, graphids):
        params = {
            "params": graphids
        }
        return self.zabbix_api.run('graph.delete', **params)

    def create_host(self, host, agent_ip=None, group_names=None, template_names=None, **params):
        params['host'] = host

        if 'interfaces' not in params:
            if agent_ip is None:
                raise TypeError('missing argument interfaces or agent_ip')
            params['interfaces'] = [{'type': 1, 'main': 1, 'useip': 1, 'ip': agent_ip, 'dns': '', 'port': '10050'}]

        if 'groups' not in params:
            if group_names is None:
                raise TypeError('missing argument group_names or groups')
            group_res = self.get_host_group(group_names)
            params['groups'] = [{'groupid': g['groupid']} for g in group_res]

        if 'templates' not in params and template_names is not None:
            template_res = self.get_template(name=template_names)
            params['templates'] = [{'templateid': t['templateid']} for t in template_res]

        return self.zabbix_api.run('host.create', **params)

    def delete_host(self, hostids=None, hostnames=None):
        params = dict()
        if hostids is not None:
            params['params'] = hostids
        elif hostnames is None:
            raise TypeError('missing argument hostids or hostnames')
        else:
            host_res = self.get_host(host=hostnames)
            hostids = [item['hostid'] for item in host_res]
            params['params'] = hostids
        return self.zabbix_api.run('host.delete', **params)

    def mass_update_host(self, hostids=None, hostnames=None, **params):
        if hostids is None:
            if hostnames is None:
                raise TypeError('missing argument hostids or hostnames')
            host_res = self.get_host(host=hostnames)
            hostids = [item['hostid'] for item in host_res]
        hosts = [{"hostid": item} for item in hostids]
        params['hosts'] = hosts
        return self.zabbix_api.run('host.massupdate', **params)

    def mass_add_host(self, hostids=None, hostnames=None, **params):
        if hostids is None:
            if hostnames is None:
                raise TypeError('missing argument hostids or hostnames')
            host_res = self.get_host(host=hostnames)
            hostids = [item['hostid'] for item in host_res]
        hosts = [{"hostid": item} for item in hostids]
        params['hosts'] = hosts
        return self.zabbix_api.run('host.massadd', **params)

    def mass_remove_host(self, hostids=None, hostnames=None, **params):
        if hostids is None:
            if hostnames is None:
                raise TypeError('missing argument hostids or hostnames')
            host_res = self.get_host(host=hostnames)
            hostids = [item['hostid'] for item in host_res]

        params['hostids'] = hostids
        return self.zabbix_api.run('host.massremove', **params)

    def update_host(self,
                    host=None,
                    agent_ip=None,
                    group_names=None,
                    template_names=None,
                    clear_template_names=None,
                    clear_single_item_and_lld=True,
                    keep_group=True,
                    **params):
        host_res = None
        if 'hostid' not in params:
            if host is None:
                raise TypeError('missing argument hostid or host')
            host_res = self.get_host(host=host, selectGroups='extend')[0]
            hostid = host_res['hostid']
            params['hostid'] = hostid

        if 'interfaces' not in params:
            if agent_ip is None:
                raise TypeError('missing argument interfaces or agent_ip')
            params['interfaces'] = [{'type': 1, 'main': 1, 'useip': 1, 'ip': agent_ip, 'dns': '', 'port': '10050'}]

        if 'groups' not in params:
            if group_names is None:
                raise TypeError('missing argument group_names or groups')
            group_res = self.get_host_group(group_names)
            params['groups'] = [{'groupid': g['groupid']} for g in group_res]

        if keep_group:
            update_group_id_list = [g['groupid'] for g in params['groups']]

            if host_res is None:
                host_res = self.get_host(hostid=params['hostid'], selectGroups='extend')[0]
            host_groups = host_res['groups']
            for g in host_groups:
                if g['groupid'] not in update_group_id_list:
                    params['groups'].append({'groupid': g['groupid']})

        if 'templates' not in params and template_names is not None:
            template_res = self.get_template(name=template_names)
            params['templates'] = [{'templateid': t['templateid']} for t in template_res]

        if 'templates_clear' not in params and clear_template_names is not None:
            template_res = self.get_template(name=clear_template_names)
            params['templates_clear'] = [{'templateid': t['templateid']} for t in template_res]

        if clear_single_item_and_lld:
            self.clear_single_item(hostids=params['hostid'])
            self.clear_single_lld_rule(hostids=params['hostid'])

        return self.zabbix_api.run('host.update', **params)


    def get_item(self, host=None, **params):
        params = self._param_to_filter(params, host=host)
        return self.zabbix_api.run('item.get', **params)


    def get_single_item(self, host=None, **params):
        item_res = self.get_item(host=host, **params)
        return [item for item in item_res if item['templateid'] == '0' and item['flags'] == '0']


    def clear_single_item(self, host=None, **params):
        single_item = self.get_single_item(host=host, **params)
        single_item_id = [i['itemid'] for i in single_item]
        return self.zabbix_api.run('item.delete', params=single_item_id)


    def get_lld_rule(self, host=None, **params):
        params = self._param_to_filter(params, host=host)
        return self.zabbix_api.run('discoveryrule.get', **params)


    def get_single_lld_rule(self, host=None, **params):
        lld_res = self.get_lld_rule(host=host, **params)
        return [lld for lld in lld_res if lld['templateid'] == '0']


    def clear_single_lld_rule(self, host=None, **params):
        single_lld = self.get_single_lld_rule(host=host, **params)
        single_lld_id = [i['itemid'] for i in single_lld]
        return self.zabbix_api.run('discoveryrule.delete', params=single_lld_id)


    def create_or_update_host(self,
                            host,
                            agent_ip=None,
                            group_names=None,
                            template_names=None,
                            ignore_update=True,
                            clear_all_template=False,
                            clear_single_item_and_lld=True,
                            keep_group=True,
                            **params):
        # raise Exception('test')
        try:
            host_res = self.get_host(host=host, selectParentTemplates='extend')
            if not host_res:
                return self.create_host(
                    host=host, agent_ip=agent_ip, group_names=group_names, template_names=template_names, **params)
        except ZbxNotFoundError:
            return self.create_host(
                host=host, agent_ip=agent_ip, group_names=group_names, template_names=template_names, **params)

        if ignore_update:
            return

        hostid = host_res[0]['hostid']

        if clear_all_template:
            templates_clear = [{'templateid': t['templateid']} for t in host_res[0]['parentTemplates']]
            if templates_clear:
                params['templates_clear'] = templates_clear

        if clear_single_item_and_lld:
            self.clear_single_item(hostids=hostid)
            self.clear_single_lld_rule(hostids=hostid)

        return self.update_host(
            hostid=hostid,
            agent_ip=agent_ip,
            group_names=group_names,
            template_names=template_names,
            keep_group=keep_group,
            **params)
