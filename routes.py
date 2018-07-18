from handler.test_handler import HelloWorldHandler
from handler.host_filter import HostFilterOptionHandler
from handler.zbx_host_item import ZbxHostItemHandler
from handler.item_group import ItemGroupHandler
from handler.item_model import HostItemModelHandler, DBItemModelHandler
from handler.token import TokenHandler
from handler.zbx_item_trend import ZbxItemTrendHandler
from handler.zbx_db_item import ZbxDbItemHandler
from handler.zbx_item import ZbxItemHandler, ItemKey
from handler.zbx_host import ZbxHostHandler
from handler.zbx_host_group import ZbxHostGroupHandler
from handler.zbx_template import ZbxTemplatehaHandler
from handler.zbx_proxy import ZbxProxyHandler
from handler.zbx_graph import ZbxGraphHandler
from handler.zbx_application import ZbxApplicationHandler
from handler.zbx_screen import  ZbxScreenHandler

ROUTES = (
    (r'/', HelloWorldHandler),
    (r'/api/host_filter_option', HostFilterOptionHandler),
    (r'/api/zbx_host_item', ZbxHostItemHandler),
    (r'/api/zbx_db_item', ZbxDbItemHandler),
    (r'/api/zbx_trend_item', ZbxItemTrendHandler),
    (r'/api/item_group', ItemGroupHandler),
    (r'/api/host_item_model', HostItemModelHandler),
    (r'/api/db_item_model', DBItemModelHandler),
    (r'/api/item_key', ItemKey),
    (r'/api/token', TokenHandler),
    (r'/api/zbx_item', ZbxItemHandler),
    (r'/api/zbx_host_group', ZbxHostGroupHandler),
    (r'/api/zbx_template', ZbxTemplatehaHandler),
    (r'/api/zbx_host', ZbxHostHandler),
    (r'/api/zbx_proxy', ZbxProxyHandler),
    (r'/api/zbx_graph', ZbxGraphHandler),
    (r'/api/zbx_application', ZbxApplicationHandler),
    (r'/api/zbx_screen', ZbxScreenHandler),

)
