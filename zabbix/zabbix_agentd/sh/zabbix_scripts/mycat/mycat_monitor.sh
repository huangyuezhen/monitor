#username
MYCAT_USER='zabbix'
#password
MYCAT_PWD='DHZKXQRsA7k65MSmhjIk'
#host ip
MYCAT_HOST='127.0.0.1'
#manager port
MYCAT_MAN_PORT='9066'
 
 
 #mycat connection 
 MYCAT_CONN="mysql -u${MYCAT_USER} -p${MYCAT_PWD} -h${MYCAT_HOST} -P${MYCAT_MAN_PORT} -N -e "
 
 
 #check in param
 
 if [ $# -ne "1" ];then
   echo "arg error!"
 fi
 
 #get data
 
 case $1 in
      thread_active_count)
                 result=`${MYCAT_CONN} "show @@threadpool" 2>/dev/null |grep -w BusinessExecutor|cut -f3 `
                 echo $result
                 ;;
          task_queue_size)
                          result=`${MYCAT_CONN} "show @@threadpool" 2>/dev/null |grep -w BusinessExecutor|cut -f4 `
                                         echo $result
                                         ;;
          memory_total_size)
                          result=`${MYCAT_CONN} "show @@server" 2>/dev/null | grep "\|" | cut -f3 ` 
                                         echo $result
                                         ;;
          memory_used_size)
                          result=`${MYCAT_CONN} "show @@server" 2>/dev/null | grep "\|" | cut -f2`
                                         echo $result
                                         ;;
          processor_net_in)
                          result=`${MYCAT_CONN} "show @@processor" 2>/dev/null |awk 'BEGIN{sum=0}{sum+=$2}END {print sum}'`
                                         echo $result
                                         ;;
          processor_net_out)
                          result=`${MYCAT_CONN} "show @@processor" 2>/dev/null |awk 'BEGIN{sum=0}{sum+=$3}END {print sum}'`
                                         echo $result
                                         ;;										 
          conn_net_in)
                          result=`${MYCAT_CONN} "show @@connection" 2>/dev/null |awk 'BEGIN{sum=0}{sum+=$9}END {print sum}'`
                                         echo $result
                                         ;;
          conn_net_out)
                          result=`${MYCAT_CONN} "show @@connection" 2>/dev/null |awk 'BEGIN{sum=0}{sum+=$10}END {print sum}'`
                                         echo $result
                                         ;;										 
          backend_net_in)
                          result=`${MYCAT_CONN} "show @@backend" 2>/dev/null |awk 'BEGIN{sum=0}{sum+=$7}END {print sum}'`
                                         echo $result
                                         ;;
          backend_net_out)
                          result=`${MYCAT_CONN} "show @@backend" 2>/dev/null |awk 'BEGIN{sum=0}{sum+=$8}END {print sum}'`
                                         echo $result
                                         ;;										 

		  fronted_conn_count)
                          result=`${MYCAT_CONN} "show @@connection" 2>/dev/null |wc -l `
                                         echo $result
                                         ;;
          backend_conn_count)
                          result=`${MYCAT_CONN} "show @@backend" 2>/dev/null |wc -l `
                                         echo $result
                                         ;;
          sql_router_cache_max_count)
                          result=`${MYCAT_CONN} "show @@cache" 2>/dev/null |egrep SQLRouteCache|awk '{print $2}'`
                                         echo $result
                                         ;;
          sql_router_cache_cur_count)
                          result=`${MYCAT_CONN} "show @@cache" 2>/dev/null |egrep SQLRouteCache|awk '{print $3}'`
                                         echo $result
                                         ;;	                                         
          sql_router_cache_access_count)
                          result=`${MYCAT_CONN} "show @@cache" 2>/dev/null |egrep SQLRouteCache|awk '{print $4}'`
                                         echo $result
                                         ;;
          sql_router_cache_hit_count)
                          result=`${MYCAT_CONN} "show @@cache" 2>/dev/null |egrep SQLRouteCache|awk '{print $5}'`
                                         echo $result
                                         ;;	
          sql_router_cache_put_count)
                          result=`${MYCAT_CONN} "show @@cache" 2>/dev/null |egrep SQLRouteCache|awk '{print $6}'`
                                         echo $result
                                         ;;
									 
										 
          *)
		  
	   echo "usage:$0(thread_active_count|task_queue_size|memory_total_size|memory_used_size 
					  fronted_conn_count|processor_net_in|processor_net_out|backend_conn_count 
					  conn_net_in|conn_net_out|backend_net_in|backend_net_in 
					  sql_router_cache_max_count|sql_router_cache_cur_count 
					  sql_router_cache_access_count|sql_router_cache_hit_count 
					  sql_router_cache_put_count)"
	   ;;
 esac
