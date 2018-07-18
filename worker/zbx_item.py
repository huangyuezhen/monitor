import re
from sqlalchemy import func, or_
from db.monitor_center import MC


def get_mutil_history_time_range_raw(zbx_db, zbx_engine, itemids, value_type, start_clock, end_clock, interval_type):
    _sql = """
SELECT 
    itemid, clock  , min(`value`) min, avg(`value`) avg, max(`value`) max,
    FLOOR(({end_clock} - clock) / {interval_time}) AS time_diff
FROM
    {table_name}
WHERE
    clock BETWEEN {start_clock} AND {end_clock} and itemid in({items})
GROUP BY itemid,time_diff
ORDER BY clock
    """

    value_type_table = {
        0: 'history',
        3: 'history_uint',
    }
    # 统计间隔
    # 1-2h: 120s
    # 3-6h : 300s
    # 6-12h : 900s
    # 12h - 1d 1500s
    # >1d :3600

    interval_type_table = {0: 120, 1: 300, 2: 900, 3: 1500, 4: 3600}
    if value_type not in value_type_table.keys():
        return

    history_table = value_type_table[value_type]
    interval_time = interval_type_table[interval_type]
    itemids = map(str, itemids)
    _sql = _sql.format(
        table_name=history_table,
        items=','.join(itemids),
        start_clock=str(start_clock),
        end_clock=str(end_clock),
        interval_time=str(interval_time))
    res = zbx_db.sql_find(engine=zbx_engine, _sql=_sql, page_size=9999999)
    return res


def get_history_time_range_raw(zbx_db, zbx_engine, itemids, value_type, start_clock, end_clock):
    _sql = """
SELECT
    h.itemid, min(`value`) min, avg(`value`) avg, max(`value`) max
FROM
    `items` i
JOIN
    {table_name} h 
ON
    h.itemid = i.itemid
WHERE
    h.itemid IN ({items})
    and h.clock >= {start_clock}
    and h.clock <= {end_clock}
GROUP BY
    h.itemid
    """
    value_type_table = {
        0: 'history',
        1: 'history_str',
        2: 'history_log',
        3: 'history_uint',
        4: 'history_text',
    }
    history_table = value_type_table[value_type]
    itemids = map(str, itemids)
    _sql = _sql.format(
        table_name=history_table, items=','.join(itemids), start_clock=str(start_clock), end_clock=str(end_clock))
    res = zbx_db.sql_find(engine=zbx_engine, _sql=_sql, page_size=9999999)
    return res


def get_history_lastdata_raw(zbx_db, zbx_engine, itemids, value_type):
    _sql = """
SELECT 
    itemid, `value`, clock
FROM
    (
    SELECT
        *
    FROM
        {table_name} h
    WHERE
        h.itemid IN ({items})
        and h.clock >= UNIX_TIMESTAMP(DATE_SUB(now(),INTERVAL 5 MINUTE))
        and h.clock <= UNIX_TIMESTAMP(now())
    ORDER BY
        h.clock DESC
    ) h
GROUP BY
    h.itemid
    """
    value_type_table = {
        0: 'history',
        1: 'history_str',
        2: 'history_log',
        3: 'history_uint',
        4: 'history_text',
    }
    history_table = value_type_table[value_type]
    itemids = map(str, itemids)
    _sql = _sql.format(table_name=history_table, items=','.join(itemids))
    res = zbx_db.sql_find(engine=zbx_engine, _sql=_sql, page_size=9999999)
    return res


def get_interval_type(start_clock, end_clock):
    # print('end_clock - start_clock is{}'.format(end_clock - start_clock))
    if (end_clock - start_clock) < 7201:
        return 0
    if (end_clock - start_clock) < 6 * 3600 + 1:
        return 1
    if (end_clock - start_clock) < 12 * 3600 + 1:
        return 2
    if (end_clock - start_clock) < 24 * 3600 + 1:
        return 3
    if (end_clock - start_clock) > 24 * 3600 + 1:
        return 4


