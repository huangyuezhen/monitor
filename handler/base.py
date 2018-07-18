from __future__ import absolute_import, division, print_function, with_statement

import json
import sys

import tornado.auth
import tornado.escape
import tornado.gen
import tornado.httpclient
import tornado.httputil
import tornado.ioloop
import tornado.locale
import tornado.options
import tornado.web
from tornado.log import access_log
from tornado.log import gen_log

from common import error
from common import util
from db import mysql

from common.error import MonitorCenterError
from worker.item_model import get_item_model_by_id
from worker.util import dumps_argus
from worker.util import loads_res
from worker.util import check_arguements
from sqlalchemy import func
from db.mysql import session_scope
from db.monitor_center import MC
from common import zabbix_api
from common.zabbix_util import ZabbixUtil
from common.util import query_string_argus_to_list

HTTPError = tornado.web.HTTPError

json_encoder = util.json_encoder
json_decoder = util.json_decoder
from conf import settings


ENV = settings['env']


class BaseHandler(tornado.web.RequestHandler):
    '''
        BaseHandler
        override class method to adapt special demands
    '''
    OK = {'code': 200, 'msg': 'OK'}
    RESPONSES = error.responses

    def options(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Methods', "PUT")
        self.add_header('Access-Control-Allow-Methods', "POST")
        self.add_header('Access-Control-Allow-Methods', "DELETE")
        # self.set_header('Access - Control - Allow - Methods', "POST")

        self.set_header('Access-Control-Allow-Headers', 'x-requested-with,content-type')

    def _get_argument(self, name, default, source, strip=True):
        args = self._get_arguments(name, source, strip=strip)
        if not args:
            if default is self._ARG_DEFAULT:
                raise tornado.web.MissingArgumentError(name)
            return default
        return args[0]

    def set_status(self, status_code, reason=None):
        '''
            Set custom error resson
        '''
        self._status_code = status_code
        self._reason = 'Unknown Error'
        if reason is not None:
            self._reason = tornado.escape.native_str(reason)
        else:
            try:
                self._reason = self.RESPONSES[status_code]
            except KeyError:
                raise ValueError('Unknown status code {}'.format(status_code))

    def write_error(self, status_code, **kwargs):

        # Customer error return format
        if self.settings.get('debug') and 'exc_info' in kwargs:
            self.set_header('Access-Control-Allow-Origin', '*')
            self.set_header('Content-Type', 'text/plain')
            import traceback
            for line in traceback.format_exception(*kwargs['exc_info']):
                self.write(line)
            self.finish()
        else:
            self.render_json_response(code=status_code, msg=self._reason)

    def _handle_request_exception(self, e):
        if isinstance(e, tornado.web.Finish):
            # not an error; just finish the request without loggin.
            if not self._finished:
                self.finish(*e.args)
            return
        try:
            self.log_exception(*sys.exc_info())
        except Exception:
            access_log.error('Error in exception logger', exc_info=True)

        if self._finished:
            return
        if isinstance(e, HTTPError):
            if e.status_code not in self.RESPONSES and not e.reason:
                gen_log.error('Bad HTTP status code: %d', e.status_code)
                self.send_error(500, exc_info=sys.exc_info())
            else:
                self.send_error(e.status_code, exc_info=sys.exc_info())
        else:
            self.send_error(500, exc_info=sys.exc_info())

    def log_exception(self, typ, value, tb):
        if isinstance(value, HTTPError):
            if value.log_message:
                format = '%d %s: ' + value.log_message
                args = ([value.status_code, self._request_summary()] + list(value.args))
                access_log.warning(format, *args)

        access_log.error('Exception: %s\n%r', self._request_summary(),
                         self.request, exc_info=(typ, value, tb))

    def render_exception(self, ex):
        self.set_status(ex.status_code)
        self.render('error.html', code=ex.status_code, msg=ex.reason)

    def render_json_response(self, **kwargs):
        '''
            Encode dict and return response to client
        '''
        callback = self.get_argument('callback', None)
        if callback:
            # return jsonp
            self.set_status(200, kwargs.get('msg', None))
            self.finish('{}({})'.format(callback, json_encoder(kwargs)))
        else:
            self.set_status(kwargs['code'], kwargs.get('msg', None))
            self.set_header('Content-Type', 'application/json;charset=utf-8')
            self.set_header('Access-Control-Allow-Origin', '*')
            _format = self.get_argument('_format', None)
            if _format:
                # return with indent
                self.finish(json.dumps(json.loads(json_encoder(kwargs)), indent=4))
            else:
                self.finish(json_encoder(kwargs))

    def prepare(self):
        '''
            check client paltform
        '''
        self.set_header('Access-Control-Allow-Origin', '*')
        self.arguments = None
        self.sessions = mysql.connect_all()

        # try to parse request body
        self._parse_body()

    def on_finish(self):
        self.arguments = None

    def _parse_body(self):
        '''
            1. request body: support json, convert single value to tuple

        '''
        content_type = self.request.headers.get('Content-Type', '')
        # parse json format arguments in request body content

        if self.request.body and content_type.startswith('application/json'):
            try:
                arguments = json_decoder(tornado.escape.native_str(self.request.body))
                self.arguments = arguments
            except json.decoder.JSONDecodeError:
                """invalid  json arguments"""
                raise error.MonitorCenterError(400, reason="JSONDecodeError,invalid json arguments")

                #     for name, values in arguments.items():
                #         if isinstance(values, str):
                #             values = [values, ]
                #         elif isinstance(values, int) or isinstance(values, float):
                #             values = [str(values), ]
                #         elif values:
                #             values = [v for v in values if v]
                #
                #         if values:
                #             self.request.arguments.setdefault(name, []).extend(values)
        elif self.request.query_arguments:
            # query string
            q_arguments = {}
            for key in self.request.query_arguments.keys():
                value = self.request.query_arguments[key][0].decode()
                q_arguments.update({key: value})

            if "_format" in q_arguments.keys():
                q_arguments.pop("_format")
            if "page" in q_arguments.keys():
                page = q_arguments.pop("page")
                page = util.page_arguments_to_int(page)
                if page < 1:
                    self.request.arguments.pop("page")
            if "page_size" in q_arguments.keys():
                page_size = q_arguments.pop("page_size")
                page_size = util.page_arguments_to_int(page_size)
                if page_size < 1:
                    self.request.arguments.pop("page_size")

            if self.arguments:
                self.arguments.update(q_arguments)
            else:
                self.arguments = q_arguments


class ZabbixBaseHandler(BaseHandler):
    def prepare(self):
        super(ZabbixBaseHandler, self).prepare()
        self.zbx_sessions = {n: s() for n, s in self.sessions.items()}
        self.zabbix = ZabbixUtil(zabbix_api[ENV])

    def get_args_dict(self, *args, prefix=""):
        res = {}
        for arg in args:
            a = self.get_arguments(arg)
            try:
                k = arg.split(prefix, 1)[1]
            except IndexError:
                k = arg
            res[k] = query_string_argus_to_list(a)
        return res

    def on_finish(self):
        super(ZabbixBaseHandler, self).on_finish()
        mysql.close_all(self.zbx_sessions)


class MonitorBaseHandler(BaseHandler):
    def prepare(self):
        super(MonitorBaseHandler, self).prepare()
        self.mc_sessions = self.sessions['monitor_center']()

    def on_finish(self):
        super(MonitorBaseHandler, self).on_finish()
        self.mc_sessions.close()
        # mysql.close_all(self.mc_sessions)


class ModelBaseHandler(MonitorBaseHandler):
    def get(self, *args, **kwargs):
        res = []
        filter_args = []
        name = self.get_arguments("name")
        page = int(self.get_argument('page', 1))
        page_size = int(self.get_argument('page_size', 15))
        if page < 1 and page_size < 1:
            page, page_size = (0, 15)

        if name:
            name = name[0].split(',')
            filter_args.append(self.model_table.name.in_(name))
        db_res, total_count = MC.join_query(
            session=self.mc_sessions,
            select_col=[self.model_table,
                        func.group_concat(self.item_group_table.name).label('item_group_name')],
            left_join_tables=([self.model_group_map_table, self.model_table.id == self.map_table_model_id_obj], [
                self.item_group_table, self.item_group_table.id == self.model_group_map_table.item_groups_id
            ]),
            filter_args=filter_args,
            group_by=(self.model_table.id, ),
            limit_offset=page - 1,
            limit_count=page_size)

        for model_row, item_group_name in db_res:
            model_row.__dict__ = loads_res(self.host_filters, model_row)
            if item_group_name:
                model_row.__dict__['item_group_name'] = item_group_name.split(',')
            else:
                model_row.__dict__['item_group_name'] = []
            for k, v in model_row.__dict__.items():
                if v is None:
                    if k in self.list_argus:
                        model_row.__dict__[k] = []
                    else:
                        model_row.__dict__[k] = ""
            res.append(model_row.__dict__)

        self.render_json_response(code=200, msg='ok', res=res, total_count=total_count)

    def post(self, *args, **kwargs):
        argus = self.arguments

        if not check_arguements(self.list_argus, argus):
            raise MonitorCenterError(status_code=401, reason='host filters arguments must be list')
        name = argus.get('name', None)
        if not name:
            raise MonitorCenterError(status_code=401, reason="Missing arguments, name is required")
        q_res = self.mc_sessions.query(self.model_table).filter(self.model_table.name == name).first()
        if q_res is not None:
            raise MonitorCenterError(status_code=401, reason="The model name existed: %s" % name)

        argus = dumps_argus(self.host_filters, argus)
        item_group_name = argus.pop('item_group_name', [])

        with session_scope(self.mc_sessions) as session:
            item_model_ins = self.model_table(**argus)
            session.add(item_model_ins)
            session.flush()

            _id = item_model_ins.id

            if item_group_name:
                item_group_ids = session.query(self.item_group_table.id, self.item_group_table.name).filter(
                    self.item_group_table.name.in_(item_group_name)).all()
                item_group_ids = sorted(item_group_ids, key=lambda x: item_group_name.index(x[1]))
                him_ins = [
                    self.model_group_map_table(**{
                        self.map_table_model_id: _id,
                        'item_groups_id': item_group_id[0]
                    }) for item_group_id in item_group_ids
                ]
                if him_ins:
                    session.add_all(him_ins)
        res = get_item_model_by_id(self.mc_sessions, self.model_table, self.host_filters, _id)
        self.render_json_response(code=200, msg='OK', res=res)

    def put(self, *args, **kwargs):
        argus = self.arguments
        _id = argus.pop('id', None)

        if not _id:
            raise MonitorCenterError(status_code=401, reason="Missing arguments, model id is required")

        if not check_arguements(self.list_argus, argus):
            raise MonitorCenterError(status_code=401, reason='host filters arguments must be list')

        item_group_name = argus.pop('item_group_name', [])
        argus = dumps_argus(self.host_filters, argus)

        with session_scope(self.mc_sessions) as session:
            session.query(self.model_table).filter_by(id=_id).update(argus, synchronize_session=False)
            session.query(self.model_group_map_table).filter(self.map_table_model_id_obj == _id).delete(
                synchronize_session=False)

            if item_group_name:
                item_group_ids = session.query(self.item_group_table.id, self.item_group_table.name).filter(
                    self.item_group_table.name.in_(item_group_name)).all()
                item_group_ids = sorted(item_group_ids, key=lambda x: item_group_name.index(x[1]))
                him_ins = [
                    self.model_group_map_table(**{
                        self.map_table_model_id: _id,
                        'item_groups_id': item_group_id[0]
                    }) for item_group_id in item_group_ids
                ]
                if him_ins:
                    session.add_all(him_ins)

        res = get_item_model_by_id(self.mc_sessions, self.model_table, self.host_filters, _id)
        self.render_json_response(code=200, msg='ok', res=res)

    def delete(self, *args, **kwargs):
        argus = self.arguments
        if not argus:
            raise MonitorCenterError(status_code=401, reason='id is required')
        _id = argus.get('id', None)
        if not _id:
            raise MonitorCenterError(status_code=401, reason='id is required')

        with session_scope(self.mc_sessions) as session:
            session.query(self.model_table).filter(self.model_table.id == _id).delete(synchronize_session=False)
            session.query(self.model_group_map_table).filter(self.map_table_model_id_obj == _id).delete(
                synchronize_session=False)

        self.render_json_response(code=200, msg='OK')

