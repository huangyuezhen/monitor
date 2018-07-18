#!/bin/bash
#
# activemq-zabbix
#
cd "$(dirname "$0")"
. $(dirname "$0")/.auth

if [[ -z "$HOSTNAME" ]]; then
    HOSTNAME=`hostname`
fi
if [[ -z "$NODE" ]]; then
    NODE=`hostname`
fi

#./activemq.py --username=$USERNAME --password=$PASSWORD --check=list_queues --conf=$CONF --hostname=$HOSTNAME --loglevel=${LOGLEVEL} --logfile=${LOGFILE} 
if [ ! -z $1 ];then
 if [ $1 = "discovery" ];then
  ./activemq.py --username=$USERNAME --password=$PASSWORD --check=list_queues --hostname=$HOSTIP --loglevel=${LOGLEVEL} --logfile=${LOGFILE}
 elif [ $1 = "check_health" ];then
  ./activemq.py --username=$USERNAME --password=$PASSWORD --check=check_health --hostname=$HOSTIP --loglevel=${LOGLEVEL} --logfile=${LOGFILE}
 elif [ $1 = "queues" ];then
  ./activemq.py --username=$USERNAME --password=$PASSWORD --conf=$CONF --check=queues --hostname=$HOSTIP --loglevel=${LOGLEVEL} --logfile=${LOGFILE}
 else
  ./activemq.py --username=$USERNAME --password=$PASSWORD --check=server --metric=$1 --hostname=$HOSTIP --loglevel=${LOGLEVEL} --logfile=${LOGFILE}
 fi
fi