def get_problem_trigger_raw(zbx_session, zbx_db, item_ids=()):
    filter_args = []
    limit_offset = 0
    limit_count = 999999999

    triggers = zbx_db.triggers
    functions = zbx_db.functions
    items = zbx_db.items
    events = zbx_db.events

    select_col = (
        triggers.triggerid.label('zbx_trigger_id'),
        triggers.description.label('zbx_trigger_description'),
        triggers.priority.label('zbx_trigger_priority'),
        items.itemid.label('zbx_item_id'),
    )

    join_tables = (
        [functions],
        [items],
        [events, triggers.triggerid == events.objectid],
    )

    filter_args.append(events.object == 0)
    filter_args.append(triggers.value == 1)
    filter_args.append(triggers.status == 0)

    if item_ids:
        if len(item_ids) == 1:
            filter_args.append(items.itemid == item_ids[0])
        else:
            filter_args.append(items.itemid.in_(item_ids))

    group_by = (triggers.triggerid, )

    order_by = triggers.lastchange

    desc = True

    db_res, count = zbx_db.join_query(
        session=zbx_session,
        join_tables=join_tables,
        select_col=select_col,
        filter_args=filter_args,
        order_by=order_by,
        desc=desc,
        group_by=group_by,
        limit_offset=limit_offset,
        limit_count=limit_count)
    return db_res, count


def get_items_raw(zbx_session,
                  zbx_db,
                  host_list=(),
                  item_app_names=(),
                  item_keys=(),
                  order_by=None,
                  desc=False,
                  limit_offset=0,
                  limit_count=15):
    filter_args = []

    items = zbx_db.items
    hosts = zbx_db.hosts
    applications = zbx_db.applications
    items_applications = zbx_db.items_applications

    join_tables = ([hosts], )
    left_join_tables = (
        [items_applications],
        [applications],
    )
    group_by = (items.itemid, )

    select_col = (
        items.itemid.label('zbx_item_id'),
        items.name.label('zbx_item_name'),
        items.key_.label('zbx_item_key'),
        items.state.label('zbx_item_state'),
        items.error.label('zbx_item_error'),
        items.units.label('zbx_item_units'),
        items.multiplier.label('zbx_item_multiplier'),
        items.formula.label('zbx_item_formula'),
        items.value_type.label('zbx_item_value_type'),
        items.valuemapid.label('zbx_item_valuemapid'),
        hosts.host.label('zbx_hostname'),
        hosts.status.label('zbx_host_status'),
        func.group_concat(applications.name).label('zbx_application_name'),
    )

    # filter host
    filter_args.append(hosts.status.in_([0, 1]))
    if host_list:
        if len(host_list) == 1:
            filter_args.append(hosts.host == host_list[0])
        else:
            filter_args.append(hosts.host.in_(host_list))

    # filter item application
    if item_app_names:
        if len(item_app_names) == 1:
            filter_args.append(applications.name == item_app_names[0])
        else:
            filter_args.append(applications.name.in_(item_app_names))

    # filter item
    filter_args.append(items.status == 0)
    filter_args.append(items.flags.in_([0, 4]))
    if item_keys:
        if len(item_keys) == 1:
            filter_args.append(items.key_ == item_keys[0])
        else:
            filter_args.append(items.key_.in_(item_keys))
    db_res, count = zbx_db.join_query(
        session=zbx_session,
        join_tables=join_tables,
        left_join_tables=left_join_tables,
        select_col=select_col,
        filter_args=filter_args,
        order_by=order_by,
        desc=desc,
        group_by=group_by,
        limit_offset=limit_offset,
        limit_count=limit_count)

    return db_res, count


def get_value_mappings(zbx_session, zbx_db):
    res = {}
    db_res = zbx_db.find(zbx_session, zbx_db.mappings, 1, 99999, return_query=True).all()
    for row in db_res:
        valuemap = res.setdefault(row.valuemapid, {})
        valuemap[row.value] = row.newvalue
    return res


def get_item_key_by_name(mc_session, name):
    _id = mc_session.query(MC.item_groups.id).filter_by(name=name).first()[0]
    q = mc_session.query(MC.items.key).filter_by(mc_item_groups_id=_id).all()
    q = [i[0] for i in q]
    return q


