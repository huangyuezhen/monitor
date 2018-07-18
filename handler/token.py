import jwt
from ldap3.core.exceptions import LDAPException
from tornado.log import app_log

from common import ldap
from common.error import MonitorCenterError
from conf import settings
from .base import BaseHandler
from common.util import  base64_decode


class TokenHandler(BaseHandler):
    def post(self):
        """
        用户登录,获取token
        """
        argus = self.arguments
        username = argus['username'] if 'username' in argus.keys() else None
        password = argus['password'] if 'password' in argus.keys() else None

        if not username or not password:
            raise MonitorCenterError(status_code=400, reason='Missing arguments,please check  your username & password')

        username = base64_decode(username)
        password = base64_decode(password)

        try:
            user = ldap.valid_user(username, password)
        except LDAPException as e:
            app_log.error(e)
            raise MonitorCenterError(status_code=500, reason='ldap error')

        if not user:
            raise MonitorCenterError(status_code=400, reason='valid failed')

        token = jwt.encode(payload=user, key=settings['token_secret'], algorithm='HS256').decode("utf-8")

        self.render_json_response(code=200, msg='OK', res={'token': token})