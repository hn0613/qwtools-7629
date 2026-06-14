#coding:utf-8
'''
Created on 2017/12/7

@author: gy
'''
from django.urls import re_path

from SRCCompany import views

urlpatterns = [
    re_path(r'^$', views.view_SRC, name='view_SRC'),
    #re_path(r'^add$', views.add_SRC, name='add_SRC'),
    re_path(r'^deletesrc/(.+)/$', views.delete_SRC, name='delete_SRC'),
    re_path(r'^WEB/(.+)', views.view_SubDomain, name='view_WEB'),
    re_path(r'^deletesubdomain/(.+)/$', views.delete_WEB, name='delete_WEB'),
    re_path(r'^subdomaininfo/(.+)/$', views.view_WEBinfo, name='view_WEBinfo'),
    re_path(r'^addweb/(.+)/$', views.Webinfo_add, name='add_webinfo'),
    re_path(r'^addplug/(.+)/$', views.Plug_add, name='add_webplug'),
    re_path(r'^addserver/(.+)/$', views.Server_add, name='add_webserver'),
    re_path(r'^addserverport/(.+)/$', views.Port_add, name='add_serverport'),
]