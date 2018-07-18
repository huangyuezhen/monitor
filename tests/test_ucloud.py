import sys
sys.path.append('.')
sys.path.append('..')
import unittest
from tests.util import BaseTestCase
from common import ucloud
from common.ucloud_util import UcloudUtil
import json


class UcloudTestCase(BaseTestCase):
    def setUp(self):
        super(UcloudTestCase, self).setUp()
        self.ucloud = ucloud
        self.ucloud_util = UcloudUtil

    def test_get_metric(self):
        parameters = {
            "Action": "GetMetric",
            "ResourceType": "udb",
            "Region": "cn-gd",
            "Zone": "cn-gd-02",
            "ResourceId": "udbha-mrfsrg",
            "MetricName.1": "DiskUsage",
            "MetricName.0": "CPUUtilization",
            "TimeRange": "120"
        }
        response = self.ucloud.get(**parameters)
        self.assertIsInstance(response, dict, response)
        self.assertEqual(response['RetCode'], 0, response)
        self.assertEqual(response['Action'], parameters['Action'] + 'Response', response)
        self.assertTrue(parameters['MetricName.0'] in response['DataSets'], response)

    def test_get_udb(self):
        params = {
            'Action': 'DescribeUDBInstance',
            'Region': 'cn-gd',
            'Offset': 0,
            'Limit': 10000,
            'ClassType': 'SQL'
        }
        response = self.ucloud.get(**params)
        self.assertEqual(response['RetCode'], 0, response)
        self.assertEqual(response['Action'], params['Action'] + 'Response', response)
        # print(json.dumps(response))

    def test_get_region(self):
        params = {
            'Action': 'GetRegion'
        }
        response = self.ucloud.get(**params)
        self.assertEqual(response['RetCode'], 0, response)
        self.assertEqual(response['Action'], params['Action'] + 'Response', response)
        # print(json.dumps(response))
        # region_list = [r['RegionName'] for r in response['Regions']]
        # print(json.dumps(region_list))

    def test_get_project_id(self):
        res = self.ucloud_util.get_project_list()
        # print(res)
        self.assertIsInstance(res, list, res)
        for p in res:
            self.assertTrue('ProjectId' in p, p)
            self.assertTrue('ProjectName' in p, p)

    # def test_get_all_ulb(self):
    #     res = []
    #     params = {
    #         'Action': 'DescribeULB',
    #         'Region': 'cn-gd'
    #     }

    #     project_list = self.ucloud_util.get_project_list()
    #     project_id_list = [p['ProjectId'] for p in project_list]

    #     for i in project_id_list:
    #         r = self.ucloud.get(project_id=i, **params)
    #         self.assertIsInstance(r, dict, r)
    #         self.assertEqual(r['RetCode'], 0, r)
    #         res.append(r)
    #     print(json.dumps(res))

    def test_get_ulb_metric_overview(self):
        res = []
        params = {
            'Action': 'DescribeULB',
            'Region': 'cn-gd'
        }

        project_list = self.ucloud_util.get_project_list()
        project_id_list = [p['ProjectId'] for p in project_list]

        project_id = project_id_list[0]
        ulb_res = self.ucloud.get(project_id=project_id, **params)
        self.assertIsInstance(ulb_res, dict, ulb_res)
        self.assertEqual(ulb_res['RetCode'], 0, ulb_res)
        ulb_id = ulb_res['DataSet'][0]['ULBId']
        ulb_id_list = [u['ULBId'] for u in ulb_res['DataSet']]

        for ulb_id in ulb_id_list:
            params = {
                "Action": "GetMetricOverview",
                "Region": 'cn-gd',
                "Zone": 'cn-gd-02',
                'ProjectId': project_id,
                "ResourceType": 'ulb',
                "ResourceId": ulb_id,
                # "MetricName.0": 'TotalNetworkOut',
                'TimeRange': 1800,
            }
            metric_res = self.ucloud.get(**params)
            self.assertIsInstance(metric_res, dict, metric_res)
            self.assertEqual(metric_res['RetCode'], 0, metric_res)
            res.extend(metric_res['DataSet'])
        # print(json.dumps(res))

    def test_get_ulb_metric(self):
        parameters = {
            "Action": "GetMetric",
            "ResourceType": "ulb",
            "Region": "cn-gd",
            "Zone": "cn-gd-02",
            "ResourceId": "ulb-bv21vb",
            "MetricName.0": "TotalNetworkOut",
            "TimeRange": "120"
        }
        response = self.ucloud.get(**parameters)
        self.assertIsInstance(response, dict, response)
        self.assertEqual(response['RetCode'], 0, response)
        self.assertEqual(response['Action'], parameters['Action'] + 'Response', response)
        self.assertTrue(parameters['MetricName.0'] in response['DataSets'], response)
        # print(json.dumps(response))


if __name__ == '__main__':
    unittest.main()
