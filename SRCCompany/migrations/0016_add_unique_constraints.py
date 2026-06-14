# -*- coding: utf-8 -*-
"""
结构迁移：添加唯一约束

确保身份键在数据库层面有约束，防止任何入口绕过 services.py 的去重逻辑。
"""
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SRCCompany', '0015_deduplicate_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='companyinfo',
            name='company_src_www',
            field=models.URLField(unique=True, verbose_name='应急中心地址'),
        ),
        migrations.AlterUniqueTogether(
            name='subdomain',
            unique_together=set([('subdomain_company', 'subdomain_www')]),
        ),
        migrations.AlterUniqueTogether(
            name='webinfo',
            unique_together=set([('web_subdomain', 'web_url')]),
        ),
        migrations.AlterUniqueTogether(
            name='server',
            unique_together=set([('server_subdomain', 'server_ip')]),
        ),
        migrations.AlterUniqueTogether(
            name='port',
            unique_together=set([('port_server', 'port')]),
        ),
        migrations.AlterUniqueTogether(
            name='plug',
            unique_together=set([('plug_webinfo', 'plug_name')]),
        ),
    ]
