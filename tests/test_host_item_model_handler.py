import sys
sys.path.append('.')
import unittest
import requests
from tests.util import BaseTestCase


class HostItemModelTestCase(BaseTestCase):
    def setUp(self):
        super(HostItemModelTestCase, self).setUp()
        self.url = self.url + '/api/' + 'host_item_model'

    def test_get_format(self):
        model_keys = (
            ('cmdb_hostname', list),
            ('cmdb_department_name', list),
            ('cmdb_ip', list),
            ('cmdb_business_group_name', list),
            ('cmdb_application_name', list),
            ('id', int),
            ('name', str),
            ('item_group_name', list),
        )
        response = requests.get(self.url)
        self.assertEqual(response.status_code, 200)
        res_json = response.json()
        # print(res_json)
        self.assertEqual(res_json['code'], 200)
        self.assertIsInstance(res_json, dict)
        self.assertIsInstance(res_json['res'], list)
        for model in res_json['res']:
            for k, t in model_keys:
                self.assertTrue(k in model, model)
                self.assertIsInstance(model[k], t, model[k])


if __name__ == '__main__':
    unittest.main()
