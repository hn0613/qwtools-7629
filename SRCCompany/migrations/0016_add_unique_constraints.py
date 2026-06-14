#coding:utf-8
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('SRCCompany', '0015_deduplicate_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='companyinfo',
            name='company_name',
            field=models.CharField(max_length=50, unique=True, verbose_name='企业名称'),
        ),
        migrations.AlterField(
            model_name='subdomain',
            name='subdomain_company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subdomain_in_company', to='SRCCompany.CompanyInfo'),
        ),
        migrations.AlterField(
            model_name='webinfo',
            name='web_subdomain',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='web_in_subdomain', to='SRCCompany.Subdomain'),
        ),
        migrations.AlterField(
            model_name='server',
            name='server_company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='server_in_company', to='SRCCompany.CompanyInfo'),
        ),
        migrations.AlterField(
            model_name='server',
            name='server_subdomain',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='server_in_subdomain', to='SRCCompany.Subdomain'),
        ),
        migrations.AlterField(
            model_name='port',
            name='port_server',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='port_in_server', to='SRCCompany.Server', verbose_name='服务器关联'),
        ),
        migrations.AlterField(
            model_name='plug',
            name='plug_webinfo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='plug_in_webinfo', to='SRCCompany.Webinfo', verbose_name='网页关联'),
        ),
        migrations.AlterUniqueTogether(
            name='subdomain',
            unique_together={('subdomain_www', 'subdomain_company')},
        ),
        migrations.AlterUniqueTogether(
            name='webinfo',
            unique_together={('web_url', 'web_subdomain')},
        ),
        migrations.AlterUniqueTogether(
            name='server',
            unique_together={('server_ip', 'server_subdomain')},
        ),
        migrations.AlterUniqueTogether(
            name='port',
            unique_together={('port', 'port_server')},
        ),
        migrations.AlterUniqueTogether(
            name='plug',
            unique_together={('plug_name', 'plug_webinfo')},
        ),
    ]
