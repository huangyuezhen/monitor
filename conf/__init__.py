import yaml
import os


if os.path.isfile('/data/conf/monitor_center/settings.yml'):
    BASE_DIR = '/data/conf/monitor_center'
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))


with open(BASE_DIR + os.path.sep + 'settings.yml', 'rb') as ymlfile:
    settings = yaml.load(ymlfile)

try:
    with open(BASE_DIR + os.path.sep + 'local_settings.yml', 'rb') as ymlfile:
        settings.update(yaml.load(ymlfile))
except:
    pass
