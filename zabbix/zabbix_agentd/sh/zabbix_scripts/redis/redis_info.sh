#!/bin/bash
HOSTIP=$1
PORT=$2
ITEM=$3

if [ $1 == 'discovery' ];then
  python $(dirname "$0")/redis_discovery.py
  exit
fi
#echo `date`,$HOSTIP,$PORT,$ITEM >> /tmp/redis.log
cmdpath=`whereis redis-cli | awk '{print $2}'`
if [ ! -f $cmdpath ];then
  echo "redis-cli: command not found"
  exit
fi
PASSWORD=`grep -v ^# /tmp/.redis.list | grep $HOSTIP | grep $PORT | awk '{print $4}'`
#print $PASSWORD
if [ -z $PASSWORD ];then
  if [ $ITEM = 'ping' ];then
    $cmdpath -h $HOSTIP -p $PORT ping
    #echo "redis-cli -h $HOSTIP -p $port ping" >> /tmp/redis.log
  else
    $cmdpath -h $HOSTIP -p $PORT info | grep $ITEM | cut -d : -f2
  fi
else
  if [ $ITEM = 'ping' ];then
    $cmdpath -h $HOSTIP -p $PORT -a $PASSWORD ping
  else
    $cmdpath -h $HOSTIP -p $PORT -a $PASSWORD info | grep $ITEM | cut -d : -f2
  fi
fi                             
