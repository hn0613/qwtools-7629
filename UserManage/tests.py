from django.test import TestCase, Client
from django.contrib.auth.models import User


class AuthSmokeTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_login_page_loads(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, '登录')

    def test_register_page_loads(self):
        resp = self.client.get('/regist/')
        self.assertEqual(resp.status_code, 200)

    def test_login_success(self):
        resp = self.client.post('/', {'username': 'testuser', 'password': 'testpass123'})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, '/SRC/')

    def test_login_wrong_password(self):
        resp = self.client.post('/', {'username': 'testuser', 'password': 'wrong'})
        self.assertEqual(resp.status_code, 200)

    def test_logout_redirects(self):
        self.client.login(username='testuser', password='testpass123')
        resp = self.client.get('/signout/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, '/')
