"""SRCINFO URL Configuration"""
from django.urls import re_path, include


urlpatterns = [
    re_path(r'^', include('UserManage.urls')),
    re_path(r'^SRC/', include('SRCCompany.urls')),
]
