from django.test import TestCase
from django.urls import reverse


class HomepageTestCase(TestCase):
    HOMEPAGE_URL = reverse('home:homepage')

    def test_homepage_get(self):
        response = self.client.get(self.HOMEPAGE_URL)
        self.assertEqual(response.status_code, 200)

    def test_homepage_post(self):
        response = self.client.post(self.HOMEPAGE_URL)
        self.assertEqual(response.status_code, 405)

    def test_homepage_with_param(self):
        response = self.client.get(self.HOMEPAGE_URL + '1/')
        self.assertEqual(response.status_code, 404)
