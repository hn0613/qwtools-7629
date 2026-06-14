#coding:utf-8
from django.shortcuts import render,HttpResponseRedirect
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from SRCCompany.models import CompanyInfo,Subdomain,Webinfo,Server,Port,Plug
from SRCCompany.forms import CompanyInfoForms,SubDomainForms
from SRCCompany.forms import WebinfoForms,ServerForms,PlugForms,PortForms
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required

from SRCCompany.services import (
    find_or_merge_company,
    find_or_merge_subdomain,
    find_or_merge_webinfo,
    find_or_merge_server,
    find_or_merge_port,
    find_or_merge_plug,
)


# Create your views here.
@csrf_protect
@login_required
def view_SRC(request):
    '''
            查看
    '''
    if request.method == "POST":
        form = CompanyInfoForms(request.POST)
        if form.is_valid():
            obj, created, merged = find_or_merge_company(form.cleaned_data)
            if created:
                messages.success(request, '添加成功')
            elif merged:
                messages.info(request, '已存在相同SRC地址的企业记录，已自动合并补全')
            return HttpResponseRedirect('/SRC')
        else:
            error = '添加失败，请检查输入'

    if request.method == "GET":
        SRC_lists = CompanyInfo.objects.all().order_by('company_updatetime')
        form = CompanyInfoForms()

        paginator = Paginator(SRC_lists, 7)

        page = request.GET.get('page')
        try:
            SRC_list = paginator.page(page)
        except PageNotAnInteger:
            SRC_list = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            SRC_list = paginator.page(paginator.num_pages)
        return render(request,'SRCinfo/SRC_view.html',{'SRC_list':SRC_list,'form':form})
    return render(request,'error.html',{'error':error})

@login_required
def delete_SRC(request,company_id):
    '''
                删除
    '''
    if company_id:
        CompanyInfo.objects.get(company_id = company_id).delete()
    return HttpResponseRedirect('/SRC')

@csrf_protect
@login_required
def view_SubDomain(request,company_id):
    '''
            查看
    '''
    if request.method == "POST":
        form = SubDomainForms(request.POST)
        if form.is_valid():
            company = CompanyInfo.objects.get(company_id=company_id)
            obj, created, merged = find_or_merge_subdomain(form.cleaned_data, company)
            if created:
                messages.success(request, '添加成功')
            elif merged:
                messages.info(request, '已存在相同子域名地址，已自动合并补全')
            return HttpResponseRedirect('/SRC/WEB/'+company_id)
        else:
            error = '添加失败，请检查输入'

    if request.method == "GET":
        SRC = CompanyInfo.objects.get(company_id=company_id)
        SubDomain_lists = SRC.subdomain_in_company.all().order_by('subdomain_updatetime')
        form = SubDomainForms()

        paginator = Paginator(SubDomain_lists, 7)

        page = request.GET.get('page')
        try:
            WEB_list = paginator.page(page)
        except PageNotAnInteger:
            WEB_list = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            WEB_list = paginator.page(paginator.num_pages)
        return render(request,'SRCinfo/SubDomain.html',{'WEB_list':WEB_list,'form':form})
    return render(request,'error.html',{'error':error})

@login_required
def delete_WEB(request,subdomain_id):
    '''
                删除
    '''
    if subdomain_id:
        WEB = Subdomain.objects.get(subdomain_id = subdomain_id)
        company_id = WEB.subdomain_company.company_id
        WEB.delete()
    return HttpResponseRedirect('/SRC/WEB/'+str(company_id))

