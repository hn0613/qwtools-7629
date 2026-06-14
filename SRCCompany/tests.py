from django.test import TestCase, Client
from django.contrib.auth.models import User
from SRCCompany.models import CompanyInfo


class SRCPageSmokeTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_src_requires_login(self):
        resp = self.client.get('/SRC/')
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/', resp.url)

    def test_src_page_loads_after_login(self):
        self.client.login(username='testuser', password='testpass123')
        resp = self.client.get('/SRC/')
        self.assertEqual(resp.status_code, 200)

    def test_add_company_via_post(self):
        self.client.login(username='testuser', password='testpass123')
        resp = self.client.post('/SRC/', {
            'company_src_name': '测试SRC',
            'company_src_www': 'https://test-src.example.com',
            'company_name': '测试公司',
            'company_www': 'https://test.example.com',
            'company_ioc': 'https://test.example.com/icon.png',
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(CompanyInfo.objects.count(), 1)
        self.assertEqual(CompanyInfo.objects.first().company_name, '测试公司')
