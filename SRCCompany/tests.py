#coding:utf-8
from django.test import TestCase, Client
from django.contrib.auth.models import User
from SRCCompany.models import CompanyInfo, Subdomain, Webinfo, Server, Port, Plug


class SearchViewTest(TestCase):
    """全局搜索功能测试"""

    def setUp(self):
        """构建测试用户和完整的六层样本数据"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123')

        # 公司
        self.company = CompanyInfo.objects.create(
            company_id=2024010101,
            company_src_name=u'测试SRC',
            company_src_www='https://src.example.com',
            company_name=u'测试科技有限公司',
            company_www='https://www.example.com',
            company_ioc='https://img.example.com/logo.png',
        )

        # 子域名
        self.subdomain = Subdomain.objects.create(
            subdomain_id='sd2024010101',
            subdomain_name=u'后台管理',
            subdomain_www='https://admin.example.com',
            subdomain_company=self.company,
        )

        # 网站信息
        self.webinfo = Webinfo.objects.create(
            web_id='web2024010101',
            web_url='https://admin.example.com/login',
            web_front=u'Vue',
            web_language=u'Java',
            web_framework=u'SpringBoot',
            web_template=u'ElementUI',
            web_container=u'Tomcat',
            web_subdomain=self.subdomain,
        )

        # 服务器
        self.server = Server.objects.create(
            server_name=u'生产服务器',
            server_ip='192.168.1.100',
            server_os=u'CentOS',
            server_company=self.company,
            server_subdomain=self.subdomain,
        )

        # 端口
        self.port = Port.objects.create(
            name=u'HTTP服务',
            port='8080',
            product=u'Nginx',
            version='1.20',
            port_server=self.server,
        )

        # 组件
        self.plug = Plug.objects.create(
            plug_name=u'jQuery',
            plug_version='3.6.0',
            plug_webinfo=self.webinfo,
        )

    # ---------- 登录拦截 ----------

    def test_search_requires_login(self):
        """未登录用户访问搜索页应被重定向到登录页"""
        resp = self.client.get('/SRC/search/', {'q': 'test'})
        self.assertEqual(resp.status_code, 302)
        self.assertIn('next=/SRC/search/', resp.url)

    # ---------- 空查询 / 空格 ----------

    def test_empty_query_shows_page(self):
        """空查询应正常返回搜索页，不报错"""
        self.client.login(username='testuser', password='testpass123')
        resp = self.client.get('/SRC/search/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['total_count'], 0)

    def test_whitespace_only_query(self):
        """纯空格查询应等同于空查询"""
        self.client.login(username='testuser', password='testpass123')
        resp = self.client.get('/SRC/search/', {'q': '   '})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['query'], '')
        self.assertEqual(resp.context['total_count'], 0)

    def test_leading_trailing_whitespace_trimmed(self):
        """前后空格应被自动修剪，仍能命中"""
        self.client.login(username='testuser', password='testpass123')
        resp = self.client.get('/SRC/search/', {'q': '  example  '})
        self.assertEqual(resp.status_code, 200)
        self.assertGreater(resp.context['total_count'], 0)

    # ---------- 大小写不敏感 ----------

    def test_case_insensitive_company(self):
        """公司名搜索应忽略大小写"""
        self.client.login(username='testuser', password='testpass123')
        resp = self.client.get('/SRC/search/', {'q': 'VUE'})
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(len(resp.context['results']['webinfos']) > 0)

    def test_case_insensitive_component(self):
        """组件名搜索应忽略大小写"""
        self.client.login(username='testuser', password='testpass123')
        resp = self.client.get('/SRC/search/', {'q': 'jquery'})
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(len(resp.context['results']['plugs']) > 0)

    # ---------- 半截关键词（子串匹配） ----------

    def test_partial_match_company_name(self):
        """半截公司名应能命中"""
        self.client.login(username='testuser', password='testpass123')
        resp = self.client.get('/SRC/search/', {'q': u'测试科技'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context['results']['companies']), 1)

    def test_partial_match_domain(self):
        """半截域名应能命中子域名"""
        self.client.login(username='testuser', password='testpass123')
        resp = self.client.get('/SRC/search/', {'q': 'admin.example'})
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(len(resp.context['results']['subdomains']) > 0)

    def test_partial_match_ip(self):
        """半截 IP 应能命中服务器"""
        self.client.login(username='testuser', password='testpass123')
        resp = self.client.get('/SRC/search/', {'q': '192.168'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context['results']['servers']), 1)

    def test_partial_match_component(self):
        """半截组件名应能命中"""
        self.client.login(username='testuser', password='testpass123')
        resp = self.client.get('/SRC/search/', {'q': 'jQu'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context['results']['plugs']), 1)

    def test_partial_match_port(self):
        """端口号子串应能命中"""
        self.client.login(username='testuser', password='testpass123')
        resp = self.client.get('/SRC/search/', {'q': '808'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context['results']['ports']), 1)

    # ---------- 各模型独立命中 ----------

    def test_search_company_by_src_name(self):
        """通过 SRC 名称搜到公司"""
        self.client.login(username='testuser', password='testpass123')
        resp = self.client.get('/SRC/search/', {'q': u'测试SRC'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context['results']['companies']), 1)

    def test_search_company_by_www(self):
        """通过官网地址搜到公司"""
        self.client.login(username='testuser', password='testpass123')
        resp = self.client.get('/SRC/search/', {'q': 'www.example.com'})
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(len(resp.context['results']['companies']) > 0)

    def test_search_subdomain(self):
        """搜索子域名地址"""
        self.client.login(username='testuser', password='testpass123')
        resp = self.client.get('/SRC/search/', {'q': 'admin.example.com'})
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(len(resp.context['results']['subdomains']) > 0)

    def test_search_webinfo_by_framework(self):
        """通过框架名搜到网站信息"""
        self.client.login(username='testuser', password='testpass123')
        resp = self.client.get('/SRC/search/', {'q': 'SpringBoot'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context['results']['webinfos']), 1)

    def test_search_webinfo_by_container(self):
        """通过容器名搜到网站信息"""
        self.client.login(username='testuser', password='testpass123')
        resp = self.client.get('/SRC/search/', {'q': 'Tomcat'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context['results']['webinfos']), 1)

    def test_search_server_by_os(self):
        """通过操作系统搜到服务器"""
        self.client.login(username='testuser', password='testpass123')
        resp = self.client.get('/SRC/search/', {'q': 'CentOS'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context['results']['servers']), 1)

    def test_search_port_by_product(self):
        """通过服务名搜到端口"""
        self.client.login(username='testuser', password='testpass123')
        resp = self.client.get('/SRC/search/', {'q': 'Nginx'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context['results']['ports']), 1)

    def test_search_plug_by_version(self):
        """通过组件版本号搜到组件"""
        self.client.login(username='testuser', password='testpass123')
        resp = self.client.get('/SRC/search/', {'q': '3.6.0'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context['results']['plugs']), 1)

    # ---------- 空结果 ----------

    def test_no_results(self):
        """无匹配关键词应返回空结果"""
        self.client.login(username='testuser', password='testpass123')
        resp = self.client.get('/SRC/search/', {'q': 'zzzznotexist999'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['total_count'], 0)

    # ---------- 层级路径完整性 ----------

    def test_subdomain_result_has_company_in_hierarchy(self):
        """子域名结果的层级路径应包含公司名"""
        self.client.login(username='testuser', password='testpass123')
        resp = self.client.get('/SRC/search/', {'q': 'admin.example.com'})
        self.assertEqual(resp.status_code, 200)
        subs = resp.context['results']['subdomains']
        self.assertTrue(len(subs) > 0)
        self.assertIn(u'测试科技', subs[0]['hierarchy'])

    def test_server_result_has_full_hierarchy(self):
        """服务器结果的层级路径应包含公司 > 子域名 > IP"""
        self.client.login(username='testuser', password='testpass123')
        resp = self.client.get('/SRC/search/', {'q': '192.168.1.100'})
        self.assertEqual(resp.status_code, 200)
        servers = resp.context['results']['servers']
        self.assertEqual(len(servers), 1)
        self.assertIn(u'测试科技', servers[0]['hierarchy'])
        self.assertIn('192.168.1.100', servers[0]['hierarchy'])

    def test_plug_result_has_full_hierarchy(self):
        """组件结果的层级路径应包含公司 > 子域名 > 网站 > 组件"""
        self.client.login(username='testuser', password='testpass123')
        resp = self.client.get('/SRC/search/', {'q': 'jQuery'})
        self.assertEqual(resp.status_code, 200)
        plugs = resp.context['results']['plugs']
        self.assertEqual(len(plugs), 1)
        self.assertIn(u'测试科技', plugs[0]['hierarchy'])
        self.assertIn('jQuery', plugs[0]['hierarchy'])

    def test_port_result_has_full_hierarchy(self):
        """端口结果的层级路径应包含公司 > 子域名 > 服务器 > 端口"""
        self.client.login(username='testuser', password='testpass123')
        resp = self.client.get('/SRC/search/', {'q': '8080'})
        self.assertEqual(resp.status_code, 200)
        ports = resp.context['results']['ports']
        self.assertEqual(len(ports), 1)
        self.assertIn(u'测试科技', ports[0]['hierarchy'])
        self.assertIn('192.168.1.100', ports[0]['hierarchy'])

    # ---------- 结果可跳转详情页 ----------

    def test_company_result_has_valid_link(self):
        """公司结果应带有效的子域名列表页链接"""
        self.client.login(username='testuser', password='testpass123')
        resp = self.client.get('/SRC/search/', {'q': u'测试科技'})
        companies = resp.context['results']['companies']
        self.assertEqual(len(companies), 1)
        link_id = companies[0]['link_id']
        # 验证链接可访问
        detail_resp = self.client.get('/SRC/WEB/{}'.format(link_id))
        self.assertEqual(detail_resp.status_code, 200)

    def test_subdomain_result_has_valid_link(self):
        """子域名结果应带有效的详情页链接"""
        self.client.login(username='testuser', password='testpass123')
        resp = self.client.get('/SRC/search/', {'q': 'admin.example.com'})
        subs = resp.context['results']['subdomains']
        self.assertTrue(len(subs) > 0)
        link_id = subs[0]['link_id']
        detail_resp = self.client.get('/SRC/subdomaininfo/{}/'.format(link_id))
        self.assertEqual(detail_resp.status_code, 200)

    # ---------- 多类型同时命中 ----------

    def test_multi_type_results(self):
        """一个关键词可能同时命中多个类型（如 example 命中公司、子域名、网站等）"""
        self.client.login(username='testuser', password='testpass123')
        resp = self.client.get('/SRC/search/', {'q': 'example.com'})
        self.assertEqual(resp.status_code, 200)
        # example.com 至少同时命中公司和子域名
        types_hit = sum(1 for v in resp.context['results'].values() if len(v) > 0)
        self.assertGreaterEqual(types_hit, 2)
