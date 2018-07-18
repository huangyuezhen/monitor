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


conf = settings['crontab']['discovery_ulb']


def get_ulb_by_cmdb(name=None):
    res = cmdb.get('ucloud/allulb', refresh=1)
    if name is not None:
        res = [u for u in res if u['Name'] == name]
    return res


def add_or_update_ulb_from_cmdb():
    logger.info('discovery ulb start')

    env = conf['env']
    agent_ip = conf['agent_ip']
    group_list = conf['group_list']
    ulb_templates = conf['ulb_templates']
    clear_all_template = conf.get('clear_all_template', False)
    clear_single_item_and_lld = conf.get('clear_single_item_and_lld', True)
    keep_group = conf.get('keep_group', True)
    ignore_update = conf.get('ignore_update', True)

    # Todo: 暂时只获取一个地区
    region = 'cn-gd'
    zone = 'cn-gd-02'

    try:
        if len(sys.argv) > 1:
            ulb_name = sys.argv[1]
            ulb_list = get_ulb_by_cmdb(name=ulb_name)
        else:
            ulb_list = get_ulb_by_cmdb()

        # print(json.dumps(ulb_list))
        assert ulb_list, 'find ulb from cmdb is not found'
        logger.debug(ulb_list)

        zbx_api = ZabbixUtil(zabbix_api[env])

        for ulb in ulb_list:
            # 过滤没有EIP的
            if not ulb['IPSet']:
                continue
            logger.debug(ulb)

            kwargs = {
                'zbx_api': zbx_api,
                'host': ulb['Name'],
                'agent_ip': agent_ip,
                'group': group_list,
                'template': ulb_templates,
                'project_id': ulb['project']['ProjectId'],
                'region': region,
                'zone': zone,
                'resource_id': ulb['ULBId'],
                'ip': ','.join([i['EIP'] for i in ulb['IPSet']]),
                'description': ulb['Tag'],
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

    logger.info('discovery ulb done')


if __name__ == '__main__':
    add_or_update_ulb_from_cmdb()
