import unittest
from tests.util import BaseTestCase
from common import cmdb


class CmdbTestCase(BaseTestCase):
    def setUp(self):
        super(CmdbTestCase, self).setUp()
        self.cmdb = cmdb

    def test_get_host_format(self):
        res_json = cmdb.get('host')
        self.assertIsInstance(res_json, list)

    def test_get_host_by_hostname(self):
        params = {
            "hostname": 'UGZB-CANYIN-A3-002',
        }
        res_json = cmdb.get('host', **params)
        # print(res_json)
        self.assertEqual(res_json[0]['hostname'], params['hostname'])


if __name__ == '__main__':
    unittest.main()