@login_required
def view_WEBinfo(request,subdomain_id):
    subdomain_list = Subdomain.objects.filter(subdomain_id = subdomain_id)
    #company_id = subdomain.subdomain_company.company_id
    if subdomain_list:
        for subdomain in subdomain_list:
            webinfo_list = subdomain.web_in_subdomain.all()
            server_list = subdomain.server_in_subdomain.all()
            plug_lists = []
            port_lists = []
            if server_list:
                for server in server_list:
                    port = server.port_in_server.all()
                    port_lists.append(port)
            if webinfo_list:
                for web in webinfo_list:
                    plug = web.plug_in_webinfo.all()
                    plug_lists.append(plug)
    else:
        error = '无效的参数'
        return render(request,'error.html',{'error':error})
    web_form = WebinfoForms()
    plug_form = PlugForms()
    server_form = ServerForms()
    port_form = PortForms()
    data = {
            'subdomain_list':subdomain_list,
            'webinfo_list':webinfo_list,
            'server_list':server_list,
            'port_lists':port_lists,
            'plug_lists':plug_lists,
            'web_form':web_form,
            'plug_form':plug_form,
            'server_form':server_form,
            'port_form':port_form,
            'subdomain_id':subdomain_id,
            }
    return render(request,'SRCinfo/WEB_view.html',data)


@csrf_protect
@login_required
def Webinfo_add(request,subdomain_id):
    if request.method == "POST":
        form = WebinfoForms(request.POST)
        if form.is_valid():
            subdomain = Subdomain.objects.get(subdomain_id=subdomain_id)
            obj, created, merged = find_or_merge_webinfo(form.cleaned_data, subdomain)
            if created:
                messages.success(request, '添加成功')
            elif merged:
                messages.info(request, '已存在相同网页链接，已自动更新技术信息')
            return HttpResponseRedirect('/SRC/subdomaininfo/' + str(subdomain_id))
        else:
            error = '添加失败，请检查输入'
            return render(request,'error.html',{'error':error})
    else:
        error = '请求错误'
        return render(request,'error.html',{'error':error})

@csrf_protect
@login_required
def Plug_add(request,subdomain_id):
    if request.method == "POST":
        form = PlugForms(request.POST)
        if form.is_valid():
            plug_webinfo = form.cleaned_data['plug_webinfo']
            obj, created, merged = find_or_merge_plug(form.cleaned_data, plug_webinfo)
            if created:
                messages.success(request, '添加成功')
            elif merged:
                messages.info(request, '已存在相同组件名称，已自动更新版本信息')
            return HttpResponseRedirect('/SRC/subdomaininfo/' + str(subdomain_id))
        else:
            error = '添加失败，请检查输入'
            return render(request,'error.html',{'error':error})
    else:
        error = '请求错误'
        return render(request,'error.html',{'error':error})

@csrf_protect
@login_required
def Server_add(request,subdomain_id):
    if request.method == "POST":
        form = ServerForms(request.POST)
        if form.is_valid():
            subdomain = Subdomain.objects.get(subdomain_id=subdomain_id)
            company = subdomain.subdomain_company
            obj, created, merged = find_or_merge_server(form.cleaned_data, subdomain, company)
            if created:
                messages.success(request, '添加成功')
            elif merged:
                messages.info(request, '已存在相同服务器IP，已自动更新信息')
            return HttpResponseRedirect('/SRC/subdomaininfo/' + str(subdomain_id))
        else:
            error = '添加失败，请检查输入'
            return render(request,'error.html',{'error':error})
    else:
        error = '请求错误'
        return render(request,'error.html',{'error':error})

@csrf_protect
@login_required
def Port_add(request,subdomain_id):
    if request.method == "POST":
        form = PortForms(request.POST)
        if form.is_valid():
            port_server = form.cleaned_data['port_server']
            obj, created, merged = find_or_merge_port(form.cleaned_data, port_server)
            if created:
                messages.success(request, '添加成功')
            elif merged:
                messages.info(request, '已存在相同端口号，已自动更新服务信息')
            return HttpResponseRedirect('/SRC/subdomaininfo/' + str(subdomain_id))
        else:
            error = '添加失败，请检查输入'
            return render(request,'error.html',{'error':error})
    else:
        error = '请求错误'
        return render(request,'error.html',{'error':error})
