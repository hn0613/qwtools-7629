#coding:utf-8
from django.shortcuts import render,HttpResponseRedirect,get_object_or_404
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect
from SRCCompany.models import CompanyInfo,Subdomain,Webinfo,Server,Port,Plug
from SRCCompany.forms import CompanyInfoForms,SubDomainForms
from SRCCompany.forms import WebinfoForms,ServerForms,PlugForms,PortForms
from SRCCompany.forms import (CompanyInfoEditForm, SubDomainEditForm,
    WebinfoEditForm, ServerEditForm, PlugEditForm, PortEditForm)
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required

import time

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
            try:
                num = CompanyInfo.objects.latest('id').id
            except Exception:
                num = 0
            company_id = time.strftime('%Y%m%d',time.localtime(time.time())) + str(num)
            company_src_name = form.cleaned_data['company_src_name']
            company_src_www = form.cleaned_data['company_src_www']
            company_name = form.cleaned_data['company_name']
            company_www = form.cleaned_data['company_www']
            company_ioc = form.cleaned_data['company_ioc']
            
            CompanyInfo.objects.get_or_create(
                                          company_id = company_id,
                                          company_src_name = company_src_name,
                                          company_src_www = company_src_www,
                                          company_name = company_name,
                                          company_www = company_www,
                                          company_ioc = company_ioc,
                                        )
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
            try:
                num = Subdomain.objects.latest('id').id
            except Exception:
                num = 0
            subdomain_id = 'sd' + time.strftime('%Y%m%d',time.localtime(time.time())) + str(num)
            subdomain_name = form.cleaned_data['subdomain_name']
            subdomain_www = form.cleaned_data['subdomain_www']
            
            Subdomain.objects.get_or_create(
                                          subdomain_id = subdomain_id,
                                          subdomain_name = subdomain_name,
                                          subdomain_www = subdomain_www,
                                          subdomain_company = CompanyInfo.objects.get(company_id=company_id),
                                        )
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
            try:
                num = Webinfo.objects.latest('id').id
            except Exception:
                num = 0
            web_id =  time.strftime('%Y%m%d',time.localtime(time.time())) + str(num)
            web_url = form.cleaned_data['web_url']
            web_front = form.cleaned_data['web_front']
            web_language = form.cleaned_data['web_language']
            web_framework = form.cleaned_data['web_framework']
            web_template = form.cleaned_data['web_template']
            web_container = form.cleaned_data['web_container']
            
            Webinfo.objects.get_or_create(web_id = web_id,
                                          web_url = web_url,
                                          web_front = web_front,
                                          web_language = web_language,
                                          web_framework = web_framework,
                                          web_template = web_template,
                                          web_container = web_container,
                                          web_subdomain = Subdomain.objects.get(subdomain_id=subdomain_id)
                                          )
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
            plug_name = form.cleaned_data['plug_name']
            plug_version = form.cleaned_data['plug_version']
            plug_webinfo = form.cleaned_data['plug_webinfo']
            web_id = plug_webinfo.web_id
            Plug.objects.get_or_create(plug_name = plug_name,
                                          plug_version = plug_version,
                                          plug_webinfo = Webinfo.objects.get(web_id = web_id )
                                          )
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
            server_subdomain = Subdomain.objects.get(subdomain_id=subdomain_id)
            company_id = server_subdomain.subdomain_company.company_id
            server_name = form.cleaned_data['server_name']
            server_ip = form.cleaned_data['server_ip']
            server_os = form.cleaned_data['server_os']
            Server.objects.get_or_create(server_subdomain=server_subdomain,
                                       server_company=CompanyInfo.objects.get(company_id=company_id),
                                       server_name=server_name,
                                       server_ip=server_ip,
                                       server_os=server_os,
                                       )
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
            name = form.cleaned_data['name']
            port = form.cleaned_data['port']
            product = form.cleaned_data['product']
            version = form.cleaned_data['version']
            port_server = form.cleaned_data['port_server']
            Port.objects.get_or_create(name=name,
                                       port=port,
                                       product=product,
                                       version=version,
                                       port_server=port_server,
                                       )
            return HttpResponseRedirect('/SRC/subdomaininfo/' + str(subdomain_id))
        else:
            error = '添加失败，请检查输入'
            return render(request,'error.html',{'error':error})
    else:
        error = '请求错误'
        return render(request,'error.html',{'error':error})


# ============ 编辑视图（AJAX：GET 返回预填表单，POST 原地更新）============

def _edit_dispatch(request, obj, FormClass, url_name, pk):
    '''编辑通用逻辑：GET 返回表单 HTML，POST 保存并返回 JSON'''
    if request.method == 'GET':
        form = FormClass(instance=obj)
        action_url = reverse(url_name, args=[pk])
        form_html = render_to_string(
            'SRCinfo/_edit_form.html',
            {'form': form, 'action_url': action_url},
            request=request
        )
        return JsonResponse({'success': True, 'form_html': form_html})
    elif request.method == 'POST':
        form = FormClass(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})


@csrf_protect
@login_required
def Company_edit(request, pk):
    '''编辑公司信息'''
    obj = get_object_or_404(CompanyInfo, pk=pk)
    return _edit_dispatch(request, obj, CompanyInfoEditForm, 'edit_company', pk)

@csrf_protect
@login_required
def Subdomain_edit(request, pk):
    '''编辑子域名信息'''
    obj = get_object_or_404(Subdomain, pk=pk)
    return _edit_dispatch(request, obj, SubDomainEditForm, 'edit_subdomain', pk)

@csrf_protect
@login_required
def Webinfo_edit(request, pk):
    '''编辑网站信息'''
    obj = get_object_or_404(Webinfo, pk=pk)
    return _edit_dispatch(request, obj, WebinfoEditForm, 'edit_webinfo', pk)

@csrf_protect
@login_required
def Server_edit(request, pk):
    '''编辑服务器信息'''
    obj = get_object_or_404(Server, pk=pk)
    return _edit_dispatch(request, obj, ServerEditForm, 'edit_server', pk)

@csrf_protect
@login_required
def Plug_edit(request, pk):
    '''编辑组件信息'''
    obj = get_object_or_404(Plug, pk=pk)
    return _edit_dispatch(request, obj, PlugEditForm, 'edit_plug', pk)

@csrf_protect
@login_required
def Port_edit(request, pk):
    '''编辑端口信息'''
    obj = get_object_or_404(Port, pk=pk)
    return _edit_dispatch(request, obj, PortEditForm, 'edit_port', pk)
