#coding:utf-8
from django.db import migrations


def _merge_duplicates(apps, model_name, natural_key_fields, child_fk_mappings):
    """
    Generic duplicate merger.

    :param model_name: e.g. 'CompanyInfo'
    :param natural_key_fields: list of field names forming the natural key
    :param child_fk_mappings: list of (ChildModelName, fk_field_name) tuples
    """
    Model = apps.get_model('SRCCompany', model_name)
    seen = {}

    for obj in Model.objects.all().order_by('id'):
        key = tuple(getattr(obj, f) if not hasattr(getattr(obj, f), 'pk')
                     else getattr(obj, f).pk
                     for f in natural_key_fields)
        if key in seen:
            keeper = seen[key]
            for child_model_name, fk_field in child_fk_mappings:
                ChildModel = apps.get_model('SRCCompany', child_model_name)
                ChildModel.objects.filter(**{fk_field: obj.pk}).update(**{fk_field: keeper.pk})
            obj.delete()
        else:
            seen[key] = obj


def deduplicate_forward(apps, schema_editor):
    _merge_duplicates(apps, 'CompanyInfo',
                      ['company_name'],
                      [('Subdomain', 'subdomain_company_id'),
                       ('Server', 'server_company_id')])

    _merge_duplicates(apps, 'Subdomain',
                      ['subdomain_www', 'subdomain_company_id'],
                      [('Webinfo', 'web_subdomain_id'),
                       ('Server', 'server_subdomain_id')])

    _merge_duplicates(apps, 'Webinfo',
                      ['web_url', 'web_subdomain_id'],
                      [('Plug', 'plug_webinfo_id')])

    _merge_duplicates(apps, 'Server',
                      ['server_ip', 'server_subdomain_id'],
                      [('Port', 'port_server_id')])

    _merge_duplicates(apps, 'Port',
                      ['port', 'port_server_id'],
                      [])

    _merge_duplicates(apps, 'Plug',
                      ['plug_name', 'plug_webinfo_id'],
                      [])


class Migration(migrations.Migration):

    dependencies = [
        ('SRCCompany', '0014_auto_20171211_0040'),
    ]

    operations = [
        migrations.RunPython(deduplicate_forward, migrations.RunPython.noop),
    ]
