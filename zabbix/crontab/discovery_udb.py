import sys

sys.path.append('.')
sys.path.append('..')
# import io
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')

from common import cmdb
from common import zabbix_api
from common import ucloud
from common.ucloud_util import UcloudUtil
from common.zabbix_util import ZabbixUtil
from conf import settings
from zabbix.crontab.util import create_or_update_zabbix_host
from  zabbix.crontab.util import logger


conf = settings['crontab']['discovery_udb']


def _get_all_udb_by_ucloud():
    res = []

    # TODO: 暂时只获取cn-gd
    region = 'cn-gd'
    # TODO: 暂时只获取mysql
    params = {'Action': 'DescribeUDBInstance', 'Region': region, 'Offset': 0, 'Limit': 10000, 'ClassType': 'SQL'}
    project_list = UcloudUtil.get_project_list()
    for pj in project_list:
        params['ProjectId'] = pj['ProjectId']
        proj = params.copy()
        response = ucloud.get(**params)
        proj['DataSet'] = response['DataSet']
        res.append(proj)
    return res


def _get_udb_map():
    res = {}
    ucloud_udb_res = _get_all_udb_by_ucloud()
    for project in ucloud_udb_res:
        for udb in project['DataSet']:
            res[udb['Name']] = {
                'DBId': udb['DBId'],
                'ProjectId': project['ProjectId'],
                'Region': project['Region'],
                'Zone': udb['Zone']
            }
            for u in udb['DataSet']:
                res[u['Name']] = {
                    'DBId': u['DBId'],
                    'ProjectId': project['ProjectId'],
                    'Region': project['Region'],
                    'Zone': u['Zone']
                }
    return res


def get_all_udb_by_cmdb():
    return get_udb_by_cmdb()


def get_udb_by_cmdb(**kwargs):
    # TODO: 暂时只获取mysql
    # hotst_type_id = 3 (云数据库) database_type_id = 2 (mysql)
    params = {'host_type_id': 3, 'page_size': 10000, 'database_type_id': 2}
    udb_list = cmdb.get('database', **params, **kwargs)

    # match ucloud info
    udb_map = _get_udb_map()
    del_index = []
    for index, udb in enumerate(udb_list):
        try:
            u_info = udb_map[udb['hostname']]
        except KeyError:
            del_index.insert(0, index)
            continue
        udb.update(u_info)

    if del_index:
        for i in del_index:
            udb_list.pop(i)

    return udb_list


def add_or_update_udb_from_cmdb():
    logger.info('discovery udb start')

    env = conf['env']
    agent_ip = conf['agent_ip']
    group_list = conf['group_list']
    mysql_udb_master_temp = conf['mysql_udb_master_templates']
    mysql_udb_slave_temp = conf['mysql_udb_slave_templates']
    clear_all_template = conf.get('clear_all_template', False)
    clear_single_item_and_lld = conf.get('clear_single_item_and_lld', True)
    keep_group = conf.get('keep_group', True)
    ignore_update = conf.get('ignore_update', True)

    try:
        if len(sys.argv) > 1:
            udb_name = sys.argv[1]
            udb_list = get_udb_by_cmdb(hostname=udb_name)
        else:
            udb_list = get_all_udb_by_cmdb()

        # print(json.dumps(udb_list))
        assert udb_list, 'find udb from cmdb is not found'
        logger.debug(udb_list)

        zbx_api = ZabbixUtil(zabbix_api[env])

        for udb in udb_list:
            logger.debug(udb)
            if udb['is_main'] == 2:
                # slave
                template_list = mysql_udb_slave_temp.copy()
            else:
                # master
                template_list = mysql_udb_master_temp.copy()

            kwargs = {
                'zbx_api': zbx_api,
                'host': udb['hostname'],
                'agent_ip': agent_ip,
                'group': group_list,
                'template': template_list,
                'project_id': udb['ProjectId'],
                'region': udb['Region'],
                'zone': udb['Zone'],
                'resource_id': udb['DBId'],
                'ip': udb['ip_addr'],
                'description': udb['note'],
                'clear_all_template': clear_all_template,
                'clear_single_item_and_lld': clear_single_item_and_lld,
                'keep_group': keep_group,
                'ignore_update': ignore_update,
                'status': 0
            }
            res = create_or_update_zabbix_host(**kwargs)
            if res:
                logger.info(res)
            # break

    except Exception as e:
        logger.error(str(e))
        sys.exit(1)

    logger.info('discovery udb done')


if __name__ == '__main__':
    add_or_update_udb_from_cmdb()
