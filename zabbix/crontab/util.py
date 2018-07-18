import logging
from tornado.log import enable_pretty_logging
from tornado.options import options
from conf import settings

log_name = 'zabbix_crontab'
logger = logging.getLogger(log_name)
options.log_rotate_mode = 'time'
options.log_file_num_backups = 30
options.logging = 'debug' if settings['debug'] else 'info'
options.log_to_stderr = True
options.log_file_prefix = '{}/{}.log'.format(settings['server']['log_path'], log_name)
enable_pretty_logging(logger=logger)


def create_or_update_zabbix_host(zbx_api, host, agent_ip, group, ignore_update, template, project_id, region, zone,
                                 resource_id, ip, **params):
    macros = [
        {
            'macro': '{$PROJECTID}',
            'value': project_id
        },
        {
            'macro': '{$REGION}',
            'value': region
        },
        {
            'macro': '{$ZONE}',
            'value': zone
        },
        {
            'macro': '{$RESOURCEID}',
            'value': resource_id
        },
        {
            'macro': '{$IP}',
            'value': ip
        },
    ]

    return zbx_api.create_or_update_host(
        host=host,
        agent_ip=agent_ip,
        group_names=group,
        ignore_update=ignore_update,
        template_names=template,
        macros=macros,
        **params)
