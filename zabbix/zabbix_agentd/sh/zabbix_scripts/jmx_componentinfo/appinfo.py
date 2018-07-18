#! /bin/env python
# -*- encoding=utf-8 -*-
'''
Appinfo Stat
Shaowei@2017-10-12
'''

import json
import optparse
import socket
import urllib2
import subprocess
import tempfile
import os
import logging
import re

from common.python.cmds import cmds

def get_realpath():
    return os.path.split(os.path.realpath(__file__))[0]

def get_binname():
    return os.path.split(os.path.realpath(__file__))[1]

class JmxAPI(object):
    def __init__(self, conf='/data/conf/zabbix-agentd/zabbix_agentd.conf', senderhostname=None):
        self.conf = conf    
        self.senderhostname = senderhostname
        self._cmdclient_jar = get_realpath() + "/" + "cmdline-jmxclient-0.10.3.jar"

    def call_jmx(self, port, beanstr, key = None):
        """
        java -jar cmdline-jmxclient-0.10.3.jar - localhost:12345 java.lang:type=Memory NonHeapMemoryUsage
        参数：
        """

        if key:
            cmdstr = "java -jar %s - localhost:%s '%s' '%s'" % (self._cmdclient_jar, port, beanstr, key)
        else:
            cmdstr = "java -jar %s - localhost:%s '%s' " % (self._cmdclient_jar, port, beanstr)
        
        c2 = cmds(cmdstr, timeout=3)
        logging.debug("Call jmx get key " + beanstr + ":" + key + " on port " + str(port))
        stdo, stde, return_code = c2.stdo(), c2.stde(), c2.code()
        logging.info("Found return code of " + str(return_code))

        logdict = {
            "cmdstr": cmdstr,
            "stdo": stdo,
            "stde": stde,
            "retcode": return_code,
            "orders": ["cmdstr", "stdo", "stde", "return_code"]}

        if return_code == 1:
            logging.error(logdict)
            return
        else:
            logging.debug(logdict)
            return stde if  stde else stdo


    def get_port_list(self):
        cmdstr = "ps -ef|grep java|grep -oP 'jmxremote.port=[0-9]{1,}'|grep -oP '\d+' 2>/dev/null"
        c2 = cmds(cmdstr, timeout=3)
        stdo, stde, return_code = c2.stdo(), c2.stde(), c2.code()
        logging.info("Found return code of " + str(return_code))

        (stdo_list, stde_list) = (re.split("\n", stdo.strip()), re.split("\n", stde.strip()))
        logdict = {
            "cmdstr": cmdstr,
            "stdo": stdo,
            "stde": stde,
            "retcode": return_code,
            "orders": ["cmdstr", "stdo", "stde", "return_code"],
        }
        if return_code == 1:
            logging.error(logdict)
            return
        else:
            logging.debug(logdict)
            return stdo_list
            #print stdo_list

    def get_appinfo(self, port, app, key):
        appinfo = self.call_jmx(port, "component:name="+app, key)
        if 'org.archive.jmx.Client' in appinfo:
            appsinfo_list = re.split('\s+',appinfo.strip())
            print(appsinfo_list[-1])
            return appsinfo_list[-1]
        else:
            return

    def get_app_component_info(self, port, app, key, sub_key=None):
        str_rp = re.compile('^.*ComponentInfo:\s')
        app_components_info_rt = self.call_jmx(port, 'component:name='+ app, 'ComponentInfo')
        if not app_components_info_rt : return 
        app_components_info = json.loads(json.loads(str_rp.sub('',app_components_info_rt)))
        if sub_key: 
            print(json.dumps(app_components_info['componentHealthIndicator'][key][sub_key]) if key in app_components_info['componentHealthIndicator'] else json.dumps(app_components_info[key][sub_key]))
            return app_components_info['componentHealthIndicator'][key][sub_key] if key in app_components_info['componentHealthIndicator'] else app_components_info[key][sub_key]
        else:
            print(json.dumps(app_components_info['componentHealthIndicator'][key]) if key in app_components_info['componentHealthIndicator'] else json.dumps(app_components_info[key]))
            return app_components_info['componentHealthIndicator'][key] if key in app_components_info['componentHealthIndicator'] else app_components_info[key]

    def list_app(self):
        apps_info = []
        port_list = self.get_port_list()
        str_rp = re.compile('^.*ComponentInfo:\s')
        for port in port_list:
            appinfo = self.call_jmx(port, 'component:name=*', 'AppName')
            if re.search(r"is not a registered",appinfo):
                continue
            if 'component:name=' in appinfo:
	        apps = re.split('\s+',appinfo.strip().replace('component:name=',''))
            elif 'org.archive.jmx.Client' in appinfo:
                apps = []
                appsinfo_list = re.split('\s+',appinfo.strip())
                apps.append(appsinfo_list[-1])
            else:
                continue 

            for app in apps:
                if not app: continue
                app_components_info_rt = self.call_jmx(port, 'component:name='+ app, 'ComponentInfo')
                if not app_components_info_rt : continue 
                app_components_info = json.loads(json.loads(str_rp.sub('',app_components_info_rt)))
                app_components = app_components_info['componentHealthIndicator'].keys()
                for app_component in app_components:
                    if app_component == "db": 
                        for app_db_info in app_components_info['componentHealthIndicator']['db']:
                            dbsource_metric = ''
                            #if re.search(r"db_active_size_connection|db_idle_size_connection|db_total_size_connection|SQL_EXCUTE_TOTAL_COUNT|SQL_EXCUTE_ERROR_COUNT|SLOW_SQL_COUNT",app_db_info):
                            if re.search(r"ql_excute_total_count|sql_excuter_error_count|slow_sql_count|slow_query_sql_count|slow_update_sql_count|sql_query_total_count|sql_update_total_count",app_db_info):
                                dbsource_metric = app_db_info
                                if dbsource_metric:
                                    element = {'{#APPNAME}': app, '{#PORT}': port, '{#DBSOURCE_MERTIC}': dbsource_metric}
                                    apps_info.append(element)
                            if re.search(r"DataSource",app_db_info):
                                for db_source_info in eval(app_components_info['componentHealthIndicator']['db'][app_db_info]):
                                    dbsource_metric = ''
				    dbsource_metric = app_db_info + '_' +db_source_info
                                    if dbsource_metric:
                                        element = {'{#APPNAME}': app, '{#PORT}': port, '{#DBSOURCE_MERTIC}': dbsource_metric}
                                        apps_info.append(element)
                    if app_component == "activemq": 
                        for app_info in app_components_info['componentHealthIndicator'][app_component]:
                            metric = ''
                            if re.search(r"listener_queue_name_size",app_info):
                                metric = app_info
                            if metric:
                                element = {'{#APPNAME}': app, '{#PORT}': port, '{#ACTIVEMQ_MERTIC}': metric}
                                apps_info.append(element)
                    if app_component == "apollo": 
                        for app_info in app_components_info['componentHealthIndicator'][app_component]:
                            metric = ''
                            if re.search(r"app.all.properties.count",app_info):
                                metric = app_info
                            if metric:
                                element = {'{#APPNAME}': app, '{#PORT}': port, '{#APOLLO_MERTIC}': metric}
                                apps_info.append(element)
                    if app_component == "dubbo": 
                        for app_info in app_components_info['componentHealthIndicator'][app_component]:
                            metric = ''
                            if re.search(r"thread_pool_size|active_size|dubbo_timeout_error_count|dubbo_error_count|dubbo_call_count",app_info):
                                metric = app_info
                            if metric:
                                element = {'{#APPNAME}': app, '{#PORT}': port, '{#DUBBO_MERTIC}': metric}
                                apps_info.append(element)
                    if app_component == "lts": 
                        for app_info in app_components_info['componentHealthIndicator'][app_component]:
                            metric = ''
                            if re.search(r"lts_job_length",app_info):
                                metric = app_info
                            if metric:
                                element = {'{#APPNAME}': app, '{#PORT}': port, '{#LTS_MERTIC}': metric}
                                apps_info.append(element)
                    if app_component == "rabbitmq": 
                        for app_info in app_components_info['componentHealthIndicator'][app_component]:
                            metric = ''
                            if re.search(r"rabbitmq_listner_queue_count",app_info):
                                metric = app_info
                            if metric:
                                element = {'{#APPNAME}': app, '{#PORT}': port, '{#RABBITMQ_MERTIC}': metric}
                                apps_info.append(element)
                    element = {'{#APPNAME}': app, '{#PORT}': port, '{#COMPONENT}': app_component}
                    apps_info.append(element)
        print(json.dumps({'data': apps_info}, sort_keys=True, indent=7, separators=(",", ":")))
        return json.dumps({'data': apps_info}, sort_keys=True, indent=7, separators=(",", ":"))


    def check_appinfo(self, port, app):
        str_rp = re.compile('^.*ComponentInfo:\s')
        rdatafile = tempfile.NamedTemporaryFile(delete=False)

        app_components_info_rt = self.call_jmx(port, 'component:name='+ app, 'ComponentInfo')
        if app_components_info_rt:
            app_components_info = json.loads(json.loads(str_rp.sub('',app_components_info_rt)))
            app_components = app_components_info['componentHealthIndicator'].keys()
            for app_component in app_components:
                if app_component == "db":
                    for app_db_info in app_components_info['componentHealthIndicator']['db']:
                        #if re.search(r"db_active_size_connection|db_idle_size_connection|db_total_size_connection|SQL_EXCUTE_TOTAL_COUNT|SQL_EXCUTE_ERROR_COUNT|SLOW_SQL_COUNT",app_db_info):
                        if re.search(r"ql_excute_total_count|sql_excuter_error_count|slow_sql_count|slow_query_sql_count|slow_update_sql_count|sql_query_total_count|sql_update_total_count",app_db_info):
                            key = '"appinfo[{0},{1}]"'
                            key = key.format(app, app_db_info)
                            value = app_components_info['componentHealthIndicator']['db'][app_db_info]
                            #print("SENDER_DATA: - %s %s" % (key,value))
                            rdatafile.write("- %s %s\n" % (key, value))
                        if re.search(r"DataSource",app_db_info):
 			    for db_source_info in eval(app_components_info['componentHealthIndicator']['db'][app_db_info]):
                              key = '"appinfo[{0},{1}]"'
                              key = key.format(app, app_db_info + '_' +db_source_info)
                              value = eval(app_components_info['componentHealthIndicator']['db'][app_db_info])[db_source_info]
                              rdatafile.write("- %s %s\n" % (key, value))
                              #print("SENDER_DATA: - %s %s" % (key,value))
                              rdatafile.write("- %s %s\n" % (key, value))
                if app_component == "activemq":
                    for app_info in app_components_info['componentHealthIndicator'][app_component]:
                        if re.search(r"listener_queue_name_size",app_info):
                            key = '"appinfo[{0},{1}]"'
                            key = key.format(app, app_info)
                            value = app_components_info['componentHealthIndicator'][app_component][app_info]
                            rdatafile.write("- %s %s\n" % (key, value))
                if app_component == "apollo":
                    for app_info in app_components_info['componentHealthIndicator'][app_component]:
                        if re.search(r"app.all.properties.count",app_info):
                            key = '"appinfo[{0},{1}]"'
                            key = key.format(app, app_info)
                            value = app_components_info['componentHealthIndicator'][app_component][app_info]
                            rdatafile.write("- %s %s\n" % (key, value))
                if app_component == "dubbo":
                    for app_info in app_components_info['componentHealthIndicator'][app_component]:
                        if re.search(r"thread_pool_size|active_size|dubbo_timeout_error_count|dubbo_error_count|dubbo_call_count",app_info):
                            key = '"appinfo[{0},{1}]"'
                            key = key.format(app, app_info)
                            value = app_components_info['componentHealthIndicator'][app_component][app_info]
                            #print("SENDER_DATA: - %s %s" % (key,value))
                            rdatafile.write("- %s %s\n" % (key, value))
                if app_component == "lts":
                    for app_info in app_components_info['componentHealthIndicator'][app_component]:
                        if re.search(r"lts_job_length",app_info):
                            key = '"appinfo[{0},{1}]"'
                            key = key.format(app, app_info)
                            value = app_components_info['componentHealthIndicator'][app_component][app_info]
                            rdatafile.write("- %s %s\n" % (key, value))
                if app_component == "rabbitmq":
                    for app_info in app_components_info['componentHealthIndicator'][app_component]:
                        if re.search(r"rabbitmq_listner_queue_count",app_info):
                            key = '"appinfo[{0},{1}]"'
                            key = key.format(app, app_info)
                            value = app_components_info['componentHealthIndicator'][app_component][app_info]
                            rdatafile.write("- %s %s\n" % (key, value))
                key = '"appinfo[{0},{1}_state]"'
                key = key.format(app, app_component)
                value = app_components_info['componentHealthIndicator'][app_component]['state']
                #print("SENDER_DATA: - %s %s" % (key,value))
                logging.debug("SENDER_DATA: - %s %s" % (key,value))
                rdatafile.write("- %s %s\n" % (key, value))
        rdatafile.close()
        return_code = self._send_data(rdatafile.name)
        os.unlink(rdatafile.name)
        print(return_code)
        return return_code


    def _send_data(self, tmpfile):
        '''Send the queue data to Zabbix.'''
        #cmdstr = '/data/svr/zabbix-agentd/bin/zabbix_sender -vv -c {0} -i {1}'
        cmdstr = '/usr/local/zabbix-agent/bin/zabbix_sender -vv -c {0} -i {1}'
        if self.senderhostname:
            cmdstr = cmdstr + " -s " + self.senderhostname
        
        c2 = cmds(cmdstr.format(self.conf, tmpfile))
        stdo, stde, return_code = c2.stdo(), c2.stde(), c2.code()
        logging.debug("Finished sending data")
        logging.info("Found return code of " + str(return_code))

        (stdo_list, stde_list) = (re.split("\n", stdo.strip()), re.split("\n", stde.strip()))
        logdict = {
            "cmdstr": cmdstr,
            "stdo": stdo,
            "stde": stde,
            "retcode": return_code,
            "orders": ["cmdstr", "stdo", "stde", "return_code"],
        }
        if return_code == 1:
            logging.error(logdict)
        else:
            logging.debug(logdict)
        return return_code

        
