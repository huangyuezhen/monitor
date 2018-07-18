#!/usr/bin/env /usr/bin/python
'''Python module to query the RabbitMQ Management Plugin REST API and get
results that can then be used by Zabbix.
https://github.com/jasonmcintosh/rabbitmq-zabbix
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


class ActiveMQAPI(object):
    '''Class for ActiveMQ Management API'''

    def __init__(self, user_name='guest', password='guest', host_name='',
                 port=8161, brokername='localhost' , conf='/data/conf/zabbix-agentd/zabbix_agentd.conf', senderhostname=None, protocol='http'):
        self.user_name = user_name
        self.password = password
        self.host_name = host_name or socket.gethostname()
        self.port = port
        self.conf = conf or '/data/conf/zabbix-agentd/zabbix_agentd.conf'
        self.senderhostname = senderhostname
        self.protocol = protocol or 'http'
        self.brokername = brokername or 'localhost'

    def call_api(self, mbean, key=None):
        '''Call the REST API and convert the results into JSON.'''
        if key:
            url = '{0}://{1}:{2}/api/jolokia/read/{3}/{4}'.format(self.protocol, self.host_name, self.port, mbean, key)
        else:
            url = '{0}://{1}:{2}/api/jolokia/read/{3}'.format(self.protocol, self.host_name, self.port, mbean)
        password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
        password_mgr.add_password(None, url, self.user_name, self.password)
        handler = urllib2.HTTPBasicAuthHandler(password_mgr)
        logging.debug('Issue a rabbit API call to get data on ' + url)
        logging.debug('Full URL:' + url)
        return json.loads(urllib2.build_opener(handler).open(url).read())

    def list_queues(self,filters=None):
        '''
        List all of the ActiveMQ queues, filtered against the filters provided
        in .rab.auth. See README.md for more information.
        '''
        queues = []
        if not filters:
            filters = [{}]
        mbean = "org.apache.activemq:type=Broker,brokerName={0},destinationType=Queue,destinationName=*"
        
        result = self.call_api(mbean.format(self.brokername))
        if result['status'] != 200:
            logging.error('call activemq error!')
            return 
        else:
            for queue_info in result['value'].values():
                if 'DLQ' in queue_info['Name']:
                    element = {'{#BROKENAME}': self.brokername,'{#DLQ_QUEUENAME}': queue_info['Name']}
                else:
                    element = {'{#BROKENAME}': self.brokername,'{#QUEUENAME}': queue_info['Name']}
                queues.append(element)  
        return queues
            
    def check_queue(self, filters=None):
        '''Return the value for a specific item in a queue's details.'''
        return_code = 0
        if not filters:
            filters = [{}]

        rdatafile = tempfile.NamedTemporaryFile(delete=False)
        mbean = "org.apache.activemq:type=Broker,brokerName={0},destinationType=Queue,destinationName=*"
        
        result = self.call_api(mbean.format(self.brokername))
        if result['status'] != 200:
            logging.error('call activemq error!')
            return 
        else:
            for queue_info in result['value'].values():
                self._prepare_data(queue_info, rdatafile)
                
        rdatafile.close()
        return_code = self._send_data(rdatafile)
        os.unlink(rdatafile.name)
        return return_code
        
    def _prepare_data(self, queue_info, tmpfile):
        '''Prepare the queue data for sending'''
        if 'DLQ' in queue_info['Name']:
            for item in ['QueueSize', 'MemoryUsageByteCount']:
                key = '"activemq.queues[{0},queue_{1},{2}]"'
                key = key.format(self.brokername, item, queue_info['Name'])
                value = queue_info.get(item, 0)
                logging.debug("SENDER_DATA: - %s %s" % (key,value))
                tmpfile.write("- %s %s\n" % (key, value))
        else:
            for item in ['QueueSize', 'Paused', 'ConsumerCount',
                     'MemoryUsageByteCount']:
                key = '"activemq.queues[{0},queue_{1},{2}]"'
                key = key.format(self.brokername, item, queue_info['Name'])
                value = queue_info.get(item, 0)
                logging.debug("SENDER_DATA: - %s %s" % (key,value))
                tmpfile.write("- %s %s\n" % (key, value))


    def _send_data(self, tmpfile):
        '''Send the queue data to Zabbix.'''
        args = '/data/svr/zabbix-agentd/bin/zabbix_sender -vv -c {0} -i {1}'
        if self.senderhostname:
            args = args + " -s " + self.senderhostname
        return_code = 0
        process = subprocess.Popen(args.format(self.conf, tmpfile.name),
                                           shell=True, stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE)
        out, err = process.communicate()
        logging.debug("Finished sending data")
        return_code = process.wait()
        logging.info("Found return code of " + str(return_code))
        if return_code == 1:
            logging.error(out)
            logging.error(err)
        else:
            logging.debug(err)
            logging.debug(out)
        return return_code      
        
    def check_health(self):
        '''Check the aliveness status of a given vhost.'''
        return self.call_api('org.apache.activemq:type=Broker,brokerName=localhost,service=Health','CurrentStatus')['value']      
        
    def check_server(self, item):
        '''
        CurrentConnectionsCount
        MemoryLimit
        MemoryPercentUsage
        Persistent
        StoreLimit
        StorePercentUsage
        TempLimit
        TempPercentUsage
        Uptime
        BrokerVersion
        BrokerName
        '''
        '''First, check the overview specific items'''
        if item == ('Uptime' or 'BrokerVersion' or 'BrokerName' or 'Persistent'):
            return self.call_api('org.apache.activemq:type=Broker,brokerName={0}'.format(self.brokername),item).get('value', 'None')
        else:
            return self.call_api('org.apache.activemq:type=Broker,brokerName={0}'.format(self.brokername),item).get('value', 0)
     

