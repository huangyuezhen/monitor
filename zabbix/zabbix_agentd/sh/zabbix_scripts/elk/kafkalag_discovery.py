#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import sys
import os
import commands
var = os.popen("/home/product/local/kafka/bin/kafka-run-class.sh kafka.tools.ConsumerOffsetChecker --group logstash --topic saofu --zookeeper localhost:2181 2>/dev/null |grep ^logstash | grep -v ^$ | awk '{print $2$3 }'").readlines()
l = []
dict = {}
for i in range(len(var)):
    dict={"{#NAME}": var[i].split("\n")[0] }
    l.append(dict)
   
#print l
mydict = {"data": l}
print json.dumps(mydict, sort_keys=True, indent=3,)
