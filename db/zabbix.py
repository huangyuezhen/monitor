from sqlalchemy.ext.automap import automap_base
from sqlalchemy import MetaData
from db.mysql import ENGINES
from db.base import DbBase


class Zabbix(DbBase):
    pass


def init_db():
    zabbix = {}
    for name, engine in ENGINES.items():
        if not name.endswith('zabbix'):
            continue

        metadata = MetaData()
        metadata.reflect(engine, only=[
            'hosts',
            'items',
            'applications',
            'items_applications',
            'graphs',
            "graphs_items",
            'history',
            'history_log',
            'history_str',
            'history_text',
            'history_uint',
            'mappings',
            'triggers',
            'events',
            'functions',
            'screens',
            'screens_items'
        ])
        base = automap_base(metadata=metadata)
        base.prepare()
        zabbix[name] = Zabbix(base)
    return zabbix


ZABBIX = init_db()
