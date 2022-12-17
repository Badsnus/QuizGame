from django.test import Client, TestCase


class HomepageTestCase(TestCase):
    def test_homepage_get(self):
        response = Client().get('/')
        self.assertEqual(response.status_code, 200)

    def test_homepage_post(self):
        response = Client().post('/')
        self.assertEqual(response.status_code, 405)

    def test_homepage_with_param(self):
        response = Client().get('/1/')
        self.assertEqual(response.status_code, 404)
