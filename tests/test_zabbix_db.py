import sys
sys.path.append('..')
import unittest
from tests.util import BaseTestCase
from db.zabbix import ZABBIX
from db.mysql import SESSIONS
from db.mysql import connect_all


class ZabbixTestCase(BaseTestCase):
    def setUp(self):
        super(ZabbixTestCase, self).setUp()
        connect_all()
        self.zbx_dbs = ZABBIX
        self.zbx_sessions = {n: s() for n, s in SESSIONS.items() if n.endswith('zabbix')}

    def test_db_available(self):
        for name, base in self.zbx_dbs.items():
            self.assertTrue(name in self.settings['db'], name)
            hosts = base.hosts
            zbx_sess = self.zbx_sessions[name]
            q = zbx_sess.query(hosts).offset(0).limit(10)
            q.all()


if __name__ == '__main__':
    unittest.main()
