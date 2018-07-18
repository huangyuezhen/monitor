from handler.base import ModelBaseHandler
from db.monitor_center import MC


class HostItemModelHandler(ModelBaseHandler):
    def prepare(self):
        super(HostItemModelHandler, self).prepare()
        self.host_filters = [
            'cmdb_hostname', 'cmdb_ip', 'cmdb_application_name', 'cmdb_business_group_name', 'cmdb_department_name'
        ]
        self.list_argus = [
            'cmdb_hostname', 'cmdb_ip', 'cmdb_application_name', 'cmdb_business_group_name', 'cmdb_department_name',
            'item_group_name'
        ]
        self.model_table = MC.host_item_models
        self.item_group_table = MC.item_groups
        self.model_group_map_table = MC.host_item_models_item_groups
        self.map_table_model_id_obj = self.model_group_map_table.host_item_models_id
        self.map_table_model_id = 'host_item_models_id'


class DBItemModelHandler(ModelBaseHandler):
    def prepare(self):
        super(DBItemModelHandler, self).prepare()
        self.host_filters = ['cmdb_ip_addr', 'cmdb_hostname', 'cmdb_database_type_id', 'cmdb_host_type_id']
        self.list_argus = [
            'cmdb_ip_addr', 'cmdb_hostname', 'cmdb_database_type_id', 'cmdb_host_type_id', 'item_group_name'
        ]
        self.model_table = MC.db_item_models
        self.item_group_table = MC.item_groups
        self.model_group_map_table = MC.db_item_models_item_groups
        self.map_table_model_id_obj = self.model_group_map_table.db_item_models_id
        self.map_table_model_id = 'db_item_models_id'
