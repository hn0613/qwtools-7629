#coding:utf-8
"""
资产链操作层。

所有涉及资产链（企业→子域名→网站/服务器→组件/端口）的读写操作
都集中在这里，views.py 不再直接调用 Model.objects。
"""
from django.shortcuts import get_object_or_404

from SRCCompany.models import (
    CompanyInfo, Subdomain, Webinfo, Server, Port, Plug
)
from SRCCompany.utils import generate_id


# ---------------------------------------------------------------------------
# 详情页：一次性取回子域名及其完整资产链
# ---------------------------------------------------------------------------

def get_subdomain_detail(subdomain_id):
    """
    取单个子域名及其完整关联数据，供详情页使用。

    替代 view_WEBinfo 中 .filter() + for 循环 + N+1 查询的逻辑。
    通过 select_related / prefetch_related 把查询降到固定次数，
    且每个 web/server 对象自带预取的 plugs/ports。

    Args:
        subdomain_id: 子域名 ID 字符串（如 'sd202606140'）。

    Returns:
        单个 Subdomain 对象（关系已预取）。

    Raises:
        Http404（通过 get_object_or_404）。
    """
    return get_object_or_404(
        Subdomain.objects
            .select_related('subdomain_company')
            .prefetch_related(
                'web_in_subdomain__plug_in_webinfo',
                'server_in_subdomain__port_in_server',
            ),
        subdomain_id=subdomain_id
    )


# ---------------------------------------------------------------------------
# 上级查找：统一用 404 替代 500
# ---------------------------------------------------------------------------

def get_company_or_404(company_id):
    """
    按 company_id 查找企业，找不到则 404。

    替代 view_SubDomain 和 delete_SRC 中无保护的 .get() 调用。
    """
    return get_object_or_404(CompanyInfo, company_id=company_id)


def get_subdomain_or_404(subdomain_id):
    """
    按 subdomain_id 查找子域名并预取企业信息，找不到则 404。

    供 Webinfo_add、Server_add 等新增视图使用。
    select_related 避免了后续需要 .subdomain_company 时的二次查询。
    """
    return get_object_or_404(
        Subdomain.objects.select_related('subdomain_company'),
        subdomain_id=subdomain_id
    )


# ---------------------------------------------------------------------------
# 实体创建：每个模型一个函数
# ---------------------------------------------------------------------------

def create_company(form):
    """
    从验证通过的 CompanyInfoForms 创建企业。

    用 create() 替代原来的 get_or_create(全字段)：
    由于 company_id 每次都是时间戳+自增拼出来的，
    get_or_create 的全字段匹配永远只会走到 create，语义等价。
    """
    company_id = generate_id(CompanyInfo)
    return CompanyInfo.objects.create(
        company_id=company_id,
        company_src_name=form.cleaned_data['company_src_name'],
        company_src_www=form.cleaned_data['company_src_www'],
        company_name=form.cleaned_data['company_name'],
        company_www=form.cleaned_data['company_www'],
        company_ioc=form.cleaned_data['company_ioc'],
    )


def create_subdomain(form, company):
    """
    在指定企业下创建子域名。

    Args:
        form: 验证通过的 SubDomainForms。
        company: 已解析的 CompanyInfo 对象。
    """
    subdomain_id = generate_id(Subdomain, prefix='sd')
    return Subdomain.objects.create(
        subdomain_id=subdomain_id,
        subdomain_name=form.cleaned_data['subdomain_name'],
        subdomain_www=form.cleaned_data['subdomain_www'],
        subdomain_company=company,
    )


def create_webinfo(form, subdomain):
    """
    在指定子域名下创建网站。

    Args:
        form: 验证通过的 WebinfoForms。
        subdomain: 已解析的 Subdomain 对象。
    """
    web_id = generate_id(Webinfo)
    return Webinfo.objects.create(
        web_id=web_id,
        web_url=form.cleaned_data['web_url'],
        web_front=form.cleaned_data['web_front'],
        web_language=form.cleaned_data['web_language'],
        web_framework=form.cleaned_data['web_framework'],
        web_template=form.cleaned_data['web_template'],
        web_container=form.cleaned_data['web_container'],
        web_subdomain=subdomain,
    )


def create_plug(form):
    """
    创建组件。

    直接用 form.cleaned_data['plug_webinfo']（已经是 Webinfo 对象），
    去掉了原来先取 web_id 再 Webinfo.objects.get(web_id=web_id) 的冗余查询。
    """
    return Plug.objects.create(
        plug_name=form.cleaned_data['plug_name'],
        plug_version=form.cleaned_data['plug_version'],
        plug_webinfo=form.cleaned_data['plug_webinfo'],
    )


def create_server(form, subdomain):
    """
    在指定子域名下创建服务器。

    通过 subdomain.subdomain_company 直取企业对象（select_related 已加载），
    去掉了原来先取 company_id 再 CompanyInfo.objects.get() 的冗余查询。
    """
    return Server.objects.create(
        server_name=form.cleaned_data['server_name'],
        server_ip=form.cleaned_data['server_ip'],
        server_os=form.cleaned_data['server_os'],
        server_subdomain=subdomain,
        server_company=subdomain.subdomain_company,
    )


def create_port(form):
    """
    创建端口。

    直接用 form.cleaned_data['port_server']（已经是 Server 对象）。
    """
    return Port.objects.create(
        name=form.cleaned_data['name'],
        port=form.cleaned_data['port'],
        product=form.cleaned_data['product'],
        version=form.cleaned_data['version'],
        port_server=form.cleaned_data['port_server'],
    )


# ---------------------------------------------------------------------------
# 删除
# ---------------------------------------------------------------------------

def delete_company(company_id):
    """
    按 company_id 删除企业，找不到则 404。
    """
    company = get_object_or_404(CompanyInfo, company_id=company_id)
    company.delete()


def delete_subdomain(subdomain_id):
    """
    按 subdomain_id 删除子域名，返回所属企业 company_id 供重定向用。
    找不到则 404。
    """
    subdomain = get_object_or_404(
        Subdomain.objects.select_related('subdomain_company'),
        subdomain_id=subdomain_id
    )
    company_id = subdomain.subdomain_company.company_id
    subdomain.delete()
    return company_id
