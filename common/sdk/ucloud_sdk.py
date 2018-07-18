# -*- coding: utf-8 -*-
import hashlib
import http.client
import json
import urllib.error
import urllib.parse
import urllib.parse
import urllib.request


class UCLOUDException(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


def _verfy_ac(private_key, params):
    items = list(params.items())
    items.sort()

    params_data = ""
    for key, value in items:
        params_data = params_data + str(key) + str(value)

    params_data = params_data + private_key

    '''use sha1 to encode keys'''
    hash_new = hashlib.sha1()
    hash_new.update(params_data.encode(encoding="utf-8"))
    hash_value = hash_new.hexdigest()
    return hash_value


class UConnection(object):
    def __init__(self, base_url):
        self.base_url = base_url
        o = urllib.parse.urlsplit(base_url)
        if o.scheme == 'https':
            self.conn = http.client.HTTPSConnection(o.netloc)
        else:
            self.conn = http.client.HTTPConnection(o.netloc)

    def __del__(self):
        self.conn.close()

    def get(self, resouse, params):
        resouse += "?" + urllib.parse.urlencode(params)
        try:
            self.conn.request("GET", resouse)
        except http.client.RemoteDisconnected:
            self.__init__(self.base_url)
            self.conn.request("GET", resouse)
        response = json.loads(self.conn.getresponse().read().decode(encoding='utf-8'))
        return response

    def post(self, uri, params):
        headers = {"Content-Type": "application/json"}
        try:
            self.conn.request("POST", uri, json.JSONEncoder().encode(params), headers)
        except http.client.RemoteDisconnected:
            self.__init__(self.base_url)
            self.conn.request("POST", uri, json.JSONEncoder().encode(params), headers)
        response = json.loads(self.conn.getresponse().read())
        return response


class UcloudApiClient(object):
    # 添加 设置 数据中心和  zone 参数
    def __init__(self, base_url, public_key, private_key):
        self.g_params = {}
        self.g_params['PublicKey'] = public_key
        self.private_key = private_key
        self.conn = UConnection(base_url)

    def _get(self, uri, project_id=None, params=None):
        # print params
        _params = dict(self.g_params, **params)

        if project_id:
            _params["ProjectId"] = project_id

        _params["Signature"] = _verfy_ac(self.private_key, _params)
        return self.conn.get(uri, _params)

    def _post(self, uri, project_id=None, params=None):
        _params = dict(self.g_params, **params)

        if project_id:
            _params["ProjectId"] = project_id

        _params["Signature"] = _verfy_ac(self.private_key, _params)
        return self.conn.post(uri, _params)

    def get(self, uri='/', project_id=None, **params):
        response = self._get(uri=uri, project_id=project_id, params=params)
        if response['RetCode'] != 0:
            raise UCLOUDException(response['Message'])
        return response

    def post(self, uri='/', project_id=None, **params):
        response = self._post(uri=uri, project_id=project_id, params=params)
        if response['RetCode'] != 0:
            raise UCLOUDException(response['Message'])
        return response
