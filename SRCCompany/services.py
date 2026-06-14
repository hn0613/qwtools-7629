#coding:utf-8
import time
from SRCCompany.models import CompanyInfo, Subdomain, Webinfo, Server


def generate_record_id(model_class, prefix=''):
    """
    为 CompanyInfo / Subdomain / Webinfo 生成基于时间的记录 ID。
    Server / Port / Plug 使用 Django 自增主键，不需要调用此函数。
    """
    try:
        latest_id = model_class.objects.latest('id').id
    except model_class.DoesNotExist:
        latest_id = 0
    return prefix + time.strftime('%Y%m%d', time.localtime()) + str(latest_id)


def get_parent_or_none(model_class, field_name, field_value):
    """
    安全查找父级记录。
    成功返回 (object, None)，失败返回 (None, error_message)。
    """
    try:
        obj = model_class.objects.get(**{field_name: field_value})
        return obj, None
    except model_class.DoesNotExist:
        return None, u'关联记录不存在 (ID: %s)' % field_value


def get_subdomain_detail(subdomain_id):
    """
    加载子域名详情页所需的全部数据。
    成功返回 (data_dict, None)，失败返回 (None, error_message)。

    返回的 data_dict 严格匹配 WEB_view.html 模板所需的 context 变量：
      subdomain_list  - 包含单个 subdomain 的列表（模板用 for 遍历）
      webinfo_list    - 该子域名下所有 Webinfo
      server_list     - 该子域名下所有 Server
      plug_lists      - 按 webinfo 分组的 Plug 查询集列表
      port_lists      - 按 server 分组的 Port 查询集列表
      subdomain_id    - 子域名 ID 字符串（模板表单 action URL 用）
    """
    try:
        subdomain = Subdomain.objects.select_related(
            'subdomain_company'
        ).get(subdomain_id=subdomain_id)
    except Subdomain.DoesNotExist:
        return None, u'无效的参数'

    webinfo_list = subdomain.web_in_subdomain.prefetch_related('plug_in_webinfo').all()
    server_list = subdomain.server_in_subdomain.prefetch_related('port_in_server').all()

    plug_lists = [web.plug_in_webinfo.all() for web in webinfo_list]
    port_lists = [server.port_in_server.all() for server in server_list]

    return {
        'subdomain_list': [subdomain],
        'webinfo_list': webinfo_list,
        'server_list': server_list,
        'plug_lists': plug_lists,
        'port_lists': port_lists,
        'subdomain_id': subdomain_id,
    }, None
