# -*- coding: utf-8 -*-
"""
数据迁移：清理历史重复记录

对每个模型按身份键分组，同组保留 id 最大的一条，
把其余记录的子级关联转移过去后再删除。
"""
from __future__ import unicode_literals

from django.db import migrations


def _dedup_company(apps, schema_editor):
    """CompanyInfo: 按 company_src_www 去重（不区分大小写）"""
    CompanyInfo = apps.get_model('SRCCompany', 'CompanyInfo')
    Subdomain = apps.get_model('SRCCompany', 'Subdomain')
    Server = apps.get_model('SRCCompany', 'Server')

    seen = {}
    for obj in CompanyInfo.objects.all().order_by('id'):
        key = (obj.company_src_www or '').lower().strip()
        if not key:
            continue
        if key in seen:
            keeper = seen[key]
            Subdomain.objects.filter(subdomain_company=obj).update(subdomain_company=keeper)
            Server.objects.filter(server_company=obj).update(server_company=keeper)
            obj.delete()
        else:
            seen[key] = obj


def _dedup_subdomain(apps, schema_editor):
    """Subdomain: 按 (subdomain_company, subdomain_www) 去重"""
    Subdomain = apps.get_model('SRCCompany', 'Subdomain')
    Webinfo = apps.get_model('SRCCompany', 'Webinfo')
    Server = apps.get_model('SRCCompany', 'Server')

    seen = {}
    for obj in Subdomain.objects.all().order_by('id'):
        key = (obj.subdomain_company_id, (obj.subdomain_www or '').lower().strip())
        if key in seen:
            keeper = seen[key]
            Webinfo.objects.filter(web_subdomain=obj).update(web_subdomain=keeper)
            Server.objects.filter(server_subdomain=obj).update(server_subdomain=keeper)
            obj.delete()
        else:
            seen[key] = obj


def _dedup_webinfo(apps, schema_editor):
    """Webinfo: 按 (web_subdomain, web_url) 去重"""
    Webinfo = apps.get_model('SRCCompany', 'Webinfo')
    Plug = apps.get_model('SRCCompany', 'Plug')

    seen = {}
    for obj in Webinfo.objects.all().order_by('id'):
        key = (obj.web_subdomain_id, (obj.web_url or '').lower().strip())
        if key in seen:
            keeper = seen[key]
            Plug.objects.filter(plug_webinfo=obj).update(plug_webinfo=keeper)
            obj.delete()
        else:
            seen[key] = obj


def _dedup_server(apps, schema_editor):
    """Server: 按 (server_subdomain, server_ip) 去重"""
    Server = apps.get_model('SRCCompany', 'Server')
    Port = apps.get_model('SRCCompany', 'Port')

    seen = {}
    for obj in Server.objects.all().order_by('id'):
        key = (obj.server_subdomain_id, (obj.server_ip or '').strip())
        if key in seen:
            keeper = seen[key]
            Port.objects.filter(port_server=obj).update(port_server=keeper)
            obj.delete()
        else:
            seen[key] = obj


def _dedup_port(apps, schema_editor):
    """Port: 按 (port_server, port) 去重 — 叶子节点，直接删"""
    Port = apps.get_model('SRCCompany', 'Port')

    seen = {}
    for obj in Port.objects.all().order_by('id'):
        key = (obj.port_server_id, (obj.port or '').strip())
        if key in seen:
            obj.delete()
        else:
            seen[key] = obj


def _dedup_plug(apps, schema_editor):
    """Plug: 按 (plug_webinfo, plug_name) 去重 — 叶子节点，直接删"""
    Plug = apps.get_model('SRCCompany', 'Plug')

    seen = {}
    for obj in Plug.objects.all().order_by('id'):
        key = (obj.plug_webinfo_id, (obj.plug_name or '').lower().strip())
        if key in seen:
            obj.delete()
        else:
            seen[key] = obj


def deduplicate_all(apps, schema_editor):
    """按层级从上到下依次去重"""
    _dedup_company(apps, schema_editor)
    _dedup_subdomain(apps, schema_editor)
    _dedup_webinfo(apps, schema_editor)
    _dedup_server(apps, schema_editor)
    _dedup_port(apps, schema_editor)
    _dedup_plug(apps, schema_editor)


def noop_reverse(apps, schema_editor):
    """去重不可逆，反向为空"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('SRCCompany', '0014_auto_20171211_0040'),
    ]

    operations = [
        migrations.RunPython(deduplicate_all, noop_reverse),
    ]
