import sys
sys.path.append('.')
sys.path.append('..')
import unittest
from tests.util import BaseTestCase
from common import zabbix_api
from common.zabbix_util import ZabbixUtil, ZbxNotFoundError
from common.sdk.zbx_sdk import ZbxSdkException
import json


class ZabbixTestCase(BaseTestCase):
    def setUp(self):
        super(ZabbixTestCase, self).setUp()
        self.api = zabbix_api['local']
        self.zbx_util = ZabbixUtil(self.api)

    def test_api_available(self):
        res = self.api.run('apiinfo.version')
        self.assertTrue(res.startswith('3'), res)

    def test_get_host_group(self):
        name = ['Templates', 'Discovered hosts']
        res = self.zbx_util.get_host_group(name=name)
        self.assertIsInstance(res, list, res)
        for g in res:
            self.assertTrue(g['name'] in name, g['name'])

    def test_get_not_found_host_group(self):
        name = ['aaa']
        with self.assertRaises(ZbxSdkException):
            self.zbx_util.get_host_group(name=name)

    def test_get_template(self):
        name = ['Template SNMP OS Linux', 'Template SNMP OS Windows']
        res = self.zbx_util.get_template(name=name)
        self.assertIsInstance(res, list, res)
        for t in res:
            self.assertTrue(t['name'] in name, t['name'])

    def test_get_not_found_template(self):
        name = ['aaa']
        with self.assertRaises(ZbxSdkException):
            self.zbx_util.get_template(name=name)

    def test_get_host_by_name(self):
        host = ['udb_test']
        res = self.zbx_util.get_host(host=host)

        self.assertIsInstance(res, list, res)
        for h in res:
            self.assertTrue(h['host'] in host, h['host'])

    def test_get_not_found_host(self):
        host = ['aaa']

        with self.assertRaises(ZbxNotFoundError):
            self.zbx_util.get_host(host=host)

    def test_get_host_by_ip(self):
        ip = '127.0.0.1'
        res = self.zbx_util.get_host(ip='127.0.0.1', selectInterfaces='extend')

        self.assertIsInstance(res, list, res)
        for h in res:
            ip_list = [i['ip'] for i in h['interfaces']]
            self.assertTrue(ip in ip_list, ip_list)

    @unittest.skip
    def test_create_host(self):
        host = 'test_hostname'
        agent_ip = '127.0.0.1'
        group_names = 'Discovered hosts'
        template_names = 'Template_Test'
        macros = [{'macro': '{$RESOURCE_ID}', 'value': 'I am resource id'}]

        res = self.zbx_util.create_host(
            host=host, agent_ip=agent_ip, group_names=group_names, template_names=template_names, macros=macros)
        self.assertIsInstance(res, dict, res)
        self.assertTrue('hostids' in res, res)

        hostid = res['hostids'][0]

        res = self.zbx_util.get_host(
            filter={'hostid': hostid},
            output='extend',
            selectGroups='extend',
            selectInterfaces='extend',
            selectParentTemplates='extend',
            selectMacros='extend')

        self.assertEqual(res[0]['hostid'], hostid, res)
        self.assertEqual(res[0]['host'], host, res)
        self.assertEqual(res[0]['interfaces'][0]['ip'], agent_ip, res)
        self.assertEqual(res[0]['groups'][0]['name'], group_names, res)
        self.assertEqual(res[0]['parentTemplates'][0]['name'], template_names, res)
        self.assertEqual(res[0]['macros'][0]['macro'], macros[0]['macro'], res)
        self.assertEqual(res[0]['macros'][0]['value'], macros[0]['value'], res)

    def test_update_host_by_hostname(self):
        host = 'test_hostname'
        agent_ip = '127.0.0.2'
        group_names = 'DB'
        template_names = 'dev_template'
        clear_template_names = ['dev_template', 'Template_Test']
        macros = [{'macro': '{$RESOURCE_ID}', 'value': 'I am new resource id'}]

        res = self.zbx_util.update_host(
            host=host,
            agent_ip=agent_ip,
            group_names=group_names,
            template_names=template_names,
            clear_template_names=clear_template_names,
            macros=macros)
        self.assertIsInstance(res, dict, res)
        self.assertTrue('hostids' in res, res)

        hostid = res['hostids'][0]

        res = self.zbx_util.get_host(
            filter={'hostid': hostid},
            output='extend',
            selectGroups='extend',
            selectInterfaces='extend',
            selectParentTemplates='extend',
            selectMacros='extend')

        self.assertEqual(res[0]['hostid'], hostid, res)
        self.assertEqual(res[0]['host'], host, res)
        self.assertEqual(res[0]['interfaces'][0]['ip'], agent_ip, res)
        self.assertEqual(res[0]['groups'][0]['name'], group_names, res)
        self.assertEqual(res[0]['parentTemplates'][0]['name'], template_names, res)
        self.assertEqual(res[0]['macros'][0]['macro'], macros[0]['macro'], res)
        self.assertEqual(res[0]['macros'][0]['value'], macros[0]['value'], res)

    def test_update_host_by_hostid(self):
        host = 'test_hostname'
        agent_ip = '127.0.0.2'
        group_names = 'DB'
        template_names = 'Template_Test'
        clear_template_names = ['dev_template', 'Template_Test']
        macros = [{'macro': '{$RESOURCE_ID}', 'value': 'I am new resource id'}]

        hostid = self.zbx_util.get_host(host=host)[0]['hostid']

        res = self.zbx_util.update_host(
            hostid=hostid,
            agent_ip=agent_ip,
            group_names=group_names,
            template_names=template_names,
            clear_template_names=clear_template_names,
            macros=macros)
        self.assertIsInstance(res, dict, res)
        self.assertTrue('hostids' in res, res)

        hostid = res['hostids'][0]

        res = self.zbx_util.get_host(
            filter={'hostid': hostid},
            output='extend',
            selectGroups='extend',
            selectInterfaces='extend',
            selectParentTemplates='extend',
            selectMacros='extend')

        self.assertEqual(res[0]['hostid'], hostid, res)
        self.assertEqual(res[0]['host'], host, res)
        self.assertEqual(res[0]['interfaces'][0]['ip'], agent_ip, res)
        self.assertEqual(res[0]['groups'][0]['name'], group_names, res)
        self.assertEqual(res[0]['parentTemplates'][0]['name'], template_names, res)
        self.assertEqual(res[0]['macros'][0]['macro'], macros[0]['macro'], res)
        self.assertEqual(res[0]['macros'][0]['value'], macros[0]['value'], res)

    def test_update_host_keep_group(self):
        keep_group_name = 'DB'
        host = 'test_hostname'
        agent_ip = '127.0.0.2'
        group_names = 'ELK'
        template_names = 'Template_Test'
        clear_template_names = ['dev_template', 'Template_Test']
        macros = [{'macro': '{$RESOURCE_ID}', 'value': 'I am new resource id'}]

        hostid = self.zbx_util.get_host(host=host)[0]['hostid']

        res = self.zbx_util.update_host(
            hostid=hostid,
            agent_ip=agent_ip,
            group_names=group_names,
            template_names=template_names,
            clear_template_names=clear_template_names,
            keep_group=True,
            macros=macros)
        self.assertIsInstance(res, dict, res)
        self.assertTrue('hostids' in res, res)

        hostid = res['hostids'][0]

        res = self.zbx_util.get_host(
            filter={'hostid': hostid},
            output='extend',
            selectGroups='extend',
            selectInterfaces='extend',
            selectParentTemplates='extend',
            selectMacros='extend')

        self.assertEqual(res[0]['hostid'], hostid, res)
        self.assertEqual(res[0]['host'], host, res)
        self.assertEqual(res[0]['interfaces'][0]['ip'], agent_ip, res)
        res_group_names = [g['name'] for g in res[0]['groups']]
        # print(res_group_names)
        self.assertTrue(keep_group_name in res_group_names, res_group_names)
        self.assertTrue(group_names in res_group_names, res_group_names)
        self.assertEqual(res[0]['parentTemplates'][0]['name'], template_names, res)
        self.assertEqual(res[0]['macros'][0]['macro'], macros[0]['macro'], res)
        self.assertEqual(res[0]['macros'][0]['value'], macros[0]['value'], res)

    def test_get_item_by_hostid(self):
        host = 'test_hostname'
        hostid = self.zbx_util.get_host(host=host)[0]['hostid']

        item_res = self.zbx_util.get_item(hostids=hostid)
        self.assertTrue(item_res)
        for i in item_res:
            self.assertEqual(i['hostid'], hostid, i)

    def test_get_item_by_host(self):
        host = 'test_hostname'

        item_res = self.zbx_util.get_item(host=host)
        self.assertTrue(item_res)
        hostid = self.zbx_util.get_host(host=host)[0]['hostid']
        for i in item_res:
            self.assertEqual(i['hostid'], hostid, i)

    # def test_get_single_item(self):
    #     host = 'test_hostname'
    #     item_res = self.zbx_util.get_item(host=host)
    #     # self.assertTrue(item_res)
    #     # print(json.dumps(item_res))

    def test_get_lld_rule_by_host(self):
        host = 'test_hostname'

        lld_res = self.zbx_util.get_lld_rule(host=host)
        # self.assertTrue(lld_res)
        hostid = self.zbx_util.get_host(host=host)[0]['hostid']
        for i in lld_res:
            self.assertEqual(i['hostid'], hostid, i)

    def test_create_or_update_host(self):
        host = 'test_hostname'
        agent_ip = '127.1.1.1'
        group_names = 'DB'
        template_names = 'Template_Test'
        macros = [{'macro': '{$RESOURCE_ID}', 'value': 'I am new new resource id'}]

        res = self.zbx_util.create_or_update_host(
            host=host,
            agent_ip=agent_ip,
            group_names=group_names,
            template_names=template_names,
            macros=macros,
            ignore_update=False,
            clear_all_template=True,
            clear_single_item_and_lld=True)

        self.assertIsInstance(res, dict, res)
        self.assertTrue('hostids' in res, res)

        hostid = res['hostids'][0]

        res = self.zbx_util.get_host(
            filter={'hostid': hostid},
            output='extend',
            selectGroups='extend',
            selectInterfaces='extend',
            selectParentTemplates='extend',
            selectMacros='extend')

        self.assertEqual(res[0]['hostid'], hostid, res)
        self.assertEqual(res[0]['host'], host, res)
        self.assertEqual(res[0]['interfaces'][0]['ip'], agent_ip, res)
        self.assertEqual(res[0]['groups'][0]['name'], group_names, res)
        self.assertEqual(res[0]['parentTemplates'][0]['name'], template_names, res)
        self.assertEqual(res[0]['macros'][0]['macro'], macros[0]['macro'], res)
        self.assertEqual(res[0]['macros'][0]['value'], macros[0]['value'], res)


if __name__ == '__main__':
    unittest.main()
