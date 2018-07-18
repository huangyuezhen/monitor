from worker.host_filter import host_filter_by_cmdb, database_filter_by_cmdb




def get_cmdb_database(cmdb_filters):
    cmdb_host_info, total_host = database_filter_by_cmdb(**cmdb_filters)

    res = dict()
    for key in cmdb_host_info:
        obj = cmdb_host_info[key]
        cmdb_ip = [item['ip_addr'] for item in obj['cmdb_ip']]
        cmdb_hostname = obj['cmdb_hostname']
        cmdb_database_name = [item['name'] for item in obj['cmdb_database_name_list']]
        _dict = {
            'cmdb_ip': cmdb_ip,
            'cmdb_database_name': cmdb_database_name,
            'cmdb_hostname': cmdb_hostname
        }
        res.update({cmdb_hostname: _dict})

    # host = list(cmdb_host_info.keys())
    # return cmdb_host_info
    return res


def get_application_items_by_hostid(session, zbx_db, hostid):
    applications_items_dict = dict()
    items = zbx_db.items
    items_applications = zbx_db.items_applications
    applications = zbx_db.applications
    graphs = zbx_db.graphs
    graphs_items = zbx_db.graphs_items
    q = session.query(items.hostid, items.itemid, items.name, items.key_,items.value_type, applications.name, graphs.name).outerjoin(
        items_applications,
        items_applications.itemid == items.itemid).outerjoin(
        applications, applications.applicationid == items_applications.applicationid).outerjoin(graphs_items,
                                                                                                graphs_items.itemid == items.itemid).outerjoin(
        graphs, graphs.graphid == graphs_items.graphid).filter(
        items.hostid.in_(hostid)).order_by(items.hostid)
    res = q.all()
    for item in res:
        hostid, itemid, item_name, item_key_,item_value_type, application_name, graph_name = item
        application_name = application_name if application_name else "无application"
        item_dict = {
            "itemid": itemid,
            "item_key_": item_key_,
            "item_name": item_name,
            "graph_name": graph_name,
            "value_type": item_value_type
        }
        if hostid in applications_items_dict.keys():
            if application_name in applications_items_dict[hostid].keys():
                applications_items_dict[hostid][application_name].append(item_dict)
            else:
                applications_items_dict[hostid].update({application_name: [item_dict]})
        else:
            applications_items_dict[hostid] = {application_name: [item_dict]}

    return applications_items_dict
