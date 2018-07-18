'''
    Utility module
'''
import base64
import datetime
import functools
import hashlib
import json
import random
import re
import time
import uuid

import requests
import sqlalchemy
from decimal import Decimal
from yaml import load

from common.error import MonitorCenterError

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

from common import ucloud


DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

KEY = base64.b64encode(uuid.uuid5(uuid.NAMESPACE_X500, 'bidong wifi').hex.encode('utf-8'))

b64encode = base64.b64encode
b64decode = base64.b64decode


class MyJSONEncoder(json.JSONEncoder):
    '''
        serial datetime date
    '''

    def default(self, obj):
        '''
            serialize datetime & date
        '''
        if isinstance(obj, datetime.datetime):
            return obj.strftime(DATE_FORMAT)
        elif isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')
        elif isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, sqlalchemy.engine.RowProxy):
            _dict = {}
            for key, value in obj.items():
                _dict.setdefault(key, value)
            return _dict
        elif isinstance(obj, sqlalchemy.orm.state.InstanceState):
            return
        else:
            # return super(json.JSONEncoder, self).default(obj)
            return super(MyJSONEncoder, self).default(obj)


json_encoder = MyJSONEncoder(ensure_ascii=False).encode
json_decoder = json.JSONDecoder().decode

_PASSWORD_ = '23456789'
_VERIFY_CODE_ = '23456789'

MAC_PATTERN = re.compile(r'[-:_]')

MOBILE_PATTERN = re.compile(r'^(?:13[0-9]|14[57]|15[0-35-9]|17[678]|18[0-9])\d{8}$')

NUM_PATTERN = re.compile(r'[0-9]')


def page_arguments_to_int(page):
    '''
    use only in parser page arguments
    :param page:
    :return:
    '''
    try:
        page = int(page)
        if page < 1:
            raise MonitorCenterError(
                status_code=400, reason="ValueError ,page &page_size arguments must be number and >0")
    except ValueError:
        raise MonitorCenterError(
            status_code=400, reason="ValueError ,page &page_size arguments  must be number and > 0")
    return page


def check_mobile(mobile):
    return True if re.match(MOBILE_PATTERN, mobile) else False


def check_num(num):
    return True if re.match(NUM_PATTERN, num) else False


def _to_int(s):
    if isinstance(s, bytes):
        return int(s.decode())
    elif isinstance(s, str):
        return int(s)
    else:
        return s


def msg_send(MSG_URL, payload):
    """
    send mobile msg
    payload :  {mobile:'', msg:''}
    codes : utf8
    """
    header = {"Content-Type": "application/json "}
    r = requests.post(MSG_URL, data=json.dumps(payload), headers=header)
    data = json.loads(r.text)
    if data.get("Code") == 200:
        return True
    else:
        return False


def check_password(u_psw, q_psw):
    '''
        u_psw: user request password
        q_pwd: db saved password
        if password check pass, return False esle True
    '''
    un_equal = True
    if u_psw == q_psw or u_psw == md5(q_psw).hexdigest():
        un_equal = False
    return un_equal


def now(fmt=DATE_FORMAT, days=0, hours=0):
    _now = datetime.datetime.now()
    if days or hours:
        _now = _now + datetime.timedelta(days=days, hours=hours)
    return _now.strftime(fmt)


def cala_delta(start):
    '''
    '''
    _now = datetime.datetime.now()
    start = datetime.datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
    return (_now - start).seconds


def md5(*args):
    '''
        join args and calculate md5
        digest() : bytes
        hexdigest() : str
    '''
    md5 = hashlib.md5()
    md5.update(b''.join([item.encode('utf-8') if isinstance(item, str) else item for item in args]))
    return md5


def sha1(*args):
    sha1 = hashlib.sha1()
    sha1.update(''.join(args).encode('utf-8'))
    return sha1


def sha256(*args):
    sha256 = hashlib.sha256()
    sha256.update(''.join(args).encode('utf-8'))
    return sha256


def generate_password(len=4):
    '''
        Generate password randomly
    '''
    return ''.join(random.sample(_PASSWORD_, len))


def generate_verify_code(_len=6):
    '''
        generate verify code
    '''
    return ''.join(random.sample(_VERIFY_CODE_, _len))


def token(user):
    '''
        as bidong's util module
    '''
    _now = int(time.time())
    _88hours_ago = _now - 3600 * 88
    _now, _88hours_ago = hex(_now)[2:], hex(_88hours_ago)[2:]
    data = ''.join([user, _88hours_ago])
    ret_data = uuid.uuid5(uuid.NAMESPACE_X500, data).hex
    return '|'.join([ret_data, _now])


def token2(user, _time):
    _t = int('0x' + _time, 16)
    _88hours_ago = hex(_t - 3600 * 88)[2:]
    data = ''.join([user, _88hours_ago])
    return uuid.uuid5(uuid.NAMESPACE_X500, data).hex


def format_mac(mac):
    '''
        output : ##:##:##:##:##:##
    '''
    mac = re.sub(r'[_.,; -]', ':', mac).upper()
    if 12 == len(mac):
        mac = ':'.join([mac[:2], mac[2:4], mac[4:6], mac[6:8], mac[8:10], mac[10:]])
    elif 14 == len(mac):
        mac = ':'.join([mac[:2], mac[2:4], mac[5:7], mac[7:9], mac[10:12], mac[12:14]])
    return mac


def strip_mac(mac):
    if mac:
        return re.sub(MAC_PATTERN, '', mac.upper())
    else:
        return ''


def _fix_key(key):
    '''
        Fix key length to 32 bytes
    '''
    slist = list(key)
    fixkeys = ('*', 'z', 'a', 'M', 'h', '.', '8', '0', 'O', '.', '.', 'a', '@', 'v', '5', '5', 'k', 'v', 'O', '.', '*',
               'z', 'a', 'r', 'h', '.', 'x', 'k', 'O', '.', 'q', 'g')
    if len(key) < 32:
        pos = len(key)
        while pos < 32:
            slist.append(fixkeys[pos - len(key)])
            pos += 1
    if len(key) > 32:
        slist = slist[:32]
    return ''.join(slist)


def singleton(cls):
    ''' Use class as singleton. '''

    cls.__new_original__ = cls.__new__

    @functools.wraps(cls.__new__)
    def singleton_new(cls, *args, **kw):
        it = cls.__dict__.get('__it__')
        if it is not None:
            return it

        cls.__it__ = it = cls.__new_original__(cls, *args, **kw)
        it.__init_original__(*args, **kw)
        return it

    cls.__new__ = singleton_new
    cls.__init_original__ = cls.__init__
    cls.__init__ = object.__init__

    return cls


def query_string_argus_to_list(query_argus):
    '''
    :param query_argus:
    :return:
    '''
    res_list = []

    if query_argus and query_argus[0] == '':
        return res_list
    if not isinstance(query_argus, list):
        return res_list
    for string in query_argus:
        res = [v for v in string.split(",")]
        res_list.extend(res)
    return res_list


def base64_decode(s):
    return base64.b64decode(s).decode()


def read_yaml(path):
    with open(path, 'rb') as f:
        stream = f.read()
    return load(stream, Loader=Loader)


def dump_file(out_path, data_obj):
    with open(out_path, "w", encoding="UTF-8") as f_dump:
        json.dump(data_obj, f_dump, ensure_ascii=False)


def read_json(path):
    with open(path, 'r') as f:
        return json.load(f)


class UcloudUtil(object):
    @staticmethod
    def get_all_project_by_ucloud():
        response = ucloud.get(Action='GetProjectList')
        return response['ProjectSet']

