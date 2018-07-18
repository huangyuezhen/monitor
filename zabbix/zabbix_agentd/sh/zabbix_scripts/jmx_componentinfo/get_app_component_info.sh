#!/bin/bash
#
# https://github.com/jasonmcintosh/rabbitmq-zabbix
#
PORT=$1
APPNAME=$2 
KEY=$3

SHELL_DIR=$(cd `dirname $0`;pwd)
${SHELL_DIR}/appinfo.py --conf='/data/conf/zabbix-agentd/zabbix_agentd.conf' \
             --logfile='/data/logs/zabbix-agentd/appinfo_zabbix.log' \
             --loglevel=${LOGLEVEL} \
             --get-component \
             --port="${PORT}" \
             --appname="${APPNAME}" \
             --key="${KEY}"
