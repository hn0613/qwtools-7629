#coding:utf-8
'''
Created on 2017/12/7

@author: gy071089
'''

from django.forms import ModelForm
from SRCCompany.models import CompanyInfo,Subdomain
from SRCCompany.models import Webinfo,Server,Port,Plug
from django.forms.widgets import TextInput,URLInput,Select


class CompanyInfoForms(ModelForm):
    class Meta:
        model = CompanyInfo
        exclude = ['company_id','company_starttime','company_updatetime']
        widgets = {
                   'company_src_name': TextInput(attrs={'class':'form-control','placeholder':'XX安全中心'}),
                   'company_src_www': URLInput(attrs={'class':'form-control','placeholder':'https://xxxx.xx'}),
                   'company_name': TextInput(attrs={'class':'form-control','placeholder':'XX公司'}),
                   'company_www': URLInput(attrs={'class':'form-control','placeholder':'https://xxxx.xx'}),
                   'company_ioc': TextInput(attrs={'class':'form-control','placeholder':'https://xxxx.xx/xx.png'}),
                   }

    def clean_company_src_www(self):
        """归一化SRC地址：去空格、统一小写"""
        val = self.cleaned_data.get('company_src_www', '')
        return val.strip().lower() if val else val


class SubDomainForms(ModelForm):
    class Meta:
        model = Subdomain
        exclude = ['subdomain_company','subdomain_starttime','subdomain_updatetime','subdomain_id']
        widgets = {
                   'subdomain_name': TextInput(attrs={'class':'form-control','placeholder':'子域名名称'}),
                   'subdomain_www': URLInput(attrs={'class':'form-control','placeholder':'https://xxxx.xx'}),
                   }

    def clean_subdomain_www(self):
        """归一化子域名地址"""
        val = self.cleaned_data.get('subdomain_www', '')
        return val.strip().lower() if val else val


class WebinfoForms(ModelForm):
    class Meta:
        model = Webinfo
        exclude = ['web_subdomain','web_id','web_starttime','web_updatetime']
        widgets = {
                   'web_url': URLInput(attrs={'class':'form-control','placeholder':'网页链接'}),
                   'web_front': TextInput(attrs={'class':'form-control','placeholder':'前端语言'}),
                   'web_language': TextInput(attrs={'class':'form-control','placeholder':'开发语言'}),
                   'web_framework': TextInput(attrs={'class':'form-control','placeholder':'开发框架'}),
                   'web_template': TextInput(attrs={'class':'form-control','placeholder':'网站模板'}),
                   'web_container': TextInput(attrs={'class':'form-control','placeholder':'WEB容器'}),
                   }

    def clean_web_url(self):
        """归一化网页链接"""
        val = self.cleaned_data.get('web_url', '')
        return val.strip().lower() if val else val


class ServerForms(ModelForm):
    class Meta:
        model = Server
        exclude = ['server_company','server_subdomain','server_starttime','server_updatetime']
        widgets = {
                   'server_name': TextInput(attrs={'class':'form-control','placeholder':'服务器名称'}),
                   'server_ip': TextInput(attrs={'class':'form-control','placeholder':'服务器IP'}),
                   'server_os': TextInput(attrs={'class':'form-control','placeholder':'操作系统'}),
                   }

    def clean_server_ip(self):
        """归一化服务器IP"""
        val = self.cleaned_data.get('server_ip', '')
        return val.strip() if val else val


class PlugForms(ModelForm):
    class Meta:
        model = Plug
        exclude = ['plug_starttime','plug_updatetime']
        widgets = {
                   'plug_name': TextInput(attrs={'class':'form-control','placeholder':'组件名称'}),
                   'plug_version': TextInput(attrs={'class':'form-control','placeholder':'组件版本'}),
                   'plug_webinfo': Select(attrs={'class':'form-control'}),
                   }

    def clean_plug_name(self):
        """归一化组件名称"""
        val = self.cleaned_data.get('plug_name', '')
        return val.strip().lower() if val else val


class PortForms(ModelForm):
    class Meta:
        model = Port
        exclude = ['cpe',]
        widgets = {
                   'name': TextInput(attrs={'class':'form-control','placeholder':'应用名称'}),
                   'port': TextInput(attrs={'class':'form-control','placeholder':'开放端口'}),
                   'product': TextInput(attrs={'class':'form-control','placeholder':'对应服务'}),
                   'version': TextInput(attrs={'class':'form-control','placeholder':'应用版本'}),
                   'port_server': Select(attrs={'class':'form-control'}),
                   }

    def clean_port(self):
        """归一化端口号"""
        val = self.cleaned_data.get('port', '')
        return val.strip() if val else val
