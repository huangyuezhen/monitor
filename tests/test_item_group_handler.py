import sys
sys.path.append('.')
import unittest
import requests
from tests.util import BaseTestCase


class ItemGroupTestCase(BaseTestCase):
    def setUp(self):
        super(ItemGroupTestCase, self).setUp()
        self.url = self.url + '/api/' + 'item_group'

    def test_get_format(self):
        group_keys = (
            ('name', str),
            ('id', int),
            ('items', list),
        )
        item_keys = (
            ('id', int),
            ('name', str),
            ('sub', int),
            ('key', str),
            ('mc_item_groups_id', int),
            ('alias', str),
            ('sort_num', int),
            ('format', str),
        )
        response = requests.get(self.url)
        self.assertEqual(response.status_code, 200)
        res_json = response.json()
        # print(res_json)
        self.assertEqual(res_json['code'], 200)
        self.assertIsInstance(res_json, dict)
        self.assertIsInstance(res_json['res'], list)
        for group in res_json['res']:
            self.assertIsInstance(group, dict, group)
            for k, t in group_keys:
                self.assertTrue(k in group, group)
                self.assertIsInstance(group[k], t, group[k])
            items = group['items']
            self.assertIsInstance(items, list, items)
            for item in items:
                for k, t in item_keys:
                    self.assertTrue(k in item, item)
                    self.assertIsInstance(item[k], t, item[k])


if __name__ == '__main__':
    unittest.main()
