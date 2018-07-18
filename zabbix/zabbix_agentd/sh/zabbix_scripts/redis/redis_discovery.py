#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
file = '/tmp/.redis.list'
f = open(file, 'r')
l = []
for row in f:
    if row[0] == '#':
        continue
    if len(row.strip(" ").split(" ")) < 3:
        continue
    else:
        (name, ip, port) = row.split(" ")[0:3]
        dict = {"{#REDISNAME}": name, "{#REDISIP}": ip, "{#REDISPORT}": port.strip('\n')}
        if l.count(dict) == 0:
            l.append(dict)

mydict = {"data": l}

print json.dumps(mydict, sort_keys=True, indent=3, ensure_ascii=False)
