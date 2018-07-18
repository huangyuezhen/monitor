import sys
sys.path.append('.')
from db import mysql
import random


def insert_key_history(engine, item_key, value=None, random_start=1, random_end=99):
    value_type_table = {
        0: 'history',
        1: 'history_str',
        2: 'history_log',
        3: 'history_uint',
        4: 'history_text',
    }

    sel_sql = """
SELECT
i.itemid, i.value_type
FROM
items i
JOIN `hosts` h
ON h.hostid = i.hostid
WHERE
i.key_ = '%s'
AND h.status != 3
    """ % item_key

    insert_sql = """
insert %s (itemid, clock, value, ns) values (%s, unix_timestamp(now()), %s, 100000)
    """

    print(sel_sql)
    res = engine.execute(sel_sql)
    output = res.fetchall()
    for row in output:
        itemid = row[0]
        value_type = row[1]
        if value is None:
            if value_type == 0:
                ivalue = random.uniform(random_start, random_end)
            else:
                ivalue = random.randint(random_start, random_end)
        else:
            ivalue = value
        sql = insert_sql % (value_type_table[value_type], itemid, ivalue)
        print(sql)
        engine.execute(sql)
    res.close()


def main():
    import requests
    from conf import settings
    import sys

    if len(sys.argv) > 1:
        item_group = sys.argv[1]
    else:
        item_group = 'default'

    port = settings['server']['port']
    res = requests.get('http://localhost:' + str(port) + '/api/item_group', params={'name': item_group})
    items = res.json()['res'][0]['items']
    key_list = [i['key'] for i in items]
    value = None
    random_start = 80
    random_end = 99

    engine = mysql.ENGINES['local_zabbix']
    while True:
        for key in key_list:
            insert_key_history(engine, key, value=value, random_start=random_start, random_end=random_end)


if __name__ == '__main__':
    main()
