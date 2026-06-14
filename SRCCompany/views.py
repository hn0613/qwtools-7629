#coding:utf-8
from django.shortcuts import render,HttpResponseRedirect
from django.views.decorators.csrf import csrf_protect
from django.http import Http404
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required

from SRCCompany.models import CompanyInfo,Subdomain,Webinfo,Server,Port,Plug
from SRCCompany.forms import CompanyInfoForms,SubDomainForms
from SRCCompany.forms import WebinfoForms,ServerForms,PlugForms,PortForms
from SRCCompany.dedup import smart_get_or_create

import time


@csrf_protect
@login_required
def view_SRC(request):
    if request.method == "POST":
        form = CompanyInfoForms(request.POST)
        if form.is_valid():
            try:
                num = CompanyInfo.objects.latest('id').id
            except Exception:
                num = 0
            company_id = time.strftime('%Y%m%d',time.localtime(time.time())) + str(num)

            obj, created = smart_get_or_create(
                CompanyInfo,
                lookup={'company_name': form.cleaned_data['company_name']},
                defaults={
                    'company_id': company_id,
                    'company_src_name': form.cleaned_data['company_src_name'],
                    'company_src_www': form.cleaned_data['company_src_www'],
                    'company_www': form.cleaned_data['company_www'],
                    'company_ioc': form.cleaned_data['company_ioc'],
                },
            )
            if not created:
                messages.info(request, '企业「%s」已存在，已更新相关信息' % obj.company_name)
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
            SRC_list = paginator.page(paginator.num_pages)
        return render(request,'SRCinfo/SRC_view.html',{'SRC_list':SRC_list,'form':form})
    return render(request,'error.html',{'error':error})

@login_required
def delete_SRC(request,company_id):
    obj = CompanyInfo.objects.filter(company_id=company_id).first()
    if obj is None:
        raise Http404
    obj.delete()
    return HttpResponseRedirect('/SRC')

@csrf_protect
@login_required
def view_SubDomain(request,company_id):
    if request.method == "POST":
        form = SubDomainForms(request.POST)
        if form.is_valid():
            try:
                num = Subdomain.objects.latest('id').id
            except Exception:
                num = 0
            subdomain_id = 'sd' + time.strftime('%Y%m%d',time.localtime(time.time())) + str(num)

            company = CompanyInfo.objects.filter(company_id=company_id).first()
            if company is None:
                return render(request,'error.html',{'error':'企业不存在'})

            obj, created = smart_get_or_create(
                Subdomain,
                lookup={
                    'subdomain_www': form.cleaned_data['subdomain_www'],
                    'subdomain_company': company,
                },
                defaults={
                    'subdomain_id': subdomain_id,
                    'subdomain_name': form.cleaned_data['subdomain_name'],
                },
            )
            if not created:
                messages.info(request, '子域名「%s」已存在，已更新相关信息' % obj.subdomain_www)
            return HttpResponseRedirect('/SRC/WEB/'+company_id)
        else:
            error = '添加失败，请检查输入'

    if request.method == "GET":
        SRC = CompanyInfo.objects.filter(company_id=company_id).first()
        if SRC is None:
            return render(request,'error.html',{'error':'企业不存在'})
        SubDomain_lists = SRC.subdomain_in_company.all().order_by('subdomain_updatetime')
        form = SubDomainForms()

        paginator = Paginator(SubDomain_lists, 7)

        page = request.GET.get('page')
        try:
            WEB_list = paginator.page(page)
        except PageNotAnInteger:
            WEB_list = paginator.page(1)
        except EmptyPage:
            WEB_list = paginator.page(paginator.num_pages)
        return render(request,'SRCinfo/SubDomain.html',{'WEB_list':WEB_list,'form':form})
    return render(request,'error.html',{'error':error})

@login_required
def delete_WEB(request,subdomain_id):
    WEB = Subdomain.objects.filter(subdomain_id=subdomain_id).first()
    if WEB is None:
        raise Http404
    company_id = WEB.subdomain_company.company_id
    WEB.delete()
    return HttpResponseRedirect('/SRC/WEB/'+str(company_id))

@login_required
def view_WEBinfo(request,subdomain_id):
    subdomain_list = Subdomain.objects.filter(subdomain_id = subdomain_id)
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
            try:
                num = Webinfo.objects.latest('id').id
            except Exception:
                num = 0
            web_id = time.strftime('%Y%m%d',time.localtime(time.time())) + str(num)

            subdomain = Subdomain.objects.filter(subdomain_id=subdomain_id).first()
            if subdomain is None:
                return render(request,'error.html',{'error':'子域名不存在'})

            obj, created = smart_get_or_create(
                Webinfo,
                lookup={
                    'web_url': form.cleaned_data['web_url'],
                    'web_subdomain': subdomain,
                },
                defaults={
                    'web_id': web_id,
                    'web_front': form.cleaned_data['web_front'],
                    'web_language': form.cleaned_data['web_language'],
                    'web_framework': form.cleaned_data['web_framework'],
                    'web_template': form.cleaned_data['web_template'],
                    'web_container': form.cleaned_data['web_container'],
                },
            )
            if not created:
                messages.info(request, '网站「%s」已存在，已更新相关信息' % obj.web_url)
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

            obj, created = smart_get_or_create(
                Plug,
                lookup={
                    'plug_name': form.cleaned_data['plug_name'],
                    'plug_webinfo': plug_webinfo,
                },
                defaults={
                    'plug_version': form.cleaned_data['plug_version'],
                },
            )
            if not created:
                messages.info(request, '组件「%s」已存在，已更新相关信息' % obj.plug_name)
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
            server_subdomain = Subdomain.objects.filter(subdomain_id=subdomain_id).first()
            if server_subdomain is None:
                return render(request,'error.html',{'error':'子域名不存在'})

            obj, created = smart_get_or_create(
                Server,
                lookup={
                    'server_ip': form.cleaned_data['server_ip'],
                    'server_subdomain': server_subdomain,
                },
                defaults={
                    'server_name': form.cleaned_data['server_name'],
                    'server_os': form.cleaned_data['server_os'],
                    'server_company': server_subdomain.subdomain_company,
                },
            )
            if not created:
                messages.info(request, '服务器「%s」已存在，已更新相关信息' % obj.server_ip)
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

            obj, created = smart_get_or_create(
                Port,
                lookup={
                    'port': form.cleaned_data['port'],
                    'port_server': port_server,
                },
                defaults={
                    'name': form.cleaned_data['name'],
                    'product': form.cleaned_data['product'],
                    'version': form.cleaned_data['version'],
                },
            )
            if not created:
                messages.info(request, '端口「%s」已存在，已更新相关信息' % obj.port)
            return HttpResponseRedirect('/SRC/subdomaininfo/' + str(subdomain_id))
        else:
            error = '添加失败，请检查输入'
            return render(request,'error.html',{'error':error})
    else:
        error = '请求错误'
        return render(request,'error.html',{'error':error})
