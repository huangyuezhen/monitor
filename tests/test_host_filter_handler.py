import unittest
from tests.util import BaseTestCase
import requests


class HostFilterOptionTestCase(BaseTestCase):
    def setUp(self):
        super(HostFilterOptionTestCase, self).setUp()
        self.url = self.url + '/api/' + 'host_filter_option'

    def tearDown(self):
        super(HostFilterOptionTestCase, self).tearDown()

    def test_get_response_format(self):
        res = requests.get(self.url)
        self.assertEqual(res.status_code, 200)
        res_json = res.json()
        self.assertIsInstance(res_json, dict)
        self.assertEqual(res_json['code'], res.status_code)
        self.assertTrue('zbx_item_application' in res_json['res'])
        self.assertIsInstance(res_json['res']['zbx_item_application'], list)
        self.assertFalse(len(res_json['res']['zbx_item_application']) < 1)
        self.assertIsInstance(res_json['res']['zbx_item_application'][0], dict)
        self.assertTrue('name' in res_json['res']['zbx_item_application'][0])
        # print(res_json)


if __name__ == '__main__':
    unittest.main()
