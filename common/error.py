from tornado.httputil import responses
from tornado.web import HTTPError

RESPONSES = responses


class MonitorCenterError(HTTPError):
    def __str__(self):
        message = 'HTTP %d: %s' % (
            self.status_code,
            self.reason or RESPONSES.get(self.status_code, 'Unknown'))
        if self.log_message:
            return message + ' (' + (self.log_message % self.args) + ')'
        else:
            return message


class TokenError(HTTPError):
    pass


class DBError(HTTPError):
    def __str__(self):
        message = 'HTTP %d: %s' % (
            self.status_code,
            self.reason or RESPONSES.get(self.status_code, 'Unknown'))
        if self.log_message:
            return message + ' (' + (self.log_message % self.args) + ')'
        else:
            return message
