#!/bin/bash
#name:yong02.tang
#Version Number:1.0
#Language:bash shell
#Use:install tcp_status
#Date:2017-9-8
[ $# -ne 1 ] && echo "Usage:CLOSE-WAIT|CLOSED|CLOSING|ESTAB|FIN-WAIT-1|FIN-WAIT-2|LAST-ACK|LISTEN|SYN-RECV SYN-SENT|TIME-WAIT" && exit 1
tcp_status_fun(){
    TCP_STAT=$1
    TCP_STAT_VALUE=`/usr/sbin/ss -ant | awk 'NR>1 {++s[$1]} END {for(k in s) print k,s[k]}' |grep $1 |awk '{print $2}'`
    if [ -z "$TCP_STAT_VALUE" ];then
        TCP_STAT_VALUE=0
    fi
    	echo $TCP_STAT_VALUE
}
tcp_status_fun $1;
