#!/bin/bash
# backup log 
logFile=/home/backup/innobackup/backup.log
status=`tail -n1 ${logFile} | grep -i "success"`
if [ -n "${status}" ]; then 
  echo 1
else 
  echo 0
fi

