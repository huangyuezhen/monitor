#!/bin/bash 

procname=$1
flag=$2
if [[ $procname == tomcat ]];then
    procname=tomcat/
elif [[ $procname == tomcat8030 ]];then
    procname=tomcat8030/
fi

mem() {
        if [[ $procname == "tomcat/" ]]||[[ $procname == "tomcat8030/" ]];then
            proc_mem=`ps aux|grep "java.*local/$procname"|grep -v grep|awk '{print $6}'`
        else 
                proc_mem=`ps aux|grep "app=$procname"|grep -v grep|awk '{print $6}'`
        fi
    if [[ "$proc_mem" == "" ]];then
        proc_mem=0
    fi
    echo $proc_mem
    #return $proc_mem
    }

cnt() {
        if [[ $procname == "tomcat/" ]]||[[ $procname == "tomcat8030/" ]];then
        proc_cnt=`ps aux|grep "java.*local/$procname"|grep -v grep|wc -l`
        else 
                proc_cnt=`ps aux|grep "app=$procname"|grep -v grep|wc -l`
        fi
    if [[ "$proc_cnt" == "" ]];then
        proc_cnt=0
    fi
    echo $proc_cnt
    #return $proc_cnt
    }

cpu() {
        if [[ $procname == "tomcat/" ]]||[[ $procname == "tomcat8030/" ]];then
                proc_cpu=`ps aux|grep "java.*local/$procname"|grep -v grep|awk '{print \$3}'`
        else 
            proc_cpu=`ps aux|grep "app=$procname"|grep -v grep|awk '{print \$3}'`
        fi
    if [[ "$proc_cpu" == "" ]];then
        proc_cpu=0.0
    fi
    echo $proc_cpu
    #return "$proc_cpu"
    }

case $flag in 
   mem)
   mem
   ;;
   cnt)
   cnt
   ;;
   cpu)
   cpu
   ;;
   *)
   echo "Parameters  Error {mem|cnt|cpu}"
esac
