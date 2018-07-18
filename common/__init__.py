from conf import settings
from common.sdk.cmdb_sdk import CmdbSdk
from common.sdk.zbx_sdk import ZbxSdk
from common.sdk import ucloud_sdk

# cmdb api
cmdb = CmdbSdk(host=settings['cmdb']['url'], token=settings['cmdb']['token'])

# zabbix api dict
zabbix_api = {}
for name, conf in settings['zabbix_api'].items():
    zabbix_api[name] = ZbxSdk(host=conf['host'], user=conf['user'], passwd=conf['password'])

# ucloud api
ucloud = ucloud_sdk.UcloudApiClient(settings['ucloud']['url'], settings['ucloud']['public_key'],
                                    settings['ucloud']['private_key'])
