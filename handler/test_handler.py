from tornado.log import app_log
from handler.base import BaseHandler


class HelloWorldHandler(BaseHandler):
    def get(self):
        app_log.info(self.request.arguments)
        self.render_json_response(code=200, msg='OK', res="Hello world")

    def post(self, *args, **kwargs):
        app_log.info(self.request.arguments)
        self.render_json_response(code=200, msg='OK', res="Hello world")
