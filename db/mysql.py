import re

from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy import exc
from sqlalchemy import orm
from common.error import DBError
from conf import settings

ENGINES = {}
SESSIONS = {}
conn = '{dialect}+{driver}://{username}:{password}@{host}:{port}/{database}?charset=utf8'
for db_name, db_config in settings['db'].items():
    DB_URL = conn.format(dialect=db_config['dialect'], driver=db_config['driver'], username=db_config['username'],
                         password=db_config['password'], host=db_config['host'], port=db_config['port'],
                         database=db_config['database'])
    db_kwargs = db_config['config']
    ENGINES[db_name] = create_engine(DB_URL, **db_kwargs)
    SESSIONS[db_name] = None

Filed = re.compile(r'(has no property) (.*)')


def connect_all():
    for engine_name in ENGINES:
        connect(engine_name)
    return SESSIONS


def connect(engine_name):
    '''
        uri: dialect+driver://user:password@host:port/dbname[?key=value...]
        kwargs: reference sqlalchemy.create_engine
    '''
    global SESSIONS
    if not SESSIONS.get(engine_name):
        # engine = create_engine(uri, **kwargs)
        session = orm.sessionmaker(bind=ENGINES[engine_name])
        if not session:
            raise DBError('%s session is None' % engine_name)
        SESSIONS[engine_name] = session

    return SESSIONS[engine_name]


def close_all(sessions):
    for n, s in sessions.items():
        if isinstance(s, orm.Session):
            s.close()


@contextmanager
def session_scope(session):
    '''
        caller create new session & close created session
        caller control session scope:
            request scope
            application scope
    '''
    try:
        yield session
        session.commit()
    except exc.IntegrityError:
        session.rollback()
        raise DBError(400, reason="Duplicate  error")
    except orm.exc.NoResultFound as e:
        session.rollback()
        raise DBError(404, reason=str(e))
    except exc.InvalidRequestError as e:
        error_info = e.args[0]
        value = Filed.search(error_info)
        if value:
            value = value.group(2)
            reason = "InvalidRequestError, arguments %s is not allowed" % value
        else:
            reason = "InvalidRequestError, please check your request arguments"
        session.rollback()
        raise DBError(status_code=400, reason=reason)
    except Exception as e:
        session.rollback()
        raise DBError(status_code=400, reason=str(e))
