#coding:utf-8
'''
Created on 2017/12/7

@author: gy
'''
from django.conf.urls import url

from SRCCompany import views

urlpatterns = [
    url(r'^$', views.view_SRC, name='view_SRC'),
    #url(r'^add$', views.add_SRC, name='add_SRC'),
    url(r'^deletesrc/(.+)/$', views.delete_SRC, name='delete_SRC'),
    url(r'^WEB/(.+)', views.view_SubDomain, name='view_WEB'),
    url(r'^deletesubdomain/(.+)/$', views.delete_WEB, name='delete_WEB'),
    url(r'^subdomaininfo/(.+)/$', views.view_WEBinfo, name='view_WEBinfo'),
    url(r'^addweb/(.+)/$', views.Webinfo_add, name='add_webinfo'),
    url(r'^addplug/(.+)/$', views.Plug_add, name='add_webplug'),
    url(r'^addserver/(.+)/$', views.Server_add, name='add_webserver'),
    url(r'^addserverport/(.+)/$', views.Port_add, name='add_serverport'),
    # 编辑路由
    url(r'^editcompany/(\d+)/$', views.Company_edit, name='edit_company'),
    url(r'^editsubdomain/(\d+)/$', views.Subdomain_edit, name='edit_subdomain'),
    url(r'^editwebinfo/(\d+)/$', views.Webinfo_edit, name='edit_webinfo'),
    url(r'^editserver/(\d+)/$', views.Server_edit, name='edit_server'),
    url(r'^editplug/(\d+)/$', views.Plug_edit, name='edit_plug'),
    url(r'^editport/(\d+)/$', views.Port_edit, name='edit_port'),
]