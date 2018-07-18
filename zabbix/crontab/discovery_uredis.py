import sys

sys.path.append('.')
sys.path.append('..')
# import io
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')

from common import cmdb
from common import zabbix_api
from common.zabbix_util import ZabbixUtil
from common.ucloud_util import UcloudUtil
from conf import settings
from zabbix.crontab.util import create_or_update_zabbix_host
from zabbix.crontab.util import logger

conf = settings['crontab']['discovery_uredis']


def get_uredis_by_cmdb(**kwargs):
    # hotst_type_id = 4 (云内存) database_type_id = 1 (redis)
    params = {'host_type_id': 4, 'page_size': 10000, 'database_type_id': 1}
    udb_list = cmdb.get('database', **params, **kwargs)

    redis_list = UcloudUtil.get_uredis_by_projectid()[1]

    # match ucloud info
    del_index = []
    for index, udb in enumerate(udb_list):
        try:
            u_info = redis_list[udb['hostname']]
        except KeyError:
            del_index.insert(0, index)
            continue
        udb.update(u_info)

    if del_index:
        for i in del_index:
            udb_list.pop(i)

    return udb_list


def add_or_update_uredis_from_cmdb():
    logger.info('discovery uredis start')

    env = conf['env']
    agent_ip = conf['agent_ip']
    group_list = conf['group_list']
    redids_template = conf['redis_templates']
    clear_all_template = conf.get('clear_all_template', False)
    clear_single_item_and_lld = conf.get('clear_single_item_and_lld', False)
    keep_group = conf.get('keep_group', True)
    ignore_update = conf.get('ignore_update', True)

    try:
        if len(sys.argv) > 1:
            redis_name = sys.argv[1]
            redis_list = get_uredis_by_cmdb(hostname=redis_name)
        else:
            redis_list = get_uredis_by_cmdb()

        assert redis_list, 'find uredis from cmdb is not found'

        logger.debug(redis_list)
        zbx_api = ZabbixUtil(zabbix_api[env])

        for uredis in redis_list:
            logger.debug(uredis)
            template_list = redids_template.copy()

            kwargs = {
                'zbx_api': zbx_api,
                'host': uredis['hostname'],
                'agent_ip': agent_ip,
                'group': group_list,
                'template': template_list,
                'project_id': uredis['ProjectId'],
                'region': uredis['Region'],
                'zone': uredis['Zone'],
                'resource_id': uredis['GroupId'],
                'ip': uredis['ip_addr'],
                'clear_all_template': clear_all_template,
                'clear_single_item_and_lld': clear_single_item_and_lld,
                'keep_group': keep_group,
                'ignore_update': ignore_update,
                'status': 0
            }
            res = create_or_update_zabbix_host(**kwargs)
            if res:
                logger.info(res)

    except Exception as e:
        logger.error(str(e))
        sys.exit(1)

    logger.info('discovery uredis done')


if __name__ == '__main__':
    add_or_update_uredis_from_cmdb()
