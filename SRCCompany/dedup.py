#coding:utf-8
from django.db import IntegrityError


def smart_get_or_create(model, lookup, defaults=None):
    """
    :param model: Django Model class
    :param lookup: dict, natural key fields for duplicate detection
    :param defaults: dict, non-key fields to set/update
    :return: (instance, created) - created=True if new, False if existing was updated
    """
    if defaults is None:
        defaults = {}

    obj = model.objects.filter(**lookup).first()
    if obj is not None:
        updated = False
        for key, value in defaults.items():
            if value is not None and value != '':
                old_value = getattr(obj, key, None)
                if old_value != value:
                    setattr(obj, key, value)
                    updated = True
        if updated:
            obj.save()
        return obj, False

    create_kwargs = {}
    create_kwargs.update(lookup)
    create_kwargs.update(defaults)
    try:
        obj = model.objects.create(**create_kwargs)
    except IntegrityError:
        obj = model.objects.filter(**lookup).first()
        if obj is None:
            raise
        return obj, False
    return obj, True
