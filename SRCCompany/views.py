#coding:utf-8
from django.shortcuts import render, HttpResponseRedirect
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required

from SRCCompany.models import CompanyInfo
from SRCCompany.forms import (
    CompanyInfoForms, SubDomainForms,
    WebinfoForms, ServerForms, PlugForms, PortForms
)
from SRCCompany import services
from SRCCompany.utils import paginate


# Create your views here.
@csrf_protect
@login_required
def view_SRC(request):
    '''
    企业列表 + 添加企业。
    POST 表单无效时落到 GET 路径，模板直接显示表单校验错误，
    不再用 error 变量，消除原来非 GET/POST 时 UnboundLocalError 的崩溃。
    '''
    if request.method == "POST":
        form = CompanyInfoForms(request.POST)
        if form.is_valid():
            services.create_company(form)
            return HttpResponseRedirect('/SRC')
        # 表单无效：落到下方 GET 路径，模板渲染时会显示表单错误
    else:
        form = CompanyInfoForms()

    SRC_lists = CompanyInfo.objects.all().order_by('company_updatetime')
    SRC_list = paginate(SRC_lists, request.GET.get('page'))
    return render(request, 'SRCinfo/SRC_view.html', {
        'SRC_list': SRC_list,
        'form': form,
    })


@login_required
def delete_SRC(request, company_id):
    '''
    删除企业。通过 services 层查找，找不到时返回 404 而非 500。
    '''
    services.delete_company(company_id)
    return HttpResponseRedirect('/SRC')


@csrf_protect
@login_required
def view_SubDomain(request, company_id):
    '''
    子域名列表 + 添加子域名。
    通过 services 查找上级企业，找不到时 404。
    '''
    company = services.get_company_or_404(company_id)

    if request.method == "POST":
        form = SubDomainForms(request.POST)
        if form.is_valid():
            services.create_subdomain(form, company)
            return HttpResponseRedirect('/SRC/WEB/' + company_id)
        # 表单无效：落到下方 GET 路径
    else:
        form = SubDomainForms()

    SubDomain_lists = company.subdomain_in_company.all().order_by('subdomain_updatetime')
    WEB_list = paginate(SubDomain_lists, request.GET.get('page'))
    return render(request, 'SRCinfo/SubDomain.html', {
        'WEB_list': WEB_list,
        'form': form,
    })


@login_required
def delete_WEB(request, subdomain_id):
    '''
    删除子域名，重定向到所属企业的子域名列表。
    通过 services 层查找并返回 company_id，找不到时 404。
    '''
    company_id = services.delete_subdomain(subdomain_id)
    return HttpResponseRedirect('/SRC/WEB/' + str(company_id))


@login_required
def view_WEBinfo(request, subdomain_id):
    '''
    详情页：子域名 + 网站(含组件) + 服务器(含端口)。

    通过 services.get_subdomain_detail 一次性预取完整资产链，
    替代原来 .filter() + for 循环 + N+1 查询的拼法。
    plug_lists / port_lists 保持 list-of-QuerySets 格式兼容模板，
    但数据来自预取，无额外查询。
    '''
    subdomain = services.get_subdomain_detail(subdomain_id)

    # 构建带范围限制的表单：组件下拉只显示当前子域名的网站，
    # 端口下拉只显示当前子域名的服务器
    web_form = WebinfoForms()
    plug_form = PlugForms(subdomain_id=subdomain_id)
    server_form = ServerForms()
    port_form = PortForms(subdomain_id=subdomain_id)

    webinfo_list = subdomain.web_in_subdomain.all()
    server_list = subdomain.server_in_subdomain.all()

    data = {
        'subdomain': subdomain,
        'subdomain_list': [subdomain],  # 兼容模板 {% for subdomain in subdomain_list %}
        'webinfo_list': webinfo_list,
        'server_list': server_list,
        'plug_lists': [web.plug_in_webinfo.all() for web in webinfo_list],
        'port_lists': [server.port_in_server.all() for server in server_list],
        'web_form': web_form,
        'plug_form': plug_form,
        'server_form': server_form,
        'port_form': port_form,
        'subdomain_id': subdomain_id,
        'subdomain_www': subdomain.subdomain_www,  # 修复模板 line 102 死变量
    }
    return render(request, 'SRCinfo/WEB_view.html', data)


@csrf_protect
@login_required
def Webinfo_add(request, subdomain_id):
    '''
    在指定子域名下添加网站。
    通过 services 查找上级子域名，找不到时 404 而非 500。
    '''
    if request.method != "POST":
        return render(request, 'error.html', {'error': '请求错误'})

    subdomain = services.get_subdomain_or_404(subdomain_id)
    form = WebinfoForms(request.POST)
    if form.is_valid():
        services.create_webinfo(form, subdomain)
        return HttpResponseRedirect('/SRC/subdomaininfo/' + str(subdomain_id))

    return render(request, 'error.html', {'error': '添加失败，请检查输入'})


@csrf_protect
@login_required
def Plug_add(request, subdomain_id):
    '''
    添加组件。
    表单接收 subdomain_id 以限制网站下拉范围并做服务端校验，
    去掉了原来从 cleaned_data 取 web_id 再 Webinfo.objects.get() 的冗余查询。
    '''
    if request.method != "POST":
        return render(request, 'error.html', {'error': '请求错误'})

    services.get_subdomain_or_404(subdomain_id)
    form = PlugForms(request.POST, subdomain_id=subdomain_id)
    if form.is_valid():
        services.create_plug(form)
        return HttpResponseRedirect('/SRC/subdomaininfo/' + str(subdomain_id))

    return render(request, 'error.html', {'error': '添加失败，请检查输入'})


@csrf_protect
@login_required
def Server_add(request, subdomain_id):
    '''
    在指定子域名下添加服务器。
    services 层通过 subdomain.subdomain_company 直取企业对象，
    去掉了原来先取 company_id 再 CompanyInfo.objects.get() 的冗余查询。
    '''
    if request.method != "POST":
        return render(request, 'error.html', {'error': '请求错误'})

    subdomain = services.get_subdomain_or_404(subdomain_id)
    form = ServerForms(request.POST)
    if form.is_valid():
        services.create_server(form, subdomain)
        return HttpResponseRedirect('/SRC/subdomaininfo/' + str(subdomain_id))

    return render(request, 'error.html', {'error': '添加失败，请检查输入'})


@csrf_protect
@login_required
def Port_add(request, subdomain_id):
    '''
    添加端口。
    表单接收 subdomain_id 以限制服务器下拉范围并做服务端校验。
    '''
    if request.method != "POST":
        return render(request, 'error.html', {'error': '请求错误'})

    services.get_subdomain_or_404(subdomain_id)
    form = PortForms(request.POST, subdomain_id=subdomain_id)
    if form.is_valid():
        services.create_port(form)
        return HttpResponseRedirect('/SRC/subdomaininfo/' + str(subdomain_id))

    return render(request, 'error.html', {'error': '添加失败，请检查输入'})
