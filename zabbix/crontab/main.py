#  从cmdb（ucloud） 自动发现 udb /uredis ，
#  往zabbix  新增或更新 host(含udb /uredis等）
#  mian 是入口函数
#  通过设置ingore_update 参数来
#  决定是否需要更新 zabbix host

import sys
sys.path.append('.')
sys.path.append('..')

from zabbix.crontab.discovery_udb import add_or_update_udb_from_cmdb
from zabbix.crontab.discovery_uredis import add_or_update_uredis_from_cmdb
from zabbix.crontab.discovery_udb_nosql import add_or_update_mongodb_from_cmdb
from zabbix.crontab.discovery_ulb import add_or_update_ulb_from_cmdb

if __name__ == '__main__':
    add_or_update_udb_from_cmdb()
    add_or_update_uredis_from_cmdb()
    add_or_update_mongodb_from_cmdb()
    add_or_update_ulb_from_cmdb()
