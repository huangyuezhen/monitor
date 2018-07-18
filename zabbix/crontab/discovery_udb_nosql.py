import sys

sys.path.append('.')
sys.path.append('..')
# import io
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')

import json
from common import cmdb
from common import zabbix_api
from common.zabbix_util import ZabbixUtil
from common.ucloud_util import UcloudUtil
from conf import settings
from zabbix.crontab.util import logger
from zabbix.crontab.util import create_or_update_zabbix_host

conf = settings['crontab']['discovery_udb_nosql']


def get_mongodb_by_cmdb(**kwargs):
    # 获取mongo
    # hotst_type_id = 3 (云数据库) database_type_id = 3 (mongodb)
    params = {'host_type_id': 3, 'page_size': 10000, 'database_type_id': 3}
    nosql_cmdb_list = cmdb.get('database', **params, **kwargs)

    nosql_ucloud_list = UcloudUtil.get_udb_nosql_by_projectid()[1]

    # match ucloud info
    del_index = []
    for index, udb in enumerate(nosql_cmdb_list):
        try:
            u_info = nosql_ucloud_list[udb['hostname']]
        except KeyError:
            del_index.insert(0, index)
            continue
        udb.update(u_info)

    if del_index:
        for i in del_index:
            nosql_cmdb_list.pop(i)

    return nosql_cmdb_list


def add_or_update_mongodb_from_cmdb():
    logger.info('discovery udb nosql start')

    env = conf['env']
    agent_ip = conf['agent_ip']
    group_list = conf['group_list']

    umongodb_templates_slave = conf['umongodb_templates_slave']
    umongodb_templates_master = conf['umongodb_templates_master']
    clear_all_template = conf.get('clear_all_template', False)
    clear_single_item_and_lld = conf.get('clear_single_item_and_lld', True)

    keep_group = conf.get('keep_group', True)
    ignore_update = conf.get('ignore_update', True)

    try:
        if len(sys.argv) > 1:
            udb_nosql_name = sys.argv[1]
            nosql_list = get_mongodb_by_cmdb(hostname=udb_nosql_name)
        else:
            nosql_list = get_mongodb_by_cmdb()

        assert nosql_list, 'find nosql udb from cmdb not found'

        zbx_api = ZabbixUtil(zabbix_api[env])

        for nosql in nosql_list:
            if nosql['is_main'] == 2:
                # slave
                template_list = umongodb_templates_slave.copy()
            else:
                # master
                template_list = umongodb_templates_master.copy()

            kwargs = {
                'zbx_api': zbx_api,
                'host': nosql['hostname'],
                'agent_ip': agent_ip,
                'group': group_list,
                'template': template_list,
                'project_id': nosql['ProjectId'],
                'region': nosql['Region'],
                'zone': nosql['Zone'],
                'resource_id': nosql['ResourceId'],
                'ip': nosql['ip_addr'],
                'clear_all_template': clear_all_template,
                'clear_single_item_and_lld': clear_single_item_and_lld,
                'keep_group': keep_group,
                'ignore_update': ignore_update,
                'status': 0
            }
            res = create_or_update_zabbix_host(**kwargs)
            if res:
                logger.info('zabbix api return :{}'.format(res))

    except Exception as e:
        logger.error(str(e))
        sys.exit(1)

    logger.info('discovery  nosql udb done')


if __name__ == '__main__':
    add_or_update_mongodb_from_cmdb()
