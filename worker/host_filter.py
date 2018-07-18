from common import cmdb
from conf import settings
from db.zabbix import ZABBIX
from db import mysql
from collections import OrderedDict
from worker.zbx_item import get_items_raw, get_history_lastdata_raw
from common.sdk.cmdb_sdk import CmdbSdkException


def get_cmdb_host_filter_options():
    """
    从cmdb获取主机筛选参数
    :return: (dict) filter option
    """
    res_options = {}
    hostname = []
    ip = []
    application = []
    department = []
    business_group = []
    page_size = 99999
    res_options['cmdb_host_status'] = settings['cmdb']['map']['host_status']
    res_options['cmdb_env'] = [{'id': i['id'], 'name': i['name']} for i in cmdb.get('env', page_size=page_size)]
    res_options['cmdb_zone_info'] = [{'id': i['id'], 'name': i['name']} for i in
                                     cmdb.get('zone_info', page_size=page_size)]
    # res_options['ip'] = list(set([i['ip_addr'] for i in cmdb.get('ip', page_size=page_size)]))
    # res_options['department'] = [[i['id'], i['name']] for i in cmdb.get('department', page_size=page_size)]
    # res_options['business_group'] = [[i['id'], i['name']] for i in cmdb.get('business_group', page_size=page_size)]
    # res_options['application'] = [[i['id'], i['name']] for i in cmdb.get('application', page_size=page_size)]

    host_res = cmdb.get('host', page_size=page_size)
    for host in host_res:
        hostname.append({'id': host['id'], 'name': host['hostname']})
        for net in host['network_interface']:
            for i in net['ip']:
                ip.append(i['ip_addr'])
        for app in host['application_list']:
            application.append(app['name'])
            department.append(app['department']['name'])
            business_group.append(app['business_group']['name'])

    res_options['cmdb_hostname'] = hostname
    res_options['cmdb_ip'] = [{'name': i} for i in list(set(ip))]
    res_options['cmdb_application'] = [{'name': i} for i in list(set(application))]
    res_options['cmdb_department'] = [{'name': i} for i in list(set(department))]
    res_options['cmdb_business_group'] = [{'name': i} for i in list(set(business_group))]
    return res_options


def host_filter_by_cmdb(**kwargs):
    """
    从cmdb筛选出主机，并格式化。
    :param kwargs: cmdb api kwargs
    :return: (ordered dict obj) host info
    """
    res = OrderedDict()
    id_env_map = {i['id']: i['name'] for i in cmdb.get('env')}
    cmdb_res = cmdb.get('host', response_obj=True, **kwargs)
    cmdb_res = cmdb_res.json()
    if cmdb_res['code'] != 200:
        raise CmdbSdkException(cmdb_res['msg'])
    total_count = cmdb_res['total_count']
    cmdb_res = cmdb_res['res']
    for host in cmdb_res:
        h = dict(
            cmdb_application=[],
            cmdb_business_group=[],
            cmdb_department=[],
            zbx_items={}
        )

        h['cmdb_hostname'] = host['hostname']
        h['cmdb_status'] = host['status']
        try:
            h['cmdb_env'] = id_env_map[host['env_id']]
        except KeyError:
            # TODO: 没有匹配的env id
            h['cmdb_env'] = ''
            # continue
        h['cmdb_ip'] = [i['ip_addr'] for net in host['network_interface'] for i in net['ip']]
        for app in host['application_list']:
            h['cmdb_application'].append(app['application']['name']) if 'name' in app['application'].keys() else  h[
                'cmdb_application'].append('')
            # h['cmdb_business_group'].append(app['business_group']['name']) if 'name' in app[
            #     'business_group'].keys() else  h['cmdb_business_group'].append('')
            h['cmdb_department'].append(app['department']['name']) if 'name' in app[
                'department'].keys() else  h['cmdb_department'].append('')

        res[h['cmdb_hostname']] = h

    return res, total_count


