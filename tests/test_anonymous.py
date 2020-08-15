from django.test import TestCase
from django.urls import reverse


class FilebrowserAnonymousTestCase(TestCase):
    def test_browse(self):
        url = reverse("fb_browse")
        response = self.client.get(url)
        self.assertEqual(302, response.status_code)
        self.assertEqual("/admin/login/?next=" + url, response.url)

    def test_mkdir(self):
        url = reverse("fb_browse")
        response = self.client.get(url)
        self.assertEqual(302, response.status_code)
        self.assertEqual("/admin/login/?next=" + url, response.url)

    def test_rename(self):
        url = reverse("fb_rename")
        response = self.client.get(url)
        self.assertEqual(302, response.status_code)
        self.assertEqual("/admin/login/?next=" + url, response.url)

    def test_delete(self):
        url = reverse("fb_delete")
        response = self.client.get(url)
        self.assertEqual(302, response.status_code)
        self.assertEqual("/admin/login/?next=" + url, response.url)

    def test_upload(self):
        url = reverse("fb_upload")
        response = self.client.get(url)
        self.assertEqual(302, response.status_code)
        self.assertEqual("/admin/login/?next=" + url, response.url)

    def test_do_upload(self):
        url = reverse("fb_do_upload")
        response = self.client.get(url)
        self.assertEqual(302, response.status_code)
        self.assertEqual("/admin/login/?next=" + url, response.url)
