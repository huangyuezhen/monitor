import unittest
from tests.util import BaseTestCase
import requests
import json
import time


class ZbxItemTestCase(BaseTestCase):
    def setUp(self):
        super(ZbxItemTestCase, self).setUp()
        self.url = self.url + '/api/' + 'zbx_item'

    def tearDown(self):
        super(ZbxItemTestCase, self).tearDown()

    def test_get_response_format(self):
        params = {
            'hosts': 'zabbix-server,test_hostname',
        }
        response = requests.get(url=self.url, params=params)
        self.assertEqual(response.status_code, 200, response.status_code)
        res = response.json()
        # print(json.dumps(res))
        self.assertEqual(res['code'], 200, res)

        res = res['res']
        self.assertTrue('total_host' in res, res)
        self.assertEqual(res['total_host'], 2, res)

        hosts = res['hosts']
        for host in hosts:
            self.assertTrue('zbx_items' in host, host)

    def test_get_last_value_format(self):
        params = {
            'hosts': 'zabbix-server',
            'last_value': 1
        }
        response = requests.get(self.url, params=params)
        res_json = response.json()
        res = res_json['res']
        hosts = res['hosts']
        for host in hosts:
            items = host['zbx_items']
            for item_key, item_info in items.items():
                item_ks = item_info.keys()
                self.assertTrue("zbx_last_value" in item_ks)
                self.assertTrue("zbx_last_clock" in item_ks)

    def test_get_trigger_format(self):
        params = {
            'hosts': 'zabbix-server',
            'problem_trigger': 1
        }
        response = requests.get(self.url, params=params)
        res_json = response.json()
        res = res_json['res']
        hosts = res['hosts']
        for host in hosts:
            items = host['zbx_items']
            for item_key, item_info in items.items():
                item_ks = item_info.keys()
                self.assertTrue("zbx_triggers" in item_ks)
                triggers = item_info['zbx_triggers']
                self.assertIsInstance(triggers, list)
                for trigger in triggers:
                    self.assertTrue("zbx_trigger_id" in trigger)
                    self.assertTrue("zbx_trigger_description" in trigger)
                    self.assertTrue("zbx_trigger_priority" in trigger)

    def test_get_time_range_value_format(self):
        params = {
            'hosts': 'zabbix-server',
            'time_range_value': 1,
            'start_clock': int(time.time() - 10000),
            'end_clock': int(time.time()),
        }
        response = requests.get(self.url, params=params)
        res_json = response.json()
        res = res_json['res']
        # print(res)
        hosts = res['hosts']
        for host in hosts:
            items = host['zbx_items']
            for item_key, item_info in items.items():
                item_ks = item_info.keys()
                self.assertTrue("zbx_min_value" in item_ks)
                self.assertTrue("zbx_avg_value" in item_ks)
                self.assertTrue("zbx_max_value" in item_ks)

    def test_get_item_by_item_keys(self):
        params = {
            'hosts': 'zabbix-server,test_hostname',
            "zbx_item_keys": ['checkstatus[frontend-pos.yunnex.nginx,10.13.165.141,0]', 'system.hostname'],
        }
        response = requests.get(self.url, params=params)
        res_json = response.json()
        print(json.dumps(res_json))
        res = res_json['res']
        for host in res['hosts']:
            items = host['zbx_items']
            for item_key, item_info in items.items():
                self.assertTrue(item_key in params['zbx_item_keys'])

    def test_get_item_by_item_group(self):
        params = {
            'hosts': 'zabbix-server,test_hostname',
            "item_group": [
                "default"
            ]
        }
        item_keys = []
        item_group_map = self.settings['zabbix_item_group_map']
        for item_group in params['item_group']:
            item_keys.extend(item_group_map[item_group])

        response = requests.get(self.url, params=params)
        res_json = response.json()
        res = res_json['res']
        for host in res['hosts']:
            items = host['zbx_items']
            for item_key, item_info in items.items():
                self.assertTrue(item_key in item_keys)


class ItemKeyTestCase(BaseTestCase):
    def setUp(self):
        super(ItemKeyTestCase, self).setUp()
        self.url = self.url + '/api/' + 'item_key'

    def tearDown(self):
        super(ItemKeyTestCase, self).tearDown()

    def test_get_format(self):
        response = requests.get(self.url)
        self.assertEqual(response.status_code, 200, response)
        res_json = response.json()
        self.assertEqual(res_json['code'], 200, res_json)
        res = res_json['res']
        self.assertIsInstance(res, list, res)
        # print(res)
        for item_info in res:
            self.assertIsInstance(item_info, dict, item_info)
            self.assertTrue('name' in item_info, item_info)
            self.assertTrue('key' in item_info, item_info)

    def test_get_like(self):
        params = {
            'like': 'activemq'
        }
        response = requests.get(self.url, params)
        res_json = response.json()
        res = res_json['res']

        # print(res)
        for item_info in res:
            self.assertTrue(params['like'].lower() in item_info['name'].lower() or
                            params['like'].lower() in item_info['key'].lower(), item_info)


if __name__ == '__main__':
    unittest.main()