def database_filter_by_cmdb(**kwargs):
    """
        从cmdb筛选出 数据库，并格式化。
        :param kwargs: cmdb api kwargs
        :return: (ordered dict obj) host info
        """
    res = OrderedDict()
    # print(kwargs)
    # id_env_map = {i['id']: i['name'] for i in cmdb.get('env')}
    # _kwargs = {'hostname': "WEIYE-DB-03"}
    cmdb_res = cmdb.get('database', response_obj=True, **kwargs)
    cmdb_res = cmdb_res.json()
    # print ('cmdb_res:',cmdb_res)
    if cmdb_res['code'] != 200:
        raise CmdbSdkException(cmdb_res['msg'])
    total_count = cmdb_res['total_count']
    cmdb_res = cmdb_res['res']
    for host in cmdb_res:
        h = {'cmdb_' + k: v for k, v in host.items()}
        h['zbx_items'] = {}

        # h = dict(
        #     cmdb_application=[],
        #     cmdb_business_group=[],
        #     cmdb_department=[],
        #     zbx_items={}
        # )

        # h['cmdb_hostname'] = host['hostname']
        # h['cmdb_ip'] = host['ip_addr']
        # h['cmdb_status'] = host['status']
        # try:
        #     h['cmdb_env'] = id_env_map[host['env_id']]
        # except KeyError:
        #     # TODO: 没有匹配的env id
        #     h['cmdb_env'] = ''
        # continue
        # h['cmdb_ip'] = [i['ip_addr'] for net in host['network_interface'] for i in net['ip']]
        # for app in host['application_list']:
        #     h['cmdb_application'].append(app['application']['name']) if 'name' in app['application'].keys() else  h[
        #         'cmdb_application'].append('')
        #     h['cmdb_business_group'].append(app['business_group']['name']) if 'name' in app[
        #         'business_group'].keys() else  h['cmdb_business_group'].append('')
        #     h['cmdb_department'].append(app['department']['name']) if 'name' in app[
        #         'department'].keys() else  h['cmdb_department'].append('')

        res[h['cmdb_hostname']] = h
    # print (list(res.keys()))

    return res, total_count


def get_zbx_host_filter_options(zbx_sessions):
    """
    获取zabbix主机筛选参数
    :param zbx_sessions: (session obj) zabbix db session
    :return: (dict) filter option
    """
    res_options = {}

    for env, zbx in ZABBIX.items():
        session = zbx_sessions[env]
        applications = zbx.applications

        # item_applications
        item_app_res = session.query(applications.name).group_by(applications.name).all()
        res_options['zbx_item_application'] = [{'name': i[0]} for i in item_app_res]

    return res_options


def host_order_by_item_lastdata(zbx_session, zbx_db, zbx_engine, item_key, desc=True, item_application_name=(),
                                **cmdb_filters):
    """
    主机按监控项最新值排序
    :param zbx_session: (session obj) zabbix db session
    :param zbx_db: (zabbix obj) zabbix db
    :param zbx_engine: (engine obj) zabbix engine
    :param item_key: (str) zabbix item key
    :param desc: (bool) order by desc?
    :param item_application_name: (tuple or list) zabbix item application list
    :param cmdb_filters: cmdb api kwargs
    :return:
    """
    host_limit_offset = cmdb_filters.get('page', 1) - 1
    host_limit_count = cmdb_filters.get('page_size', 15)
    cmdb_filters['page'] = 1
    cmdb_filters['page_size'] = 999999

    cmdb_hosts = cmdb.get('host', only_host=1, **cmdb_filters)
    if len(cmdb_hosts) < 1:
        return []
    cmdb_hosts = [h['hostname'] for h in cmdb_hosts]
    items, count = get_items_raw(
        zbx_session=zbx_session,
        zbx_db=zbx_db,
        host_list=cmdb_hosts,
        item_app_names=item_application_name,
        item_keys=[item_key],
        limit_offset=0,
        limit_count=999999
    )
    if count < 1:
        return []
    value_type = items[0].zbx_item_value_type

    lower_hostname_map = {h.lower(): h for h in cmdb_hosts}
    itemid_hostname = {item.zbx_item_id: lower_hostname_map[item.zbx_hostname.lower()] for item in items}
    lastdata = get_history_lastdata_raw(
        zbx_db=zbx_db,
        zbx_engine=zbx_engine,
        itemids=itemid_hostname.keys(),
        value_type=value_type
    )

    sorted_itemids = sorted(lastdata, key=lambda l: l.value, reverse=desc)[host_limit_offset:host_limit_count]
    return [itemid_hostname[i.itemid] for i in sorted_itemids]


