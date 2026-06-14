#coding:utf-8
from django.shortcuts import render, HttpResponseRedirect
from django.views.decorators.csrf import csrf_protect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required

from SRCCompany.models import CompanyInfo, Subdomain, Webinfo, Server, Port, Plug
from SRCCompany.forms import CompanyInfoForms, SubDomainForms
from SRCCompany.forms import WebinfoForms, ServerForms, PlugForms, PortForms
from SRCCompany.services import generate_record_id, get_parent_or_none, get_subdomain_detail


@csrf_protect
@login_required
def view_SRC(request):
    if request.method == "POST":
        form = CompanyInfoForms(request.POST)
        if form.is_valid():
            company_id = generate_record_id(CompanyInfo)
            CompanyInfo.objects.create(
                company_id=company_id,
                company_src_name=form.cleaned_data['company_src_name'],
                company_src_www=form.cleaned_data['company_src_www'],
                company_name=form.cleaned_data['company_name'],
                company_www=form.cleaned_data['company_www'],
                company_ioc=form.cleaned_data['company_ioc'],
            )
            return HttpResponseRedirect('/SRC')
        else:
            return render(request, 'error.html', {'error': u'添加失败，请检查输入'})

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
    return render(request, 'SRCinfo/SRC_view.html', {'SRC_list': SRC_list, 'form': form})


@login_required
def delete_SRC(request, company_id):
    if company_id:
        CompanyInfo.objects.get(company_id=company_id).delete()
    return HttpResponseRedirect('/SRC')


@csrf_protect
@login_required
def view_SubDomain(request, company_id):
    if request.method == "POST":
        form = SubDomainForms(request.POST)
        if form.is_valid():
            company, err = get_parent_or_none(CompanyInfo, 'company_id', company_id)
            if err:
                return render(request, 'error.html', {'error': err})
            subdomain_id = generate_record_id(Subdomain, prefix='sd')
            Subdomain.objects.create(
                subdomain_id=subdomain_id,
                subdomain_name=form.cleaned_data['subdomain_name'],
                subdomain_www=form.cleaned_data['subdomain_www'],
                subdomain_company=company,
            )
            return HttpResponseRedirect('/SRC/WEB/' + company_id)
        else:
            return render(request, 'error.html', {'error': u'添加失败，请检查输入'})

    company, err = get_parent_or_none(CompanyInfo, 'company_id', company_id)
    if err:
        return render(request, 'error.html', {'error': err})
    SubDomain_lists = company.subdomain_in_company.all().order_by('subdomain_updatetime')
    form = SubDomainForms()
    paginator = Paginator(SubDomain_lists, 7)
    page = request.GET.get('page')
    try:
        WEB_list = paginator.page(page)
    except PageNotAnInteger:
        WEB_list = paginator.page(1)
    except EmptyPage:
        WEB_list = paginator.page(paginator.num_pages)
    return render(request, 'SRCinfo/SubDomain.html', {'WEB_list': WEB_list, 'form': form})


@login_required
def delete_WEB(request, subdomain_id):
    if subdomain_id:
        WEB = Subdomain.objects.get(subdomain_id=subdomain_id)
        company_id = WEB.subdomain_company.company_id
        WEB.delete()
    return HttpResponseRedirect('/SRC/WEB/' + str(company_id))


@login_required
def view_WEBinfo(request, subdomain_id):
    data, err = get_subdomain_detail(subdomain_id)
    if err:
        return render(request, 'error.html', {'error': err})
    data['web_form'] = WebinfoForms()
    data['plug_form'] = PlugForms(subdomain_id=subdomain_id)
    data['server_form'] = ServerForms()
    data['port_form'] = PortForms(subdomain_id=subdomain_id)
    return render(request, 'SRCinfo/WEB_view.html', data)


@csrf_protect
@login_required
def Webinfo_add(request, subdomain_id):
    if request.method != "POST":
        return render(request, 'error.html', {'error': u'请求错误'})
    form = WebinfoForms(request.POST)
    if not form.is_valid():
        return render(request, 'error.html', {'error': u'添加失败，请检查输入'})
    subdomain, err = get_parent_or_none(Subdomain, 'subdomain_id', subdomain_id)
    if err:
        return render(request, 'error.html', {'error': err})
    Webinfo.objects.create(
        web_id=generate_record_id(Webinfo),
        web_url=form.cleaned_data['web_url'],
        web_front=form.cleaned_data['web_front'],
        web_language=form.cleaned_data['web_language'],
        web_framework=form.cleaned_data['web_framework'],
        web_template=form.cleaned_data['web_template'],
        web_container=form.cleaned_data['web_container'],
        web_subdomain=subdomain,
    )
    return HttpResponseRedirect('/SRC/subdomaininfo/' + str(subdomain_id))


@csrf_protect
@login_required
def Plug_add(request, subdomain_id):
    if request.method != "POST":
        return render(request, 'error.html', {'error': u'请求错误'})
    form = PlugForms(request.POST, subdomain_id=subdomain_id)
    if not form.is_valid():
        return render(request, 'error.html', {'error': u'添加失败，请检查输入'})
    Plug.objects.create(
        plug_name=form.cleaned_data['plug_name'],
        plug_version=form.cleaned_data['plug_version'],
        plug_webinfo=form.cleaned_data['plug_webinfo'],
    )
    return HttpResponseRedirect('/SRC/subdomaininfo/' + str(subdomain_id))


@csrf_protect
@login_required
def Server_add(request, subdomain_id):
    if request.method != "POST":
        return render(request, 'error.html', {'error': u'请求错误'})
    form = ServerForms(request.POST)
    if not form.is_valid():
        return render(request, 'error.html', {'error': u'添加失败，请检查输入'})
    subdomain, err = get_parent_or_none(Subdomain, 'subdomain_id', subdomain_id)
    if err:
        return render(request, 'error.html', {'error': err})
    Server.objects.create(
        server_subdomain=subdomain,
        server_company=subdomain.subdomain_company,
        server_name=form.cleaned_data['server_name'],
        server_ip=form.cleaned_data['server_ip'],
        server_os=form.cleaned_data['server_os'],
    )
    return HttpResponseRedirect('/SRC/subdomaininfo/' + str(subdomain_id))


@csrf_protect
@login_required
def Port_add(request, subdomain_id):
    if request.method != "POST":
        return render(request, 'error.html', {'error': u'请求错误'})
    form = PortForms(request.POST, subdomain_id=subdomain_id)
    if not form.is_valid():
        return render(request, 'error.html', {'error': u'添加失败，请检查输入'})
    Port.objects.create(
        name=form.cleaned_data['name'],
        port=form.cleaned_data['port'],
        product=form.cleaned_data['product'],
        version=form.cleaned_data['version'],
        port_server=form.cleaned_data['port_server'],
    )
    return HttpResponseRedirect('/SRC/subdomaininfo/' + str(subdomain_id))
