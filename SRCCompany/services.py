#coding:utf-8
"""
集中去重服务模块

所有资产创建的入口都通过本模块完成去重和合并，
避免去重逻辑分散在各个视图中各写一套。

每个 find_or_merge_* 函数返回三元组：
    (object, created, merged)
    - object:  最终保留/创建的记录
    - created: 是否为全新创建
    - merged:  是否命中了已有记录并做了合并
"""
import time
import uuid

from SRCCompany.models import (
    CompanyInfo, Subdomain, Webinfo, Server, Port, Plug,
)


# ---------------------------------------------------------------------------
# 内部工具
# ---------------------------------------------------------------------------

def _make_id(prefix=''):
    """生成编号：日期 + 8位随机hex，避免并发碰撞。"""
    date_part = time.strftime('%Y%m%d', time.localtime(time.time()))
    rand_part = uuid.uuid4().hex[:8]
    return prefix + date_part + rand_part


def _fill_blank(target, field, value):
    """只在目标字段为空时填充（补缺策略）。"""
    current = getattr(target, field, None)
    if (current is None or current == '') and value is not None and value != '':
        setattr(target, field, value)


def _overwrite(target, field, value):
    """用新值覆盖旧值（更新策略），但跳过 None / 空串。"""
    if value is not None and value != '':
        setattr(target, field, value)


# ---------------------------------------------------------------------------
# CompanyInfo  —  身份键: company_src_www（全局，不区分大小写）
# ---------------------------------------------------------------------------

def find_or_merge_company(cleaned_data):
    """
    按 company_src_www 去重。
    重复时采用"补缺"策略：只填充空字段。
    """
    src_www = cleaned_data.get('company_src_www', '').strip()

    existing = CompanyInfo.objects.filter(
        company_src_www__iexact=src_www,
    ).first()

    if existing:
        _fill_blank(existing, 'company_src_name', cleaned_data.get('company_src_name'))
        _fill_blank(existing, 'company_name', cleaned_data.get('company_name'))
        _fill_blank(existing, 'company_www', cleaned_data.get('company_www'))
        _fill_blank(existing, 'company_ioc', cleaned_data.get('company_ioc'))
        existing.save()
        return existing, False, True

    company_id = int(time.strftime('%Y%m%d', time.localtime(time.time()))
                     + str(uuid.uuid4().int)[:4])
    obj = CompanyInfo.objects.create(
        company_id=company_id,
        company_src_name=cleaned_data.get('company_src_name', ''),
        company_src_www=src_www,
        company_name=cleaned_data.get('company_name', ''),
        company_www=cleaned_data.get('company_www', ''),
        company_ioc=cleaned_data.get('company_ioc'),
    )
    return obj, True, False


# ---------------------------------------------------------------------------
# Subdomain  —  身份键: (subdomain_company, subdomain_www)
# ---------------------------------------------------------------------------

def find_or_merge_subdomain(cleaned_data, company):
    """
    在同一公司下按 subdomain_www 去重。
    重复时采用"补缺"策略。
    """
    www = cleaned_data.get('subdomain_www', '').strip()

    existing = Subdomain.objects.filter(
        subdomain_company=company,
        subdomain_www__iexact=www,
    ).first()

    if existing:
        _fill_blank(existing, 'subdomain_name', cleaned_data.get('subdomain_name'))
        existing.save()
        return existing, False, True

    subdomain_id = 'sd' + time.strftime('%Y%m%d', time.localtime(time.time())) \
                   + uuid.uuid4().hex[:8]
    obj = Subdomain.objects.create(
        subdomain_id=subdomain_id,
        subdomain_name=cleaned_data.get('subdomain_name'),
        subdomain_www=www,
        subdomain_company=company,
    )
    return obj, True, False


# ---------------------------------------------------------------------------
# Webinfo  —  身份键: (web_subdomain, web_url)
# ---------------------------------------------------------------------------