def get_items(zbx_session,
              zbx_db,
              cmdb_host_info,
              application_name=(),
              item_keys=(),
              order_by=None,
              desc=False,
              page=1,
              page_size=9999999,
              last_value=False,
              zbx_engine=None,
              problem_trigger=False,
              time_range_value=False,
              start_clock=None,
              end_clock=None,
              mutil_history_value=False,
              trend_value=False):
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
    if time_range_value or mutil_history_value:
        assert start_clock and end_clock, "time range value need to use start_clock and end_clock argument."
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
        if last_value or time_range_value or mutil_history_value:
            item['zbx_last_value'] = ""
            item['zbx_last_clock'] = ""
            item['zbx_min_value'] = ""
            item['zbx_avg_value'] = ""
            item['zbx_max_value'] = ""
            history_items = history_type_itemids.setdefault(item['zbx_item_value_type'], [])
            history_items.append(item['zbx_item_id'])
        # itemid iteminfo dict
        if last_value or problem_trigger or time_range_value or mutil_history_value:
            itemid_iteminfo[item['zbx_item_id']] = item
        else:
            item_key = item.pop('zbx_item_key')
            cmdb_host_info[lower_hostname_map[item['zbx_hostname'].lower()]]['zbx_items'][item_key] = item

    if last_value or time_range_value or mutil_history_value:
        assert zbx_engine, "last_value and time range value need to use zbx_engine argument."
        for history_type, itemids in history_type_itemids.items():
            # request last data
            if last_value:
                last_data = get_history_lastdata_raw(
                    zbx_db=zbx_db, zbx_engine=zbx_engine, value_type=history_type, itemids=itemids)
                for itemid, last_v, last_clock in last_data:
                    itemid_iteminfo[itemid]['zbx_last_value'] = last_v
                    itemid_iteminfo[itemid]['zbx_last_clock'] = last_clock

            # request time range value
            if time_range_value:
                time_range_data = get_history_time_range_raw(
                    zbx_db=zbx_db,
                    zbx_engine=zbx_engine,
                    value_type=history_type,
                    itemids=itemids,
                    start_clock=start_clock,
                    end_clock=end_clock)
                for itemid, min_value, avg_value, max_value in time_range_data:
                    itemid_iteminfo[itemid]['zbx_min_value'] = min_value
                    itemid_iteminfo[itemid]['zbx_avg_value'] = avg_value
                    itemid_iteminfo[itemid]['zbx_max_value'] = max_value
            if mutil_history_value:
                interval_type = get_interval_type(start_clock, end_clock)
                mutil_his_data = get_mutil_history_time_range_raw(
                    zbx_db=zbx_db,
                    zbx_engine=zbx_engine,
                    value_type=history_type,
                    itemids=itemids,
                    start_clock=start_clock,
                    end_clock=end_clock,
                    interval_type=interval_type)
                if mutil_his_data:
                    for ii in range(0, len(mutil_his_data)):
                        # for itemid, clock, min_value, avg_value in mutil_his_data:
                        itemid, clock, min_value, avg_value, max_value, time_diff = mutil_his_data[ii]
                        ob = {
                            'zbx_min_value': min_value,
                            'zbx_avg_value': avg_value,
                            'zbx_max_value': max_value,
                            'clock': clock
                        }
                        if 'values' in itemid_iteminfo[itemid].keys():
                            itemid_iteminfo[itemid]['values'].append(ob)
                        else:
                            itemid_iteminfo[itemid]['values'] = [ob]
            # if trend_value :

        value_map = get_value_mappings(zbx_session=zbx_session, zbx_db=zbx_db)

    # request time range data

    if last_value or problem_trigger or (start_clock and end_clock):
        # request item trigger status
        if problem_trigger:
            itemid_triggers = {}
            trigger_res_label = (
                'zbx_trigger_id',
                'zbx_trigger_description',
                'zbx_trigger_priority',
            )
            db_res, total_trigger = get_problem_trigger_raw(zbx_session, zbx_db, itemid_iteminfo.keys())
            for row in db_res:
                trigger = {}
                trigger.update({k: row.__getattribute__(k) for k in trigger_res_label})
                itemid_trigger = itemid_triggers.setdefault(row.zbx_item_id, [])
                itemid_trigger.append(trigger)

        for itemid, item in itemid_iteminfo.items():
            # convert value by value map
            if last_value or time_range_value:
                item_valuemapid = item['zbx_item_valuemapid']
                if item_valuemapid:
                    if last_value:
                        item_last_value = item['zbx_last_value']
                        if item_last_value:
                            item['zbx_last_value'] = value_map[item_valuemapid][str(item_last_value)]
                    if time_range_value:
                        item_min_value = item['zbx_min_value']
                        item_avg_value = item['zbx_avg_value']
                        item_max_value = item['zbx_max_value']
                        if item_min_value:
                            try:
                                item_min_value = int(item_min_value)
                            except ValueError:
                                pass
                            item['zbx_min_value'] = value_map[item_valuemapid][str(item_min_value)]
                        if item_avg_value:
                            try:
                                item_avg_value = int(item_avg_value)
                            except ValueError:
                                pass
                            item['zbx_avg_value'] = value_map[item_valuemapid][str(item_avg_value)]
                        if item_max_value:
                            try:
                                item_max_value = int(item_max_value)
                            except ValueError:
                                pass
                            item['zbx_max_value'] = value_map[item_valuemapid][str(item_max_value)]

            if problem_trigger:
                item['zbx_triggers'] = itemid_triggers.get(item['zbx_item_id'], [])
            item_key = item.pop('zbx_item_key')
            cmdb_host_info[lower_hostname_map[item['zbx_hostname'].lower()]]['zbx_items'][item_key] = item

    return cmdb_host_info, total_host


