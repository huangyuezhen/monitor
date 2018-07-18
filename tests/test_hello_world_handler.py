import unittest
import requests
from tests.util import BaseTestCase


class HelloWorldTestCase(BaseTestCase):
    def test_get(self):
        response = requests.get(self.url)
        self.assertEqual(response.status_code, 200)
        res_json = response.json()
        self.assertIsInstance(res_json, dict)
        self.assertEqual(res_json['code'], response.status_code)
        self.assertEqual(res_json['res'], 'Hello world')


if __name__ == '__main__':
    unittest.main()
