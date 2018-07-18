#!/bin/bash

mysqladmin_con="/usr/local/mysql/bin/mysqladmin" 
mysql_con="/usr/local/mysql/bin/mysql"

if [ $# -ne 1 ];then
echo "arg error!"
fi

case $1 in
#从应用程序的角度观测，数据库响应速度=网络延时+响应延时，其中响应延时从请求抵达数据库服务器开始，到服务器将响应结果发出结束。
#响应延时是衡量数据库性能最重要的指标之一，而tcprstat是专门统计响应延时的工具，当应用出现性能问题时可快速排查是否为数据库导致的。
#准备工作：
#cp -a tcprstat /usr/bin/tcprstat
#chmod +x /usr/bin/tcprstat
ResponseTime)
#result=`sudo /usr/bin/tcprstat -p 3306 -t 1 -n 1 -l 10.13.6.183 | cut -f9 | tail -1`
result=`sudo /usr/bin/tcprstat -p 3306 -t 1 -n 1 | cut -f9 | tail -1`
echo $result
;;
Ping)
#result=`${mysqladmin_con} ping | grep -c alive`
result=`ps aux|grep -v grep|grep -c mysqld_safe`
echo $result
;;
DB_size)
#result=`sudo du -sm /home/mysql/data/* | grep saofu | awk '{print $1}'`
#result=`${mysql_con} -Ns -e 'select sum((DATA_LENGTH+INDEX_LENGTH)) as DBSIZE from information_schema.TABLES where table_schema="saofu"'`
result=`${mysql_con} -Ns -e 'select sum((DATA_LENGTH+INDEX_LENGTH)) as DBSIZE from information_schema.TABLES'`
echo $result
;;
Long_sql)
#result=`${mysql_con} -e "show full processlist" | grep Query | awk 'BEGIN{if($6>=600){print "1"} else if($6<600){print "0"}}' | tail -1`
result=`${mysql_con} -Ns -e 'select time from information_schema.processlist where Command ="Query" order by time desc limit 1'`
echo $result
;;
Version)
result=`${mysql_con} -V`
echo $result
;;
Uptime)
result=`${mysqladmin_con} status |awk -F "[ :]+" '{print $2}'`
echo $result
;;
Com_update)
result=`${mysqladmin_con} extended-status|grep -w "Com_update"|cut -d"|" -f3`
echo $result
;;
Slow_queries)
result=`${mysqladmin_con} status|cut -f5 -d":"|cut -f1 -d"O"`
echo $result
;;
Com_select)
result=`${mysqladmin_con} extended-status|grep -w "Com_select"|cut -f3 -d"|"`
echo $result
;;
Com_rollback)
result=`${mysqladmin_con} extended-status|grep -w "Com_rollback"|cut -f3 -d"|"`
echo $result
;;
Questions)
result=`${mysqladmin_con} status|cut -f4 -d":"|cut -f1 -d"S"`
echo $result
;;
Transactions)
c_rollback=`${mysqladmin_con} extended-status|grep -w "Com_rollback"|cut -f3 -d"|"`
c_commit=`${mysqladmin_con} extended-status |grep -w "Com_commit"|cut -d"|" -f3`
result=$[c_rollback+c_commit]
echo $result
;;
Innodb_buffer_read_hits)
reads=`${mysqladmin_con} extended-status |grep -w "Innodb_buffer_pool_reads"|cut -d"|" -f3`
requests=`${mysqladmin_con} extended-status |grep -w "Innodb_buffer_pool_read_requests"|cut -d"|" -f3`
result=$(printf "%.2f" `echo "scale=2;( 1 - $reads / $requests) * 100"|bc`)
echo $result
;;
Innodb_buffer_usage)
pages_free=`${mysqladmin_con} extended-status |grep -w "Innodb_buffer_pool_pages_free"|cut -d"|" -f3`
pages_total=`${mysqladmin_con} extended-status |grep -w "Innodb_buffer_pool_pages_total"|cut -d"|" -f3`
result=$(printf "%.2f" `echo "scale=2;( 1 - $pages_free / $pages_total ) * 100"|bc`)
echo $result
;;
Innodb_buffer_wait)
result=`${mysqladmin_con} extended-status |grep -w "Innodb_buffer_pool_wait_free"|cut -d"|" -f3`
echo $result
;;
Innodb_buffer_dirty_ratio)
pages_dirty=`${mysqladmin_con} extended-status |grep -w "Innodb_buffer_pool_pages_dirty"|cut -d"|" -f3`
pages_total=`${mysqladmin_con} extended-status |grep -w "Innodb_buffer_pool_pages_total"|cut -d"|" -f3`
result=$(printf "%.2f" `echo "scale=2;(pages_dirty / $pages_total) * 100"|bc`)
echo $result
;;
D_pending_fsyncs)
result=`${mysqladmin_con} extended-status |grep -w "Innodb_data_pending_fsyncs"|cut -d"|" -f3`
echo $result
;;
D_pending_reads)
result=`${mysqladmin_con} extended-status |grep -w "Innodb_data_pending_reads"|cut -d"|" -f3`
echo $result
;;
D_pending_writes)
result=`${mysqladmin_con} extended-status |grep -w "Innodb_data_pending_writes"|cut -d"|" -f3`
echo $result
;;
Log_waits)
result=`${mysqladmin_con} extended-status |grep -w "Innodb_log_waits"|cut -d"|" -f3`
echo $result
;;
Log_pending_fsyncs)
result=`${mysqladmin_con} extended-status |grep -w "Innodb_os_log_pending_fsyncs"|cut -d"|" -f3`
echo $result
;;
Log_pending_writes)
result=`${mysqladmin_con} extended-status |grep -w "Innodb_os_log_pending_writes"|cut -d"|" -f3`
echo $result
;;
Log_written)
result=`${mysqladmin_con} extended-status |grep -w "Innodb_os_log_written"|cut -d"|" -f3`
echo $result
;;
Com_insert)
result=`${mysqladmin_con} extended-status |grep -w "Com_insert"|cut -d"|" -f3`
echo $result
;;
Com_delete)
result=`${mysqladmin_con} extended-status |grep -w "Com_delete"|cut -d"|" -f3`
echo $result
;;
Com_commit)
result=`${mysqladmin_con} extended-status |grep -w "Com_commit"|cut -d"|" -f3`
echo $result
;;
RW_ratio)
c_select=`${mysqladmin_con} extended-status|grep -w "Com_select"|cut -f3 -d"|"`
c_insert=`${mysqladmin_con} extended-status |grep -w "Com_insert"|cut -d"|" -f3`
c_delete=`${mysqladmin_con} extended-status |grep -w "Com_delete"|cut -d"|" -f3`
c_update=`${mysqladmin_con} extended-status|grep -w "Com_update"|cut -d"|" -f3`
# result=$[c_select/(c_insert+c_delete+c_update)]
result=$(printf "%.2f" `echo "scale=2;$c_select/($c_insert+$c_delete+$c_update)"|bc`)
echo $result
;;
Bytes_sent)
result=`${mysqladmin_con} extended-status |grep -w "Bytes_sent" |cut -d"|" -f3`
echo $result
;;
Bytes_received)
result=`${mysqladmin_con} extended-status |grep -w "Bytes_received" |cut -d"|" -f3`
echo $result
;;
Com_begin)
result=`${mysqladmin_con} extended-status |grep -w "Com_begin"|cut -d"|" -f3`
echo $result
;;
Threads_connected)
result=`${mysqladmin_con} extended-status |grep -w "Threads_connected"|cut -d"|" -f3`
echo $result
;;
Threads_running)
result=`${mysqladmin_con} extended-status |grep -w "Threads_running"|cut -d"|" -f3`
echo $result
;;
Innodb_row_lock_current_waits)
result=`${mysqladmin_con} extended-status |grep -w "Innodb_row_lock_current_waits"|cut -d"|" -f3`
echo $result 
;;
*)
echo "Usage:$0(ResponseTime|Ping|DB_size|Long_sql|Version|Uptime|Com_update|Slow_queries|Com_select|Com_rollback|Questions|Com_insert|Com_delete|Com_commit|Bytes_sent|Bytes_received|Com_begin|Threads_connected|RW_ratio|Transactions|Threads_running|Innodb_buffer_read_hits|Innodb_buffer_usage|Innodb_buffer_wait|Innodb_buffer_dirty_ratio|D_pending_fsyncs|D_pending_reads|D_pending_writes|Log_waits|Log_pending_fsyncs|Log_pending_writes|Log_written|Innodb_row_lock_current_waits)"
;;
esac
