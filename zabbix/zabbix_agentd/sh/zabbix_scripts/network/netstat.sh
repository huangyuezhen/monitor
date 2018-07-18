#!/bin/bash

if [ $# -lt 1 ];then
        echo -2
        exit
fi

statsfile=/tmp/netstat_stats.txt
type=$1

find /tmp/ -cmin -1 | grep netstat_stats.txt >>/dev/null
if [ $? -eq 0 ];then
:
else
        /usr/sbin/ss | awk '{print $1}'  | sort | uniq -c >$statsfile  || echo -1
fi

cat $statsfile | grep "$type"  >>/dev/null
if [ $? -eq 0 ];then
        cat $statsfile | grep "$type" |  awk '{print $1}'
else
        echo 0
fi
