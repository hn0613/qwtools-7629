#coding:utf-8
from django.test import TestCase, Client
from django.contrib.auth.models import User
from SRCCompany.models import CompanyInfo, Subdomain, Webinfo, Server, Port, Plug


class SearchGlobalTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='tester', password='testpass123')

        cls.company = CompanyInfo.objects.create(
            company_id=201712101,
            company_src_name='AlphaSRC',
            company_src_www='https://src.alpha.com',
            company_name='Alpha公司',
            company_www='https://www.alpha.com',
        )
        cls.subdomain = Subdomain.objects.create(
            subdomain_id='sd201712101',
            subdomain_name='邮件系统',
            subdomain_www='https://mail.alpha.com',
            subdomain_company=cls.company,
        )
        cls.webinfo = Webinfo.objects.create(
            web_id='201712101',
            web_url='https://mail.alpha.com/login',
            web_language='Java',
            web_framework='Spring',
            web_container='Tomcat',
            web_subdomain=cls.subdomain,
        )
        cls.server = Server.objects.create(
            server_name='web-prod-01',
            server_ip='192.168.1.100',
            server_os='CentOS',
            server_company=cls.company,
            server_subdomain=cls.subdomain,
        )
        cls.port = Port.objects.create(
            name='httpd',
            port='8080',
            product='Apache',
            version='2.4.6',
            port_server=cls.server,
        )
        cls.plug = Plug.objects.create(
            plug_name='jQuery',
            plug_version='3.2.1',
            plug_webinfo=cls.webinfo,
        )

    def setUp(self):
        self.client = Client()
        self.client.login(username='tester', password='testpass123')

    # ---- 基本搜索 ----

    def test_search_company_by_name(self):
        resp = self.client.get('/SRC/search/', {'q': 'Alpha'})
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(any(r['type'] == '公司' for r in resp.context['results']))

    def test_search_company_by_src_name(self):
        resp = self.client.get('/SRC/search/', {'q': 'AlphaSRC'})
        self.assertTrue(any(r['type'] == '公司' for r in resp.context['results']))

    def test_search_subdomain_by_url(self):
        resp = self.client.get('/SRC/search/', {'q': 'mail.alpha'})
        self.assertTrue(any(r['type'] == '子域名' for r in resp.context['results']))

    def test_search_subdomain_by_name(self):
        resp = self.client.get('/SRC/search/', {'q': '邮件'})
        self.assertTrue(any(r['type'] == '子域名' for r in resp.context['results']))

    # ---- 跨层级搜索 ----

    def test_search_server_by_ip(self):
        resp = self.client.get('/SRC/search/', {'q': '192.168.1.100'})
        self.assertTrue(any(r['type'] == '服务器' for r in resp.context['results']))

    def test_search_server_by_os(self):
        resp = self.client.get('/SRC/search/', {'q': 'CentOS'})
        self.assertTrue(any(r['type'] == '服务器' for r in resp.context['results']))

    def test_search_port_by_number(self):
        resp = self.client.get('/SRC/search/', {'q': '8080'})
        self.assertTrue(any(r['type'] == '端口' for r in resp.context['results']))

    def test_search_port_by_product(self):
        resp = self.client.get('/SRC/search/', {'q': 'Apache'})
        self.assertTrue(any(r['type'] == '端口' for r in resp.context['results']))

    def test_search_plug_by_name(self):
        resp = self.client.get('/SRC/search/', {'q': 'jQuery'})
        self.assertTrue(any(r['type'] == '组件' for r in resp.context['results']))

    def test_search_plug_by_version(self):
        resp = self.client.get('/SRC/search/', {'q': '3.2.1'})
        self.assertTrue(any(r['type'] == '组件' for r in resp.context['results']))

    def test_search_webinfo_by_framework(self):
        resp = self.client.get('/SRC/search/', {'q': 'Spring'})
        self.assertTrue(any(r['type'] == '网站' for r in resp.context['results']))

    def test_search_webinfo_by_container(self):
        resp = self.client.get('/SRC/search/', {'q': 'Tomcat'})
        self.assertTrue(any(r['type'] == '网站' for r in resp.context['results']))

    # ---- 大小写不敏感 ----

    def test_case_insensitive_upper(self):
        resp = self.client.get('/SRC/search/', {'q': 'ALPHA'})
        self.assertTrue(len(resp.context['results']) > 0)

    def test_case_insensitive_lower(self):
        resp = self.client.get('/SRC/search/', {'q': 'alpha'})
        self.assertTrue(len(resp.context['results']) > 0)

    def test_case_insensitive_mixed(self):
        resp = self.client.get('/SRC/search/', {'q': 'aLpHa'})
        self.assertTrue(len(resp.context['results']) > 0)

    # ---- 空格容错 ----

    def test_whitespace_leading(self):
        resp = self.client.get('/SRC/search/', {'q': '  Alpha'})
        self.assertTrue(len(resp.context['results']) > 0)

    def test_whitespace_trailing(self):
        resp = self.client.get('/SRC/search/', {'q': 'Alpha   '})
        self.assertTrue(len(resp.context['results']) > 0)

    def test_whitespace_both(self):
        resp = self.client.get('/SRC/search/', {'q': '  Alpha  '})
        self.assertTrue(len(resp.context['results']) > 0)

    # ---- 部分关键词 ----

    def test_partial_keyword_ip(self):
        resp = self.client.get('/SRC/search/', {'q': '192.168'})
        self.assertTrue(any(r['type'] == '服务器' for r in resp.context['results']))

    def test_partial_keyword_domain(self):
        resp = self.client.get('/SRC/search/', {'q': 'mail'})
        self.assertTrue(any(r['type'] == '子域名' for r in resp.context['results']))

    def test_partial_keyword_component(self):
        resp = self.client.get('/SRC/search/', {'q': 'Que'})
        self.assertTrue(any(r['type'] == '组件' for r in resp.context['results']))

    # ---- 空关键词 ----

    def test_empty_query(self):
        resp = self.client.get('/SRC/search/', {'q': ''})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['result_count'], 0)

    def test_no_query_param(self):
        resp = self.client.get('/SRC/search/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['result_count'], 0)

    def test_whitespace_only_query(self):
        resp = self.client.get('/SRC/search/', {'q': '   '})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['result_count'], 0)

    # ---- 无匹配 ----

    def test_no_match(self):
        resp = self.client.get('/SRC/search/', {'q': 'zzz_no_match_xyz'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['result_count'], 0)
        self.assertContains(resp, '未找到')

    # ---- 结果包含正确的跳转链接 ----

    def test_company_result_url(self):
        resp = self.client.get('/SRC/search/', {'q': 'Alpha公司'})
        company_results = [r for r in resp.context['results'] if r['type'] == '公司']
        self.assertTrue(len(company_results) > 0)
        self.assertIn(str(self.company.company_id), company_results[0]['url'])

    def test_subdomain_result_url(self):
        resp = self.client.get('/SRC/search/', {'q': '邮件系统'})
        sd_results = [r for r in resp.context['results'] if r['type'] == '子域名']
        self.assertTrue(len(sd_results) > 0)
        self.assertIn(self.subdomain.subdomain_id, sd_results[0]['url'])

    def test_server_result_url(self):
        resp = self.client.get('/SRC/search/', {'q': '192.168.1.100'})
        sv_results = [r for r in resp.context['results'] if r['type'] == '服务器']
        self.assertTrue(len(sv_results) > 0)
        self.assertIn(self.subdomain.subdomain_id, sv_results[0]['url'])

    def test_result_links_in_html(self):
        resp = self.client.get('/SRC/search/', {'q': 'Alpha'})
        self.assertContains(resp, '查看详情')

    # ---- 结果包含层级路径 ----

    def test_breadcrumb_for_server(self):
        resp = self.client.get('/SRC/search/', {'q': '192.168.1.100'})
        sv_results = [r for r in resp.context['results'] if r['type'] == '服务器']
        self.assertIn('Alpha', sv_results[0]['breadcrumb'])

    def test_breadcrumb_for_port(self):
        resp = self.client.get('/SRC/search/', {'q': '8080'})
        port_results = [r for r in resp.context['results'] if r['type'] == '端口']
        self.assertIn('Alpha', port_results[0]['breadcrumb'])
        self.assertIn('192.168.1.100', port_results[0]['breadcrumb'])

    # ---- 登录保护 ----

    def test_login_required(self):
        self.client.logout()
        resp = self.client.get('/SRC/search/', {'q': 'Alpha'})
        self.assertEqual(resp.status_code, 302)
