from sqlalchemy import text

from sqlalchemy import bindparam
from sqlalchemy import Integer, String
from sqlalchemy import desc as sa_desc

from db.mysql import session_scope

from common.util import _to_int


class DbBase(object):
    def __init__(self, base, table_prefix=""):
        for name, obj in base.classes.items():
            self.__setattr__(name.lstrip(table_prefix), obj)

    @staticmethod
    def add(session, table, **kwargs):
        assert kwargs
        with session_scope(session) as session:
            new_object = table(**kwargs)
            row = session.add(new_object)
            return row

    @staticmethod
    def add_all(session, obs=[]):
        assert obs
        with session_scope(session) as session:
            session.add_all(obs)

    @staticmethod
    def update(session, table, filters, up_argus, flag=True):
        assert up_argus, filters
        with session_scope(session) as session:
            if flag:
                row = session.query(table).filter_by(**filters).update(up_argus, synchronize_session=False)
            else:
                row = session.query(table).filter(filters).update(up_argus, synchronize_session=False)

            return row

    @staticmethod
    def update_many(session, all_updates, flag=True):
        """
        update many rows in one  tramsaction
        :param session:
        :param all_updates: a list ,has keys :filters/table_name/up_argus
        :param flag: if true ,filters is keyword arguments else like CMDB.host.id ==_id
        :return: effect_row
        """
        assert all_updates
        with session_scope(session) as session:
            row = 0
            for ii in all_updates:
                filters = ii.pop("filters")
                table = ii.pop("table_name")
                _up_argus = ii.pop("up_argus")
                if flag:
                    row += session.query(table).filter_by(**filters).update(_up_argus, synchronize_session=False)
                else:
                    row += session.query(table).filter(filters).update(_up_argus, synchronize_session=False)
            return row

    @staticmethod
    def find(session, table, *args, one=False, return_query=False, **kwargs):
        # assert kwargs
        page, page_size = args if args else (1, 15)

        if not isinstance(page, int):
            page = int(page)
        if not isinstance(page_size, int):
            page_size = int(page_size)
        if page < 1 or page_size < 1:
            page, page_size = (1, 15)

        with session_scope(session) as session:
            q = session.query(table).filter_by(**kwargs)
            if one:
                res = q.first()
                return res
                # return q.first() if not return_query else q
            elif page > 0 and page_size > 0:
                total_count = q.count()
                if return_query:
                    return q
                offset = (page - 1) * page_size
                q = q.offset(offset).limit(page_size)
                return q, total_count

    @staticmethod
    def delete(session, table, filters):
        with session_scope(session) as session:
            session.query(table).filter_by(**filters).delete(synchronize_session=False)
            return True

    @staticmethod
    def join_find(session, table=(), one=True, **kwargs):
        """
        has been deserted
        """
        assert kwargs
        page, page_size = int(kwargs.get("page", 1)), int(kwargs.get("page_size", 15))
        _ob = kwargs.get("_key1")
        _value = kwargs.get("_value1")

        with session_scope(session) as session:
            table1, table2 = table
            if _value == -1:
                q = session.query(table1, table2).join(table2)
            else:
                q = session.query(table1, table2).join(table2).filter(_ob == _value)

            if one:
                return q.first()
            elif page > 0 and page_size > 0:
                total_count = q.count()
                offset = (page - 1) * page_size
                q = q.offset(offset).limit(page_size).all()
                return q, total_count

    @staticmethod
    def sql_find(engine, _sql, **kwargs):

        page, page_size = int(kwargs.get("page", 1)), int(kwargs.get("page_size", 15))
        if page > 0 and page_size > 0:
            offset = (page - 1) * page_size
            _sql = " limit".join([_sql, " {},{}".format(offset, page_size)])

        res = engine.execute(_sql)
        output = res.fetchall()
        res.close()
        return output

    @staticmethod
    def sql_find_bind_param(engine, _sql):

        res = engine.execute(_sql)
        output = res.fetchall()
        res.close()
        return output

    @staticmethod
    def page_bind_params(page, page_size, _sql, **kwargs):
        """
        sqlalchemy   bind params  to prevent sql injection
        bind page params
        if  page  or page_size is None ,set default(1,15)
        to prevent too much out_out to return

        """
        if isinstance(page, list):
            page = _to_int(page[0])
        if isinstance(page_size, list):
            page_size = _to_int(page_size[0])

        if page < 0 or page_size < 0:
            page = 1
            page_size = 15

        offset = (page - 1) * page_size
        _limit_sql = " limit :offset,:page_size "
        _sql = " ".join([_sql, _limit_sql])
        kwargs.update({"offset": [offset], "page_size": [page_size]})

        return _sql, kwargs

    @staticmethod
    def sql_bindparams(int_params_list, str_params_list, **kwargs):
        """
        to  prevent sql injection ,use sql bindparams
        :param kwargs:  self.request.arguments
        :return: a list of  bindparams
        """
        b_p = []

        for key, _value in kwargs.items():

            if isinstance(_value, list):
                _value = _value[0].decode() if isinstance(_value[0], bytes) else _value[0]
            elif isinstance(_value, bytes):
                _value = _value.decode()

            if key in int_params_list:
                o = bindparam(key, value=_value, type_=Integer)
            elif key in str_params_list:
                o = bindparam(key, value=_value, type_=String)
            else:
                continue
            b_p.append(o)
        return b_p

    def textualsql_get(self, engine, _sql, textsql_where, int_params_list, str_params_list, page, page_size,
                       sep="  AND ", t_count_flag=True, **kwargs):
        """
        textualsql selct to prevent sql injection
        """
        """pop page arguments ,if exist"""
        kwargs.pop("page", -1)
        kwargs.pop("page_size", -1)

        """ get  where condition statement"""
        where_condition = textsql_where(sep=sep, **kwargs)

        """select statement join filters"""
        if where_condition:
            _sql = "  WHERE ".join([_sql, where_condition])

        if not t_count_flag:
            """ not get total count """
            _sql, kwargs = self.page_bind_params(page, page_size, _sql, **kwargs)

        """where condition  bind params"""
        count_b_q = self.sql_bindparams(int_params_list, str_params_list, **kwargs)

        stmt = text(_sql, bindparams=count_b_q)

        return self.sql_find_bind_param(engine, stmt)

    # def id_generator(self, session, table_name='', field_name='id'):
    #     ID = self.ids
    #     with session_scope(session) as session:
    #         ids = session.query(ID).filter(ID.table_name == table_name,
    #                                        ID.field_name == field_name).with_for_update().one()
    #         # this row is now locked
    #         ids.nextid = ids.nextid + 1
    #         session.add(ids)
    #         return ids.nextid

    @staticmethod
    def join_query(session, join_tables=(), left_join_tables=(), select_col=(), filter_args=(),
                   order_by=None, desc=False, group_by=(), limit_offset=0, limit_count=15):
        assert join_tables or left_join_tables, "takes exactly one tables argument"
        if select_col:
            q = session.query(*select_col)
        else:
            select_tables = [t for ta in join_tables for t in ta]
            select_tables.extend([t for ta in left_join_tables for t in ta])
            q = session.query(*select_tables)

        for table_arr in join_tables:
            q = q.join(*table_arr)

        for table_arr in left_join_tables:
            q = q.outerjoin(*table_arr)

        if filter_args:
            q = q.filter(*filter_args)

        if order_by is not None:
            if desc:
                q = q.order_by(sa_desc(order_by))
            else:
                q = q.order_by(order_by)

        if group_by:
            q = q.group_by(*group_by)

        q = q.offset(int(limit_offset)).limit(int(limit_count))
        # print(q)

        return q.all(), q.count()
