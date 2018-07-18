from sqlalchemy import or_


def get_zbx_screen_with_full_info(zbx_db, zbx_sesssion, **filters):
    screens = zbx_db.screens
    screens_items = zbx_db.screens_items
    graphs = zbx_db.graphs
    graphs_items = zbx_db.graphs_items
    items = zbx_db.items
    hosts = zbx_db.hosts

    screen_query = zbx_sesssion.query(screens)


def screen_filter_by_name(query=None, case_sensitive=None, zbx_db=None, like=None, name=[]):
    screens = zbx_db.screens
    if like:
        format_name = ['%{}%'.format(i) for i in name]
        rule = or_(*[screens.name.like(i) for i in format_name]) if case_sensitive else or_(
            *[screens.name.ilike(i) for i in format_name])
    else:
        rule = screens.name.in_(name)
    query = query.filter(rule)
    return query
