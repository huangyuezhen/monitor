import unittest
from tests.util import BaseTestCase
import requests
import json
import time


class ZbxHostItemTestCase(BaseTestCase):
    def setUp(self):
        super(ZbxHostItemTestCase, self).setUp()
        self.url = self.url + '/api/' + 'zbx_host_item'

    def tearDown(self):
        super(ZbxHostItemTestCase, self).tearDown()

    def test_get_response_format(self):
        response = requests.get(self.url)
        self.assertEqual(response.status_code, 200)
        res_json = response.json()
        # print(json.dumps(res_json, indent=4, ensure_ascii=False))
        # print(json.dumps(res_json))

        self.assertIsInstance(res_json, dict)
        self.assertEqual(res_json['code'], response.status_code)

        res = res_json['res']
        self.assertTrue('hosts' in res)
        self.assertTrue('total_host' in res)

        total_host = res['total_host']
        self.assertIsInstance(total_host, int)

        hosts = res['hosts']
        self.assertIsInstance(hosts, list)
        self.assertFalse(len(hosts) < 1)

        host = hosts[0]
        self.assertTrue('cmdb_application' in host)
        self.assertIsInstance(host['cmdb_application'], list)
        self.assertTrue('cmdb_business_group' in host)
        self.assertIsInstance(host['cmdb_business_group'], list)
        self.assertTrue('cmdb_department' in host)
        self.assertIsInstance(host['cmdb_department'], list)
        self.assertTrue('cmdb_hostname' in host)
        self.assertIsInstance(host['cmdb_hostname'], str)
        self.assertTrue('cmdb_status' in host)
        self.assertIsInstance(host['cmdb_status'], int)
        self.assertTrue('cmdb_env' in host)
        self.assertIsInstance(host['cmdb_env'], str)
        self.assertTrue('cmdb_ip' in host)
        self.assertIsInstance(host['cmdb_ip'], list)
        self.assertTrue('zbx_items' in host)

        items = host['zbx_items']
        self.assertIsInstance(items, dict)
        for item_key, item_info in items.items():
            self.assertIsInstance(item_info, dict)
            item_ks = item_info.keys()
            self.assertTrue("zbx_item_id" in item_ks)
            self.assertTrue("zbx_item_name" in item_ks)
            self.assertTrue("zbx_item_state" in item_ks)
            self.assertTrue("zbx_item_error" in item_ks)
            self.assertTrue("zbx_item_units" in item_ks)
            self.assertTrue("zbx_item_multiplier" in item_ks)
            self.assertTrue("zbx_item_formula" in item_ks)
            self.assertTrue("zbx_item_value_type" in item_ks)
            self.assertTrue("zbx_hostname" in item_ks)
            self.assertTrue("zbx_host_status" in item_ks)
            self.assertTrue("zbx_application_name" in item_ks)

    def test_get_last_value_format(self):
        params = {
            'last_value': 1
        }
        response = requests.get(self.url, params=params)
        res_json = response.json()
        res = res_json['res']
        hosts = res['hosts']
        host = hosts[0]
        items = host['zbx_items']
        for item_key, item_info in items.items():
            item_ks = item_info.keys()
            self.assertTrue("zbx_last_value" in item_ks)
            self.assertTrue("zbx_last_clock" in item_ks)

    def test_get_trigger_format(self):
        params = {
            'problem_trigger': 1
        }
        response = requests.get(self.url, params=params)
        res_json = response.json()
        res = res_json['res']
        hosts = res['hosts']
        host = hosts[0]
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
            'time_range_value': 1,
            'start_clock': int(time.time() - 10000),
            'end_clock': int(time.time()),
        }
        response = requests.get(self.url, params=params)
        res_json = response.json()
        res = res_json['res']
        # print(res)
        hosts = res['hosts']
        host = hosts[0]
        items = host['zbx_items']
        for item_key, item_info in items.items():
            item_ks = item_info.keys()
            self.assertTrue("zbx_min_value" in item_ks)
            self.assertTrue("zbx_avg_value" in item_ks)
            self.assertTrue("zbx_max_value" in item_ks)

    def test_get_item_by_item_keys(self):
        params = {
            "zbx_item_keys": [
                "agent.ping",
                "system.hostname",
            ]
        }
        response = requests.get(self.url, params=params)
        res_json = response.json()
        res = res_json['res']
        for host in res['hosts']:
            items = host['zbx_items']
            for item_key, item_info in items.items():
                self.assertTrue(item_key in params['zbx_item_keys'])

    def test_get_item_by_item_group(self):
        params = {
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

    def test_get_item_by_hostname(self):
        params = {
            "cmdb_hostname": 'Zabbix-Master-01'
        }
        response = requests.get(self.url, params=params)
        res_json = response.json()
        res = res_json['res']
        for host in res['hosts']:
            self.assertEqual(host['cmdb_hostname'], params['cmdb_hostname'])

    def test_get_item_host_not_found(self):
        params = {
            "cmdb_hostname": "aaaaaaaaa"
        }
        response = requests.get(self.url, params=params)
        res_json = response.json()
        self.assertEqual(res_json['code'], 200)
        res = res_json['res']
        self.assertEqual(res['total_host'], 0)
        self.assertEqual(res['hosts'], [])

    def test_get_item_total_count(self):
        response = requests.get(self.url)
        res_json = response.json()
        res = res_json['res']
        self.assertGreater(res['total_host'], 300)


if __name__ == '__main__':
    unittest.main()
