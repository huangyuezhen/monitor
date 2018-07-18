import datetime
import time
from worker.zbx_item import get_items_raw
from worker.zbx_item import _convert_item_name_variable
from db.monitor_center import MC


def get_trend_time_range_raw(zbx_db, zbx_engine, itemids, value_type, start_clock, end_clock):
    _sql = """
SELECT 
    itemid, clock  , value_min  min, value_avg avg, value_max max
FROM
    {table_name}
WHERE
    clock BETWEEN FLOOR({start_clock}) AND {end_clock} and itemid in({items})
ORDER BY clock
    """

    #  不同的数据类型 取不同 的表
    value_type_table = {0: 'trends', 3: 'trends_uint'}
    if value_type not in value_type_table.keys():
        return

    trend_table = value_type_table[value_type]

    _itemid = itemids[0]
    itemids = map(str, itemids)
    _sql = _sql.format(
        table_name=trend_table,
        items=','.join(itemids),
        start_clock=str(start_clock),
        end_clock=str(end_clock),
    )
    res = zbx_db.sql_find(engine=zbx_engine, _sql=_sql, page_size=9999999)
    if len(res) == 0:
        return [(_itemid, None, None, None, None)]
    return res


def substract_month(month, year):
    if month < 1:
        month = 12 + month
        year = year - 1
    return month, year


#  获取item 取值
# 1:最小值 2: 平均值 3: 最大值 4:最新值
def get_item_sub(
        mc_session,
        zbx_db,
):
    zbx_db.find()


def get_middle_start_clock(link_ratio_type, end_clock):
    if link_ratio_type > 0:
        end_time = datetime.datetime.fromtimestamp(end_clock)
        year = end_time.year
        month = end_time.month
        day = end_time.day
        hour = end_time.hour
        minute = end_time.minute
        second = end_time.second
    if link_ratio_type == 1:
        midddle_datetime = end_time - datetime.timedelta(days=1)
        start_datetime = midddle_datetime - datetime.timedelta(days=1)

    if link_ratio_type == 2:
        midddle_datetime = end_time - datetime.timedelta(weeks=1)
        start_datetime = midddle_datetime - datetime.timedelta(weeks=1)
    if link_ratio_type == 3:
        month = month - 1
        month, year = substract_month(month, year)
        midddle_datetime = datetime.datetime(year, month, day, hour, minute, second)
        month2 = month - 1
        month, year = substract_month(month2, year)
        start_datetime = datetime.datetime(year, month, day, hour, minute, second)
    if link_ratio_type == 4:
        month = month - 3
        month, year = substract_month(month, year)
        midddle_datetime = datetime.datetime(year, month, day, hour, minute, second)
        month2 = month - 3
        month, year = substract_month(month, year)
        start_datetime = datetime.datetime(year, month2, day, hour, minute, second)
    return start_datetime, midddle_datetime


#  返回所有clock
def get_full_clock(min_clock, start_clock, end_clock):

    res = dict()
    while min_clock > start_clock:
        res.update({min_clock: '1'})
        min_clock = min_clock - 3600

    middle = min_clock + 3600
    while middle < end_clock:
        res.update({middle: '1'})
        middle = middle + 3600

    return res