# TODO: 暂时不能多个zabbix一起获取
# def get_env_items(zbx_sessions, cmdb_host_info, env_list=(), item_app_names=(), item_key=None, host_order_by=None,
#                   host_desc=False, item_order_by=None, item_desc=False, last_value=True):
#     res_hosts = []
#     total_hosts_count = 0
#     total_items_count = 0
#
#     # cmdb_env to zbxdb_env
#     if env_list:
#         env_list = (settings['cmdb_to_zbxdb_env_map'][e] for e in env_list)
#     else:
#         env_list = ZABBIX.keys()
#
#     for env in env_list:
#         host_items, count = get_items(
#             zbx_session=zbx_sessions[env],
#             zbx_db=ZABBIX[env],
#             cmdb_host_info=cmdb_host_info,
#             item_app_names=item_app_names,
#             item_key=item_key,
#             order_by=item_order_by,
#             desc=item_desc,
#             last_value=last_value,
#             zbx_engine=mysql.ENGINES[env]
#         )
#         res_hosts.extend(host_items.values())
#         total_hosts_count += len(host_items.keys())
#         total_items_count += count
#
#     # sort
#     # if len(res_hosts) > 0:
#     #     if host_order_by not in res_hosts[0]:
#     #         host_order_by = 'cmdb_business_group'
#     #     if isinstance(res_hosts[0][host_order_by], (list, tuple)):
#     #         res_hosts = sorted(res_hosts, key=lambda d: d[host_order_by][0], reverse=host_desc)
#     #     else:
#     #         res_hosts = sorted(res_hosts, key=lambda d: d[host_order_by], reverse=host_desc)
#
#     return res_hosts, total_hosts_count, total_items_count


def _convert_item_name_variable(item_name, item_key):
    name_var_prog = re.compile(r'\$\d+')
    name_vars = name_var_prog.findall(item_name)
    if name_vars:
        item_key_args = _zbx_itemkey_args(item_key)
        if item_key_args:
            for index, key_arg in enumerate(item_key_args, start=1):
                item_name = item_name.replace('$%s' % index, key_arg)

    return item_name


def _zbx_itemkey_args(item_key):
    key_args = []
    if '[' in item_key:
        key_args = item_key.split('[', maxsplit=1)[1].rsplit(']', maxsplit=1)[0]
        key_args = [s.strip().strip('"').strip("'") for s in key_args.split(',')]

    return key_args


def get_item_key(zbx_session, zbx_db, like=None):
    res = []
    items = zbx_db.items

    q = zbx_session.query(items.name, items.key_).group_by(items.key_)
    if like:
        like_str = "%{}%".format(like)
        q = q.having(or_(items.name.like(like_str), items.key_.like(like_str)))

    db_res = q.all()
    total_count = q.count()
    for row in db_res:
        res.append({'key': row.key_, 'name': _convert_item_name_variable(row.name, row.key_)})
    return res, total_count


def test():
    from db.zabbix import ZABBIX
    from db.mysql import SESSIONS
    from db.mysql import connect_all
    connect_all()
    sess = SESSIONS['local_zabbix']
    sess = sess()
    db = ZABBIX['local_zabbix']

    # print(get_problem_trigger_raw(sess, db))
    res = get_item_key(sess, db, 'mq')
    print(res)


if __name__ == '__main__':
    test()
