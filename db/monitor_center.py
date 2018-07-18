from sqlalchemy.ext.automap import automap_base
from db.mysql import ENGINES, session_scope
from db.base import DbBase


class MonitorCenter(DbBase):
    pass


def init_db():
    engine = ENGINES['monitor_center']
    base = automap_base()
    base.prepare(engine, reflect=True)
    return MonitorCenter(base, table_prefix="mc_")


MC = init_db()



