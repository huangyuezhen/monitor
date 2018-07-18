#!/bin/bash
#
# https://github.com/jasonmcintosh/rabbitmq-zabbix
#
PORT=$1
APPNAME=$2

SHELL_DIR=$(cd `dirname $0`;pwd)
${SHELL_DIR}/appinfo.py --check --conf='/data/conf/zabbix-agentd/zabbix_agentd.conf' --logfile='/data/logs/zabbix-agentd/appinfo_zabbix.log' --loglevel=  --port=${PORT} --appname=${APPNAME}
