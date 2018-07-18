from worker.util import loads_res


def get_item_model_by_id(session, model_table, host_filter_list, _id):
    q = session.query(model_table).filter_by(id=_id).first()
    res = loads_res(host_filter_list, q)
    return res
