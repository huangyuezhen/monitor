#!/bin/bash

ifname=$1
ifstat=$2

if [ -f /sbin/ethtool ];then
        :
else
        exit 2
fi

if [ $ifname = "gb1" ];then
        if [ -f  /etc/sysconfig/network-scripts/ifcfg-em1 ];then
                ifname=em1
        else
                ifname=eth0
        fi
elif [ $ifname = "gb2" ];then
        if [ -f  /etc/sysconfig/network-scripts/ifcfg-em2 ];then
                ifname=em2
        else
                ifname=eth1
        fi
elif [ $ifname = "gb3" ];then
        if [ -f  /etc/sysconfig/network-scripts/ifcfg-em3 ];then
                ifname=em3
        else
                ifname=eth2
        fi
elif [ $ifname = "gb4" ];then
        if [ -f  /etc/sysconfig/network-scripts/ifcfg-em4 ];then
                ifname=em4
        else
                ifname=eth3
        fi
else
        exit 3
fi

sudo /sbin/ethtool $ifname | grep $ifstat  | awk -F: '{print $2}'
