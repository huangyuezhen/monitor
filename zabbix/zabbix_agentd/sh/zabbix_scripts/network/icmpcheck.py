#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
icmpcheck list file : /tmp/.icmpcheck.list
'''
import json
file = '/tmp/.icmpcheck.list'
f = open(file, 'r')
l = []
for row in f:
    if row[0] == '#':
        continue
#    if len(row.split(" ")) < 3:
#        continue
    else:
        dest = row.split(" ")[0]
        dict = {"{#TARGET}": dest.strip("\n")}
        if l.count(dict) == 0:
            l.append(dict)

mydict = {"data": l}

print json.dumps(mydict, sort_keys=True, indent=3, ensure_ascii=False)

