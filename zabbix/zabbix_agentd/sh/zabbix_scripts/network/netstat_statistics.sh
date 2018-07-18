#!/bin/bash

tmp_file=/tmp/.netstat_statistics.log

if [ $1 == 'create_stat_file' ];then
        netstat -s > $tmp_file && echo 0 || echo 1
else
        cat $tmp_file| grep "$*" | awk '{print $1}'
fi
