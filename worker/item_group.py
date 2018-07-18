from db.monitor_center import MC


def join_ItemName_ItemKey_to_dict(item):
    """
    把 Item_groud 的 返回结果，从
    item_key :[xxx,xx]
    item_name : [xxx,xx]作为独立的数组，
    更改为
    [{'key':xx ,'name':xxx}] 的字典数组

    :param item:  字典
    :return:
    """
    item_name = item.pop('item_name')
    item_key = item.pop('item_key')
    item_info = []
    if item_name:
        for ii in range(0, len(item_name)):
            item_info.append({'name': item_name[ii], 'key': item_key[ii]})
        item.update({'item': item_info})
    return item


def get_item_groups_by_id(session, _id):
    name = session.query(MC.item_groups.name).filter_by(id=_id).first()[0]
    q = session.query(MC.items).filter(MC.items.mc_item_groups_id == _id).all()
    items = []
    for ii in q:
        ii.__dict__.pop("_sa_instance_state")
        items.append(ii.__dict__)
    return {"id": _id, "name": name, "items": items}
