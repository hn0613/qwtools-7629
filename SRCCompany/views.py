#coding:utf-8
from django.shortcuts import render,HttpResponseRedirect
from django.views.decorators.csrf import csrf_protect
from SRCCompany.models import CompanyInfo,Subdomain,Webinfo,Server,Port,Plug
from SRCCompany.forms import CompanyInfoForms,SubDomainForms
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required 
from SRCCompany.forms import WebinfoForms,ServerForms,PlugForms,PortForms

import time
from django.db.models import Q

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

@login_required
def search(request):
    '''全局搜索：跨公司/子域名/网站/服务器/端口/组件多模型模糊匹配'''
    query = request.GET.get('q', '').strip()
    results = {
        'companies': [],
        'subdomains': [],
        'webinfos': [],
        'servers': [],
        'plugs': [],
        'ports': [],
    }

    if query:
        q = query

        # ---- 公司 ----
        companies = CompanyInfo.objects.filter(
            Q(company_name__icontains=q) |
            Q(company_src_name__icontains=q) |
            Q(company_www__icontains=q) |
            Q(company_src_www__icontains=q)
        ).distinct()
        for c in companies:
            results['companies'].append({
                'obj': c,
                'hierarchy': c.company_name,
                'link_id': c.company_id,
            })

        # ---- 子域名 ----
        subdomains = Subdomain.objects.filter(
            Q(subdomain_name__icontains=q) |
            Q(subdomain_www__icontains=q)
        ).select_related('subdomain_company').distinct()
        for s in subdomains:
            results['subdomains'].append({
                'obj': s,
                'hierarchy': u'{} > {}'.format(
                    s.subdomain_company.company_name, s.subdomain_name or s.subdomain_www),
                'link_id': s.subdomain_id,
            })

        # ---- 网站信息 ----
        webinfos = Webinfo.objects.filter(
            Q(web_url__icontains=q) |
            Q(web_front__icontains=q) |
            Q(web_language__icontains=q) |
            Q(web_framework__icontains=q) |
            Q(web_template__icontains=q) |
            Q(web_container__icontains=q)
        ).select_related(
            'web_subdomain',
            'web_subdomain__subdomain_company'
        ).distinct()
        for w in webinfos:
            sd = w.web_subdomain
            co = sd.subdomain_company
            results['webinfos'].append({
                'obj': w,
                'hierarchy': u'{} > {} > {}'.format(
                    co.company_name, sd.subdomain_name or sd.subdomain_www, w.web_url),
                'link_id': sd.subdomain_id,
            })

        # ---- 服务器 ----
        servers = Server.objects.filter(
            Q(server_name__icontains=q) |
            Q(server_ip__icontains=q) |
            Q(server_os__icontains=q)
        ).select_related(
            'server_subdomain',
            'server_subdomain__subdomain_company'
        ).distinct()
        for s in servers:
            sd = s.server_subdomain
            co = sd.subdomain_company
            results['servers'].append({
                'obj': s,
                'hierarchy': u'{} > {} > {}'.format(
                    co.company_name, sd.subdomain_name or sd.subdomain_www, s.server_ip),
                'link_id': sd.subdomain_id,
            })

        # ---- 组件 ----
        plugs = Plug.objects.filter(
            Q(plug_name__icontains=q) |
            Q(plug_version__icontains=q)
        ).select_related(
            'plug_webinfo',
            'plug_webinfo__web_subdomain',
            'plug_webinfo__web_subdomain__subdomain_company'
        ).distinct()
        for p in plugs:
            wi = p.plug_webinfo
            sd = wi.web_subdomain
            co = sd.subdomain_company
            results['plugs'].append({
                'obj': p,
                'hierarchy': u'{} > {} > {} > {}'.format(
                    co.company_name, sd.subdomain_name or sd.subdomain_www,
                    wi.web_url, p.plug_name),
                'link_id': sd.subdomain_id,
            })

        # ---- 端口 ----
        try:
            ports = Port.objects.filter(
                Q(name__icontains=q) |
                Q(port__icontains=q) |
                Q(product__icontains=q) |
                Q(version__icontains=q)
            ).select_related(
                'port_server',
                'port_server__server_subdomain',
                'port_server__server_subdomain__subdomain_company'
            ).distinct()
        except Exception:
            ports = Port.objects.none()
        for p in ports:
            sv = p.port_server
            sd = sv.server_subdomain
            co = sd.subdomain_company
            detail_parts = [u'端口:{}'.format(p.port)]
            if p.product:
                detail_parts.append(p.product)
            if p.version:
                detail_parts.append(p.version)
            results['ports'].append({
                'obj': p,
                'hierarchy': u'{} > {} > {} > {}'.format(
                    co.company_name, sd.subdomain_name or sd.subdomain_www,
                    sv.server_ip, u' / '.join(detail_parts)),
                'link_id': sd.subdomain_id,
            })

    total_count = sum(len(v) for v in results.values())

    context = {
        'query': query,
        'results': results,
        'total_count': total_count,
    }
    return render(request, 'SRCinfo/search_results.html', context)
