import json


def check_arguements(list_argus, argus):
    '''
     根据 list_argus 检测 argus 里对应的参数是否为数组
    :param list_argus:  参数名 数组
    :param argus:  需要检测的参数
    :return:
    '''
    for _key in list_argus:
        if _key in argus.keys():
            if not isinstance(argus[_key], list):
                return False
    return True


def dumps_argus(key_field, argus):
    """
     dump json to string
    :param key_field:   field  than need to be dumps
    :param argus : dictionary need to dumps
    """
    for key, value in argus.items():
        if key in key_field:
            argus.update({key: json.dumps(value)})
    return argus


def loads_res(json_field, item):
    """
    load json_string to json
    :param json_field:   field  than need to be load
    :param item:  object (return from query)
    :return:
    """
    item.__dict__.pop("_sa_instance_state") if "_sa_instance_state" in item.__dict__.keys() else item.__dict__
    for key, value in item.__dict__.items():
        if value and not isinstance(value, int) and key in json_field:
            try:
                item.__dict__.update({key: json.loads(value, encoding='utf-8')})
            except:
                pass

    return item.__dict__