def find_or_merge_webinfo(cleaned_data, subdomain):
    """
    在同一子域名下按 web_url 去重。
    重复时采用"更新"策略：技术字段用新值覆盖。
    """
    url = cleaned_data.get('web_url', '').strip()

    existing = Webinfo.objects.filter(
        web_subdomain=subdomain,
        web_url__iexact=url,
    ).first()

    if existing:
        _overwrite(existing, 'web_front', cleaned_data.get('web_front'))
        _overwrite(existing, 'web_language', cleaned_data.get('web_language'))
        _overwrite(existing, 'web_framework', cleaned_data.get('web_framework'))
        _overwrite(existing, 'web_template', cleaned_data.get('web_template'))
        _overwrite(existing, 'web_container', cleaned_data.get('web_container'))
        existing.save()
        return existing, False, True

    web_id = time.strftime('%Y%m%d', time.localtime(time.time())) \
             + uuid.uuid4().hex[:8]
    obj = Webinfo.objects.create(
        web_id=web_id,
        web_url=url,
        web_front=cleaned_data.get('web_front'),
        web_language=cleaned_data.get('web_language'),
        web_framework=cleaned_data.get('web_framework'),
        web_template=cleaned_data.get('web_template'),
        web_container=cleaned_data.get('web_container'),
        web_subdomain=subdomain,
    )
    return obj, True, False


# ---------------------------------------------------------------------------
# Server  —  身份键: (server_subdomain, server_ip)
# ---------------------------------------------------------------------------

def find_or_merge_server(cleaned_data, subdomain, company):
    """
    在同一子域名下按 server_ip 去重。
    重复时采用"更新"策略。
    """
    ip = cleaned_data.get('server_ip', '').strip()

    existing = Server.objects.filter(
        server_subdomain=subdomain,
        server_ip=ip,
    ).first()

    if existing:
        _overwrite(existing, 'server_name', cleaned_data.get('server_name'))
        _overwrite(existing, 'server_os', cleaned_data.get('server_os'))
        existing.save()
        return existing, False, True

    obj = Server.objects.create(
        server_name=cleaned_data.get('server_name'),
        server_ip=ip,
        server_os=cleaned_data.get('server_os'),
        server_subdomain=subdomain,
        server_company=company,
    )
    return obj, True, False


# ---------------------------------------------------------------------------
# Port  —  身份键: (port_server, port)
# ---------------------------------------------------------------------------

def find_or_merge_port(cleaned_data, server):
    """
    在同一服务器下按 port 去重。
    重复时采用"更新"策略。
    """
    port_val = cleaned_data.get('port', '').strip()

    existing = Port.objects.filter(
        port_server=server,
        port=port_val,
    ).first()

    if existing:
        _overwrite(existing, 'name', cleaned_data.get('name'))
        _overwrite(existing, 'product', cleaned_data.get('product'))
        _overwrite(existing, 'version', cleaned_data.get('version'))
        existing.save()
        return existing, False, True

    obj = Port.objects.create(
        name=cleaned_data.get('name'),
        port=port_val,
        product=cleaned_data.get('product'),
        version=cleaned_data.get('version'),
        cpe=cleaned_data.get('cpe'),
        port_server=server,
    )
    return obj, True, False


# ---------------------------------------------------------------------------
# Plug  —  身份键: (plug_webinfo, plug_name)
# ---------------------------------------------------------------------------

def find_or_merge_plug(cleaned_data, webinfo):
    """
    在同一网页下按 plug_name 去重。
    重复时采用"更新"策略。
    """
    name = cleaned_data.get('plug_name', '').strip()

    existing = Plug.objects.filter(
        plug_webinfo=webinfo,
        plug_name__iexact=name,
    ).first()

    if existing:
        _overwrite(existing, 'plug_version', cleaned_data.get('plug_version'))
        existing.save()
        return existing, False, True

    obj = Plug.objects.create(
        plug_name=name,
        plug_version=cleaned_data.get('plug_version'),
        plug_webinfo=webinfo,
    )
    return obj, True, False
