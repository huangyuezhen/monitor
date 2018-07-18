#!/bin/bash
#
# https://github.com/jasonmcintosh/rabbitmq-zabbix
#
SHELL_DIR=$(cd `dirname $0`;pwd)
${SHELL_DIR}/appinfo.py -l --conf='/data/conf/zabbix-agentd/zabbix_agentd.conf' --logfile='/data/logs/zabbix-agentd/appinfo_zabbix.log' --loglevel=${LOGLEVEL}