def main():
    '''Command-line parameters and decoding for Zabbix use/consumption.'''
    choices = ['list_queues', 'queues', 'check_health', 'server']
    parser = optparse.OptionParser()
    parser.add_option('--username', help='ActiveMQ API username', default='admin')
    parser.add_option('--password', help='ActiveMQ API password', default='admin')
    parser.add_option('--hostname', help='ActiveMQ API host', default=socket.gethostname())
    parser.add_option('--brokername', help='ActiveMQ API brokername', default='localhost')
    parser.add_option('--protocol', help='Use http or https', default='http')
    parser.add_option('--port', help='ActiveMQ API port', type='int', default=8161)
    parser.add_option('--check', type='choice', choices=choices, help='Type of check')
    parser.add_option('--metric', help='Which metric to evaluate', default='')
    parser.add_option('--filters', help='Filter used queues (see README)')
    parser.add_option('--conf', default='/etc/zabbix/zabbix_agentd.conf')
    parser.add_option('--senderhostname', default='', help='Allows including a sender parameter on calls to zabbix_sender')
    parser.add_option('--logfile', help='File to log errors (defaults to /data/sh/zabbix_scripts/activemq/activemq_zabbix.log)', default='/data/sh/zabbix_scripts/activemq/activemq_zabbix.log')
    parser.add_option('--loglevel', help='Defaults to INFO', default='INFO')
    (options, args) = parser.parse_args()
    if not options.check:
        parser.error('At least one check should be specified')
    logging.basicConfig(filename=options.logfile or "activemq_zabbix.log", level=logging.getLevelName(options.loglevel or "INFO"), format='%(asctime)s %(levelname)s: %(message)s')

    logging.debug("Started trying to process data")
    api = ActiveMQAPI(user_name=options.username, password=options.password,
                      host_name=options.hostname, port=options.port,brokername=options.brokername,
                      conf=options.conf, senderhostname=options.senderhostname, 
                     protocol=options.protocol)
    if options.filters:
        try:
            filters = json.loads(options.filters)
        except KeyError:
            parser.error('Invalid filters object.')
    else:
        filters = [{}]
    if not isinstance(filters, (list, tuple)):
        filters = [filters]
        
    if options.check == 'list_queues':
        print json.dumps({'data': api.list_queues(filters)})
    elif options.check == 'queues':
        print api.check_queue(filters)
    elif options.check == 'check_health':
        print api.check_health()
    elif options.check == 'server':
        if not options.metric:
            parser.error('Missing required parameter: "metric"')
        else:
            print api.check_server(options.metric)

if __name__ == '__main__':
    main()
