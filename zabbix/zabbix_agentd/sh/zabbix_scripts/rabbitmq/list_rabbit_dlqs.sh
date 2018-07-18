#!/bin/bash
#
# https://github.com/jasonmcintosh/rabbitmq-zabbix
#
cd "$(dirname "$0")"
. .rab.auth

if [[ -z "$HOSTNAME" ]]; then
    HOSTNAME=`hostname`
fi
if [[ -z "$NODE" ]]; then
    NODE=`hostname`
fi

METRIC=$1

./api.py --username=$USERNAME --password=$PASSWORD --check=list_dlq_queues --filter="$FILTER" --metric=$METRIC --conf=$CONF --hostname=$HOSTNAME --node="$NODE"  --loglevel=${LOGLEVEL} --logfile=${LOGFILE} --port=$PORT --protocol=$PROTOCOL