def cmdb_host_filter_order_by_item(zbx_session, zbx_db, zbx_engine, order_by_item_key, order_by_item_desc=True,
                                   item_application_name=(), **cmdb_filters):
    sorted_hostname = host_order_by_item_lastdata(
        zbx_session=zbx_session,
        zbx_db=zbx_db,
        zbx_engine=zbx_engine,
        item_key=order_by_item_key,
        desc=order_by_item_desc,
        item_application_name=item_application_name,
        **cmdb_filters
    )
    cmdb_filters.pop('hostname')
    cmdb_host_info, total_count = host_filter_by_cmdb(hostname=sorted_hostname, **cmdb_filters)
    sorted_hostname.reverse()
    for h in sorted_hostname:
        cmdb_host_info.move_to_end(h, last=False)
    return cmdb_host_info, total_count


def filter_cmdb_host(self, cmdb_filters):
    host_args_key = ('cmdb_host_status', 'cmdb_zone_name', 'cmdb_ip_name', 'cmdb_ip', 'cmdb_hostname',
                     'cmdb_application_name', 'cmdb_department_name', 'cmdb_business_group_name', 'cmdb_like')

    # host cmdb api kwargs
    cmdb_filters.update(self.get_args_dict(*host_args_key, prefix='cmdb_'))
    cmdb_filters['page'] = int(self.get_argument("page", 1))
    cmdb_filters['page_size'] = int(self.get_argument("page_size", 20))

    cmdb_host_info, total_host = host_filter_by_cmdb(**cmdb_filters)
    return cmdb_host_info


def filter_cmdb_database(self, cmdb_filters):
    host_args_key = ('cmdb_ip_addr', 'cmdb_hostname', 'cmdb_host_type_id', 'cmdb_database_type_id', 'cmdb_like',
                     'cmdb_ip_name')

    # cmdb api kwargs
    cmdb_filters.update(self.get_args_dict(*host_args_key, prefix='cmdb_'))
    cmdb_filters['page'] = int(self.get_argument("page", 1))
    cmdb_filters['page_size'] = int(self.get_argument("page_size", 20))

    cmdb_host_info, total_host = database_filter_by_cmdb(**cmdb_filters)

    res = dict()
    for key in cmdb_host_info:
        obj = cmdb_host_info[key]
        cmdb_ip = [item['ip_addr'] for item in obj['cmdb_ip']]
        cmdb_hostname = obj['cmdb_hostname']
        cmdb_database_name = [item['name'] for item in obj['cmdb_database_name_list']]
        _dict = {
            'cmdb_ip': cmdb_ip,
            'cmdb_database_name': cmdb_database_name,
            'cmdb_hostname': cmdb_hostname
        }
        res.update({cmdb_hostname: _dict})

    # host = list(cmdb_host_info.keys())
    # return cmdb_host_info
    return res


def host_db_filter_by_cmdb(self, filter_type):
    cmdb_filters = dict()
    cmdb_host_info = dict()
    if filter_type == 1:
        cmdb_host_info = filter_cmdb_host(self, cmdb_filters)
        if not cmdb_host_info:
            return self.render_json_response(code=200, msg='OK', res=[])
    elif filter_type == 2:
        cmdb_host_info = filter_cmdb_database(self, cmdb_filters)
        if not cmdb_host_info:
            return self.render_json_response(code=200, msg='OK', res=[])
    host = list(cmdb_host_info.keys()) if cmdb_host_info else None

    return host


def test():
    import json
    import time

    sessions = mysql.connect_all()
    sessions = {n: s() for n, s in sessions.items()}

    a = time.time()
    # print(a)
    print(json.dumps(get_zbx_host_filter_options(sessions), ensure_ascii=False))
    b = time.time()
    print(b - a)
    print(json.dumps(get_cmdb_host_filter_options(), ensure_ascii=False))
    c = time.time()
    print(c - b)


if __name__ == '__main__':
    test()
