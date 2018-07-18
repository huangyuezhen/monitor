import unittest
from conf import settings


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.settings = settings
        port = settings['server']['port']
        self.url = 'http://127.0.0.1:' + str(port)

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
