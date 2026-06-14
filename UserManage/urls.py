#coding:utf-8
'''
Created on 2017/11/28

@author: gy071089
'''


from django.urls import re_path

from UserManage import views

urlpatterns = [
    re_path(r'^$', views.signin, name='signin'),
    re_path(r'^regist/$', views.regist, name='regist'),
    re_path(r'^signout/$', views.signout, name='signout'),
]