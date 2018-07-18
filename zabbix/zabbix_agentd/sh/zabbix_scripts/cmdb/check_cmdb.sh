#!/bin/bash


cmdb() {

        CMDB_AGENT=`ps -ef | grep $1.py | grep -v 'grep' | wc -l`

        if [ $CMDB_AGENT -eq 1 ];then
                echo 1
        else
                echo 0
        fi
}

cmdb $1
