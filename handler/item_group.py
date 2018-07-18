import json

from common.error import MonitorCenterError
from db.monitor_center import MC
from handler.base import MonitorBaseHandler
from db.mysql import session_scope
from worker.item_group import get_item_groups_by_id


class ItemGroupHandler(MonitorBaseHandler):
    def get(self):
        name = self.get_arguments("name")
        page = int(self.get_argument('page', 1))
        page_size = int(self.get_argument('page_size', 15))

        item_groups = MC.item_groups
        items = MC.items

        if page < 1 and page_size < 1:
            page, page_size = (0, 15)

        if name:
            name = name[0].split(',')
            q = self.mc_sessions.query(item_groups).filter(item_groups.name.in_(name))
        else:
            q = self.mc_sessions.query(item_groups)
        total_count = q.count()
        offset = (page - 1) * page_size
        q = q.offset(offset).limit(page_size)

        res = []
        for ii in q:
            _group_id = ii.id
            _items = []
            q_items = self.mc_sessions.query(items).filter(items.mc_item_groups_id == _group_id).order_by(
                items.sort_num).all()
            for j in q_items:
                j.__dict__.pop("_sa_instance_state")
                _items.append(j.__dict__)
            ii.__dict__.pop("_sa_instance_state")
            ii.__dict__.update({'items': _items})
            res.append(ii.__dict__)

        self.render_json_response(code=200, msg='OK', res=res, total_count=total_count)

    def post(self, *args, **kwargs):
        argus = self.arguments

        for key in ['name', 'items']:
            if key not in argus.keys():
                raise MonitorCenterError(status_code=401, reason='Missing arguments')

        grp_name = argus['name']
        items = argus['items']

        with session_scope(self.mc_sessions) as session:

            item_groups = MC.item_groups(**{"name": grp_name})
            session.add(item_groups)
            session.flush()

            item_groups_id = item_groups.id
            items_instance = []
            for ii in items:
                ii.update({"mc_item_groups_id": item_groups_id})
                item_instance = MC.items(**ii)
                items_instance.append(item_instance)
            session.add_all(items_instance)
        res = get_item_groups_by_id(self.mc_sessions, item_groups_id)
        self.render_json_response(code=200, msg='OK', res=res)

    def put(self):
        argus = self.arguments
        _id = argus.pop('id', None)
        if not _id:
            raise MonitorCenterError(code=401, reason="Missing arguments, item_groups id  are required")

        if 'items' in argus.keys():
            items = argus.pop("items")

        with session_scope(self.mc_sessions) as session:
            #  更新 item_groups
            session.query(MC.item_groups).filter_by(id=_id).update(argus, synchronize_session=False)

            # 先删除 后更新items
            #  删除
            session.query(MC.items).filter_by(mc_item_groups_id=_id).delete(synchronize_session=False)
            #  更新
            item_groups_id = _id
            items_instance = []
            for ii in items:
                ii.update({"mc_item_groups_id": item_groups_id})
                item_instance = MC.items(**ii)
                items_instance.append(item_instance)
            session.add_all(items_instance)

        res = get_item_groups_by_id(self.mc_sessions, _id)

        self.render_json_response(code=200, msg='OK', res=res)

    def delete(self, *args, **kwargs):

        argus = self.arguments
        _id = argus['id'] if 'id' in argus.keys() else None
        if not _id:
            raise MonitorCenterError(code=401, reason='id is required')

        with session_scope(self.mc_sessions) as session:
            session.query(MC.item_groups).filter_by(id=_id).delete(synchronize_session=False)
            session.query(MC.items).filter_by(mc_item_groups_id=_id).delete(synchronize_session=False)

        self.render_json_response(code=200, msg='OK')