def get_trend_items(zbx_session,
                    zbx_db,
                    cmdb_host_info,
                    application_name=(),
                    item_keys=(),
                    order_by=None,
                    desc=False,
                    page=1,
                    page_size=9999999,
                    zbx_engine=None,
                    end_clock=None,
                    trend_value=False,
                    link_ratio_type=-1):
    """
    获取zabbix item信息
    :param zbx_session: (session obj)
    :param zbx_db: (zabbix obj)
    :param cmdb_host_info: (ordered dict obj) see: host_filter_by_cmdb()
    :param application_name: (tuple or list) zabbix item application name list
    :param item_keys: (str) zabbix item key
    :param order_by: (str) order by col
    :param desc: (bool) order by desc?
    :param page: (int) limit start
    :param page_size: (int) limit size
    :param last_value: (bool) return last value?
    :param zbx_engine: (engine obj) zabbix engine
    :param problem_trigger: (bool) return problem trigger?
    :param time_range_value: (bool) request item history min,avg,max value
    :param start_clock: (int) timestamp of start clock
    :param end_clock: (int) timestamp of end clock
    :param    mutil_history_value ： 返回多个 历史值（图表）
    :return: (ordered dict obj, int) host item info and item count
    """
    cycle_type = {1: '日', 2: '周', 3: '月', 4: '季'}
    if trend_value:
        assert end_clock, "time range value need to use start_clock and end_clock argument."
    history_type_itemids = dict()
    itemid_iteminfo = dict()
    item_res_label = (
        'zbx_item_id',
        'zbx_item_name',
        'zbx_item_key',
        'zbx_item_state',
        'zbx_item_error',
        'zbx_item_units',
        'zbx_item_multiplier',
        'zbx_item_formula',
        'zbx_item_value_type',
        'zbx_item_valuemapid',
        'zbx_hostname',
        'zbx_host_status',
        'zbx_application_name',
    )
    if order_by not in item_res_label:
        order_by = None
    limit_offset = int(page) - 1
    limit_count = int(page_size)
    host_list = list(cmdb_host_info.keys())

    db_res, total_host = get_items_raw(
        zbx_session=zbx_session,
        zbx_db=zbx_db,
        host_list=host_list,
        item_app_names=application_name,
        item_keys=item_keys,
        order_by=order_by,
        desc=desc,
        limit_offset=limit_offset,
        limit_count=limit_count)

    if total_host < 1:
        return cmdb_host_info, total_host

    lower_hostname_map = {h.lower(): h for h in host_list}
    for row in db_res:
        item = {}
        item.update({k: row.__getattribute__(k) for k in item_res_label})
        item['zbx_item_name'] = _convert_item_name_variable(item['zbx_item_name'], item['zbx_item_key'])
        if not item['zbx_application_name']:
            item['zbx_application_name'] = 'No Application'
        item['zbx_application_name'] = item['zbx_application_name'].split(',')

        # item_type itemid dict
        if trend_value:
            history_items = history_type_itemids.setdefault(item['zbx_item_value_type'], [])
            history_items.append(item['zbx_item_id'])
        # itemid iteminfo dict
        if trend_value:
            itemid_iteminfo[item['zbx_item_id']] = item
            itemid_iteminfo[item['zbx_item_id']]['trend_value'] = {}
            # else:
            #     item_key = item.pop('zbx_item_key')
            # cmdb_host_info[lower_hostname_map[item['zbx_hostname'].lower()]]['zbx_items'][item_key] = item

    if trend_value:
        assert zbx_engine, "last_value and time range value need to use zbx_engine argument."
        for history_type, itemids in history_type_itemids.items():

            start_datetime, midddle_datetime = get_middle_start_clock(link_ratio_type, end_clock)  # 获取时间

            middle_clock = round(time.mktime(midddle_datetime.timetuple()))
            start_clock = round(time.mktime(start_datetime.timetuple()))

            mutil_trend_data_dict = dict()
            clock_dict = {1: [middle_clock, end_clock], 2: [start_clock, middle_clock]}
            full_clock_dict = dict()

            for key in clock_dict:
                _start_clock, _end_clock = clock_dict[key]
                mutil_trend_data = get_trend_time_range_raw(
                    zbx_db=zbx_db,
                    zbx_engine=zbx_engine,
                    value_type=history_type,
                    itemids=itemids,
                    start_clock=_start_clock,
                    end_clock=_end_clock)
                mutil_trend_data_dict[_end_clock] = mutil_trend_data
                min_clock = min(list(map(lambda x: x[1], mutil_trend_data)))
                if min_clock:
                    full_clock_dict[_end_clock] = get_full_clock(min_clock, _start_clock, _end_clock)  # 把缺省值补充为null
                else:
                    full_clock_dict[_end_clock] = {}

    if mutil_trend_data_dict:

        for _key in mutil_trend_data_dict:
            mutil_trend_data = mutil_trend_data_dict[_key]
            full_clock = full_clock_dict[_key]

            if len(mutil_trend_data) == 1 and mutil_trend_data[0][1] == None:  # 数值不存在时
                itemid = mutil_trend_data[0][0]
                itemid_iteminfo[itemid]['trend_value'][str(_key)] = []
                continue
            elif len(full_clock.keys()) > len(mutil_trend_data):
                itemid = mutil_trend_data[0][0]
                sql_return_clock = list(map(lambda x: x[1], mutil_trend_data))
                for key_clock in full_clock:
                    try:
                        sql_return_clock.index(key_clock)
                    except:
                        mutil_trend_data.append((itemid, key_clock, None, None, None))
                mutil_trend_data.sort(key=lambda x: x[1], reverse=False)

            for ii in range(0, len(mutil_trend_data)):
                # for itemid, clock, min_value, avg_value in mutil_his_data:
                itemid, clock, min_value, avg_value, max_value = mutil_trend_data[ii]
                ob = {
                    'zbx_min_value': min_value,
                    'zbx_avg_value': avg_value,
                    'zbx_max_value': max_value,
                    'clock': clock
                }
                if str(_key) in itemid_iteminfo[itemid]['trend_value'].keys():
                    itemid_iteminfo[itemid]['trend_value'][str(_key)].append(ob)
                else:
                    itemid_iteminfo[itemid]['trend_value'][str(_key)] = [ob]

                    # value_map = get_value_mappings(zbx_session=zbx_session, zbx_db=zbx_db)

    for itemid, item in itemid_iteminfo.items():
        # convert value by value map
        # item_key = item.pop('zbx_item_key')

        cmdb_host_info[lower_hostname_map[item['zbx_hostname'].lower()]]['item'] = item

        # request time range data

    return cmdb_host_info, total_host
