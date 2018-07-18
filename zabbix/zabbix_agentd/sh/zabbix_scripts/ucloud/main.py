# 从ucloud 上获取udb uredis  ulb等监控信息，
# mian 是入口函数，ucloud_sdk 为调用的sdk
# settings.yml  为配置信息，包括ucloud 私钥等信息
# 2017-12-15
# huangyuezhen


import os
import yaml
import sys

from ucloud_sdk import UcloudApiClient

sys.path.insert(0, os.path.abspath('.'))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

with open(BASE_DIR + os.path.sep + 'settings.yml', 'rb') as ymlfile:
    settings = yaml.load(ymlfile)

CONFIGS = settings['ucloud']
UDB_ITEM = settings['udb']


class GetInfoFromUCloud(object):
    def __init__(self, base_url=CONFIGS['base_url'], public_key=CONFIGS['public_key'],
                 private_key=CONFIGS['private_key'], ):
        self.client = UcloudApiClient(base_url=base_url, public_key=public_key,
                                      private_key=private_key)

    def get_metric(self, param):
        Params = {
            "Action": "GetMetric",
            "Region": "cn-gd",
            "Zone": "cn-gd-02",
            'TimeRange': 1800,
            'ProjectId': "org-e5sxn5"
            # "BeginTime": 1511248527,
            # "EndTime": 1511978199
        }
        Params.update(param)
        response = self.client.get('/', params=Params)
        return response

    def get_metric_by_resourceId(self, resourceId):
        '''
         根据 resource ID返回所有的监控指标
        :return:
        '''
        param = {
            "ResourceType": "udb",
            "ResourceId": resourceId
        }
        # "ResourceId": "udb-sb53e3",
        # "MetricName.1": "DiskUsage",
        # "MetricName.0": "CPUUtilization",
        for i in range(0, len(UDB_ITEM['udb'])):
            mertic_name = "MetricName." + str(i)
            param.update({mertic_name: UDB_ITEM['udb'][i]})
        res = self.get_metric(param)
        return res

    def get_metric_by_argus(self, region, zone, projectId, resourceType, resourceId, metricName):
        """
        根据resourceID metricName 返回 指定的指标
        :param resourceId:
        :param metricName:
        :return:
        """
        param = {
            "Region": region,
            "Zone": zone,
            'ProjectId': projectId,
            "ResourceType": resourceType,
            "ResourceId": resourceId,
            "MetricName.0": metricName,
            'TimeRange': 1800,
        }
        res = self.get_metric(param)
        # print(res)
        if res['RetCode'] == 0 and len(res['DataSets'][metricName]) > 0:
            return res['DataSets'][metricName][-1]['Value']
        else:
            return res
            # return res


if __name__ == '__main__':
    InsGetInfoFromUCloud = GetInfoFromUCloud()
    arg = sys.argv
    region, zone, projectId, resourceType, resourceId, metricName = arg[1:]
    res = InsGetInfoFromUCloud.get_metric_by_argus(region=region, zone=zone, projectId=projectId,
                                                   resourceType=resourceType, resourceId=resourceId,
                                                   metricName=metricName)
    print(res)

    # Region = "cn-gd"
    # Zone = "cn-gd-02"
    # ProjectId = "org-e5sxn5"
    # ResourceType = 'udb'
    # ResourceId = 'udbha-jggmuo'
    # MetricName = 'MemUsage'
    # res = InsGetInfoFromUCloud.get_metric_by_argus(region=Region, zone=Zone, projectId=ProjectId,
    #                                                resourceType=ResourceType, resourceId=ResourceId,
    #                                                metricName=MetricName)
    # print(res)
