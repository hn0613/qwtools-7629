#coding:utf-8
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

class SubDomainForms(ModelForm):
    class Meta:
        model = Subdomain
        exclude = ['subdomain_company','subdomain_starttime','subdomain_updatetime','subdomain_id']
        widgets = {
                   'subdomain_name': TextInput(attrs={'class':'form-control','placeholder':'子域名名称'}),
                   'subdomain_www': URLInput(attrs={'class':'form-control','placeholder':'https://xxxx.xx'}),
                   }

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

class ServerForms(ModelForm):
    class Meta:
        model = Server
        exclude = ['server_company','server_subdomain','server_starttime','server_updatetime']
        widgets = {
                   'server_name': TextInput(attrs={'class':'form-control','placeholder':'服务器名称'}),
                   'server_ip': TextInput(attrs={'class':'form-control','placeholder':'服务器IP'}),
                   'server_os': TextInput(attrs={'class':'form-control','placeholder':'操作系统'}),
                   }

class PlugForms(ModelForm):
    class Meta:
        model = Plug
        exclude = ['plug_starttime','plug_updatetime']
        widgets = {
                   'plug_name': TextInput(attrs={'class':'form-control','placeholder':'组件名称'}),
                   'plug_version': TextInput(attrs={'class':'form-control','placeholder':'组件版本'}),
                   'plug_webinfo': Select(attrs={'class':'form-control'}),
                   }

    def __init__(self, *args, **kwargs):
        """
        接收可选参数 subdomain_id，限制组件关联的网站下拉框
        只显示当前子域名下的网站，防止跨子域名提交。
        不传时行为与原来一致（显示全部网站）。
        """
        subdomain_id = kwargs.pop('subdomain_id', None)
        super(PlugForms, self).__init__(*args, **kwargs)
        if subdomain_id:
            self.fields['plug_webinfo'].queryset = Webinfo.objects.filter(
                web_subdomain__subdomain_id=subdomain_id
            )

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

    def __init__(self, *args, **kwargs):
        """
        接收可选参数 subdomain_id，限制端口关联的服务器下拉框
        只显示当前子域名下的服务器，防止跨子域名提交。
        不传时行为与原来一致（显示全部服务器）。
        """
        subdomain_id = kwargs.pop('subdomain_id', None)
        super(PortForms, self).__init__(*args, **kwargs)
        if subdomain_id:
            self.fields['port_server'].queryset = Server.objects.filter(
                server_subdomain__subdomain_id=subdomain_id
            )
