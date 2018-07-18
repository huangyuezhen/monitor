import os
import sys
import json

from conf import settings
from common import ucloud
from common.util import dump_file

sys.path.insert(0, os.path.abspath('.'))
CONFIGS = settings['ucloud']


class UcloudUtil(object):
    @staticmethod
    def get_project_list():
        '''
        获取项目信息
        :return:
        '''
        Parameters = {
            'Action': 'GetProjectList',
            'ResourceCount': 'Yes',
            'MemberCount': 'Yes'
        }
        response = ucloud.get('/', **Parameters)

        if response.get('RetCode') == 0 and response.get('TotalCount') != 0:
            return response.get('ProjectSet')

    @staticmethod
    def get_uhosts_yunnex(params):
        """获取云主机信息"""
        Parameters = {
            'Action': 'DescribeUHostInstance',
            'Region': 'cn-gd',
            'Zone': 'cn-gd-02',
            'Limit': 1000000
        }
        Parameters.update(params)
        response = ucloud.get('/', **Parameters)

        if response.get('RetCode') == 0 and response.get('TotalCount') != 0:
            return [response.get('TotalCount'), response.get('UHostSet')]
        else:
            return {}

    @staticmethod
    def get_uhost_tag_yunnex(params):
        '''
        获取 云主机 tag 信息
        :param params:
        :return:
        '''
        Parameters = {
            'Action': 'DescribeUHostTags',
            'Region': 'cn-gd',
            'Zone': 'cn-gd-02',
            'Limit': 10000000
        }
        Parameters.update(params)
        response = ucloud.get('/', **Parameters)

        if response.get('RetCode') == 0 and response.get('TotalCount') != 0:
            return response.get('TagSet')
        else:
            return {}

    @staticmethod
    def get_phosts_yunnex():
        '''
        获取物理机信息
        :return:
        '''
        Parameters = {
            'Action': 'DescribePHost',
            'Limit': 10000000,
            'Region': 'cn-gd',
            'Zone': 'cn-gd-02',
            'PHostId': 'upm-lsite1',
        }
        response = ucloud.get('/', **Parameters)

        if response.get('RetCode') == 0 and response.get('TotalCount') != 0:
            return response.get('PHostSet')

    @staticmethod
    def get_ulb_yunnex():
        '''
        获取负载均衡主机信息
        ulb (ucloud load balance) '''
        Parameters = {
            'Action': 'DescribeULB',
            'Region': 'cn-gd',
            'Zone': 'cn-gd-02',
            'Limit': 10000000
        }
        response = ucloud.get('/', **Parameters)

        if response.get('RetCode') == 0 and response.get('TotalCount') != 0:
            return response.get('DataSet')

    @staticmethod
    def get_udb_yunnex(params, class_type="SQL"):
        '''
        获取云数据库信息
        '''
        Parameters = {
            'Action': 'DescribeUDBInstance',
            'Region': 'cn-gd',
            'Zone': 'cn-gd-02',
            'Offset': 0,
            'ClassType': class_type,
            'Limit': 10000000
        }
        Parameters.update(params)
        response = ucloud.get('/', **Parameters)

        if response.get('RetCode') == 0 and response.get('TotalCount') != 0:
            return [response.get('TotalCount'), response.get('DataSet')]
        else:
            return []

    @staticmethod
    def get_uredis_yunnex(params):
        """
        获取redis 信息
        :return:
        """
        Parameters = {
            'Action': 'DescribeURedisGroup',
            'Region': 'cn-gd',
            'Zone': 'cn-gd-02',
            'Offset': 0,
            'ClassType': 'SQL',
            'Limit': 10000000
        }
        Parameters.update(params)
        response = ucloud.get('/', **Parameters)

        if response.get('RetCode') == 0 and response.get('TotalCount') != 0:
            return [response.get('TotalCount'), response.get('DataSet')]
        else:
            return []

    @staticmethod
    def get_host_by_projectid(out_path='conf/script/load_init_data/data/Uhost.json'):
        '''
        根据项目ID 返回云主机信息
        :return:
        '''
        project_set = UcloudUtil.get_project_list()
        res = []
        for project in project_set:
            total_count, uhost_set = UcloudUtil.get_uhosts_yunnex({'ProjectId': project['ProjectId']})
            host_list = UcloudUtil.uhost_to_host(uhost_set)

            res.append({'ProjectId': project['ProjectId'], 'ProjectName': project['ProjectName'],
                        "TotalCount": total_count, "HostSet": host_list})
        # dump_file(out_path, res)
        return res

    @staticmethod
    def get_uhost_tag_by_projectid():
        '''
        根据项目ID 返回 云主机tag 信息
        :return:
        '''
        tag_set = UcloudUtil.get_uhost_tag_yunnex({'ProjectId': 'org-yw1iri'})
        return tag_set

    @staticmethod
    def get_udb_by_projectid(class_type="SQL"):
        '''
        根据项目ID 返回 云数据库信息
        :return:
        '''
        project_set = UcloudUtil.get_project_list()
        res = []

        for project in project_set:
            if class_type == "SQL":
                _res = UcloudUtil.get_udb_yunnex({'ProjectId': project['ProjectId']}, class_type="SQL")
            else:
                _res = UcloudUtil.get_udb_yunnex({'ProjectId': project['ProjectId']}, class_type="NOSQL")
            total_count, tag_set = _res if len(_res) > 1 else [None, None]

            res.append({"prejsct_id": project['ProjectId'], "preject_name": project['ProjectName'],
                        "total_count": total_count, "res": tag_set})
        return res

    @staticmethod
    def get_udb_nosql_by_projectid():
        '''
               根据项目ID 返回 云数据库(Nosql)信息
               :return:
               '''
        project_set = UcloudUtil.get_project_list()
        res = []
        id_res = {}

        for project in project_set:
            _res = UcloudUtil.get_udb_yunnex({'ProjectId': project['ProjectId']}, class_type="NOSQL")
            total_count, tag_set = _res if len(_res) > 1 else [None, None]

            res.append({"prejsct_id": project['ProjectId'], "preject_name": project['ProjectName'],
                        "total_count": total_count, "res": tag_set})
            if tag_set:
                for db in tag_set:
                    id_res[db['Name']] = {'Region': 'cn-gd', 'Zone': 'cn-gd-02', "ProjectId": project['ProjectId'],
                                          "ProjectName": project['ProjectName'],
                                          'ResourceId': db['DBId']}
                    for _dbset in db['DataSet']:
                        id_res[_dbset['Name']] = {'Region': 'cn-gd', 'Zone': 'cn-gd-02',
                                                  "ProjectId": project['ProjectId'],
                                                  "ProjectName": project['ProjectName'],
                                                  'ResourceId': _dbset['DBId']}
        return [res, id_res]

    @staticmethod
    def get_uredis_by_projectid():
        """
        根据项目ID 返回 云 redis信息
        :return:
        """
        project_set = UcloudUtil.get_project_list()
        res = []
        id_res = {}
        for project in project_set:

            res = UcloudUtil.get_uredis_yunnex(
                {'ProjectId': project['ProjectId']})
            total_count, tag_set = res if res else (None, None)

            res.append({"prejsct_id": project['ProjectId'], "preject_name": project['ProjectName'],
                        "total_count": total_count, "res": tag_set})
            if tag_set:
                for ii in tag_set:
                    id_res[ii['Name']] = {'Region': 'cn-gd', 'Zone': 'cn-gd-02', "ProjectId": project['ProjectId'],
                                          "preject_name": project['ProjectName'], "GroupId": ii['GroupId'],
                                          }
        return [res, id_res]

    @staticmethod
    def get_os_type(ii):
        if ii["OsType"] == "Linux":
            os_type = 1
        elif ii["OsType"] == "Windows":
            os_type = 2
        else:
            os_type = 0
        return os_type

    @staticmethod
    def get_disk_soft_type(ii):
        if ii["Type"] == "Boot":
            _type = 1
        elif ii["Type"] == "Data":
            _type = 2
        elif ii["Type"] == "Udisk":
            _type = 3
        else:
            _type = 0
        return _type

    @staticmethod
    def get_ip_type(ii):
        if ii["Type"] == "Private":
            _type = 1
        else:
            _type = 0
        return _type

    @staticmethod
    def uhost_to_host(uhost_list):
        '''
        ucloud host 信息字段 与CMDB 字段对照，转换
        :param uhost_list: list
        :return:
        '''

        host_list = []
        for ii in uhost_list:

            os_type = UcloudUtil.get_os_type(ii)

            disks = []
            for j in ii["DiskSet"]:
                _type = UcloudUtil.get_disk_soft_type(j)
                disk = {
                    "tag": j["Drive"],
                    "size": j["Size"],
                    "disk_type": 1,
                    "type": _type
                }
                disks.append(disk)

            network_interfaces = []
            for k in ii["IPSet"]:
                ip_type = UcloudUtil.get_ip_type(k)
                ip_addr = k['IP']
                network_interface = {
                    "mac_addr": ip_addr,
                    "name": "",
                    "ip": {
                        "ip_type": ip_type,
                        "ip_addr": ip_addr
                    }
                }
                network_interfaces.append(network_interface)

            host = {
                "memory_total": ii['Memory'],
                "cpu_core_num": ii["CPU"],
                "os_info": ii["OsName"],
                "hostname": ii["Name"],
                # "os_type_name": ii["OsType"],
                "os_type": os_type,
                "disk": disks,
                "network_interface": network_interfaces

            }
            host_list.append(host)
        return host_list  # InsGetInfoFromUCloud = GetInfoFromUCloud()


# InsGetInfoFromUCloud.get_host_by_projectid()
if __name__ == '__main__':
    res ,id_res= UcloudUtil.get_udb_nosql_by_projectid()

    print(json.dumps(res, ensure_ascii=False, indent=4))
    out_path = "E://udb_nosql_id.json"
    dump_file(out_path, id_res)