def main():
    '''Command-line parameters and decoding for Zabbix use/consumption.'''
    parser = optparse.OptionParser()
    parser.add_option('-l','--list', action="store_true", dest="is_list", default=False, help='List all apps')
    parser.add_option('--list-dbsource', action="store_true", dest="is_list_db", default=False, help='List db source')
    parser.add_option('-c','--check', action="store_true", dest="is_check", default=False, help='Check apps Component infos')
    parser.add_option('--get', action="store_true", dest="is_get", default=False, help='Check apps Component info')
    parser.add_option('--get-component', action="store_true", dest="is_get_component_info", default=False, help='Check apps Component info')
    parser.add_option('--port', help='the JMX port', type='int', default=False)
    parser.add_option('--appname', help='AppName', default='')
    parser.add_option('--key', help='AppName', default='')
    parser.add_option('--conf', default='/data/conf/zabbix-agentd/zabbix_agentd.conf')
    parser.add_option('--senderhostname', default='', help='Allows including a sender parameter on calls to zabbix_sender')
    parser.add_option('--logfile', help='File to log errors (defaults to /data/log/zabbix-agentd/appinfo_zabbix.log)', default='/data/log/zabbix-agentd/appinfo_zabbix.log')
    parser.add_option('--loglevel', help='Defaults to INFO', default='INFO')

    (options, args) = parser.parse_args()
    logging.basicConfig(filename=options.logfile or "/data/log/zabbix-agentd/appinfo_zabbix.log", level=logging.getLevelName(options.loglevel or "INFO"), format='%(asctime)s %(levelname)s: %(message)s')
     
    logging.debug("Started trying to process data")
    api = JmxAPI(options.conf, options.senderhostname)

    if options.is_list:
        api.list_app() 

    if options.is_list_db:
        api.list_dbsource() 

    if options.is_check and options.port and options.appname:
       api.check_appinfo(options.port, options.appname)

    if options.is_get and options.port and options.appname and options.key:
       api.get_appinfo(options.port, options.appname, options.key)

    if options.is_get_component_info and options.port and options.appname and options.key:
       api.get_app_component_info(options.port, options.appname, options.key)



if __name__ == '__main__':
    main()

