import os
import shutil
import tempfile
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.test import TestCase
from django.urls import reverse

from filebrowser_safe.functions import get_directory
from filebrowser_safe.templatetags.fb_tags import get_query_string

User = get_user_model()


class FilebrowserStaffTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.upload_dir = default_storage.path(get_directory())
        cls.subdir = Path(cls.upload_dir) / "TEST_DIRECTORY"
        cls.subdir.mkdir()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Cleanup the upload directory if some of the tests failed and
        # didn't cleanup after itself.
        shutil.rmtree(cls.upload_dir)

    def setUp(self):
        user = User.objects.create_user(
            username="staff",
            password="password",
            is_staff=True,
        )
        self.client.force_login(user)

    def test_browse(self):
        url = reverse("fb_browse")
        with tempfile.NamedTemporaryFile(dir=self.upload_dir) as temp_file:
            response = self.client.get(url)
            self.assertContains(response, os.path.basename(temp_file.name))
            self.assertContains(response, self.subdir.name)

    def test_browse__dir(self):
        url = reverse("fb_browse") + f"?dir={self.subdir.name}"
        with tempfile.NamedTemporaryFile(dir=str(self.subdir)) as temp_file:
            response = self.client.get(url, data={"dir": self.subdir.name})
            self.assertContains(response, os.path.basename(temp_file.name))

    def test_browse__suspicious(self):
        url = reverse("fb_browse") + f"?dir={self.subdir.name}/../"
        response = self.client.get(url)
        self.assertRedirects(response, reverse("fb_browse") + "?")

    def test_mkdir_page_get(self):
        url = reverse("fb_mkdir")
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

    def test_mkdir(self):
        url = reverse("fb_mkdir")
        redirect_url = reverse("fb_browse") + get_query_string(
            {"ot": "desc", "o": "date"}
        )
        test_name = "New folder for test"
        test_path = os.path.join(self.upload_dir, test_name)
        self.assertFalse(default_storage.exists(test_path))
        response = self.client.post(url, data={"dir_name": test_name}, follow=True)
        self.assertEqual(200, response.status_code)
        self.assertEqual([(redirect_url, 302)], response.redirect_chain)
        self.assertTrue(default_storage.exists(test_path))
        # Cleanup newly created directory
        os.rmdir(test_path)

    def test_rename_get_page(self):
        url = reverse("fb_rename")
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

    def test_rename(self):
        url = reverse("fb_rename")
        redirect_url = reverse("fb_browse") + "?"
        with tempfile.NamedTemporaryFile(
            dir=self.upload_dir, prefix="fb-", suffix="-test.txt", delete=False
        ) as temp_file:
            temp_path = temp_file.name
        new_file_name = "fb-test-renamed.txt"
        new_file_path = os.path.join(self.upload_dir, new_file_name)
        self.assertTrue(default_storage.exists(temp_path))
        self.assertFalse(default_storage.exists(new_file_path))
        response = self.client.post(
            url + "?filename=" + os.path.basename(temp_path),
            data={"name": os.path.splitext(new_file_name)[0]},
            follow=True,
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual([(redirect_url, 302)], response.redirect_chain)
        self.assertFalse(default_storage.exists(temp_path))
        self.assertTrue(default_storage.exists(new_file_path))
        # Cleanup test created file
        default_storage.delete(new_file_path)

    def test_delete(self):
        url = reverse("fb_delete")
        redirect_url = reverse("fb_browse") + "?"
        with tempfile.NamedTemporaryFile(
            dir=self.upload_dir, prefix="fb-", suffix="-test.txt", delete=False
        ) as temp_file:
            temp_path = temp_file.name
        self.assertTrue(default_storage.exists(temp_path))
        response = self.client.post(
            url + "?filename=" + os.path.basename(temp_path), follow=True
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual([(redirect_url, 302)], response.redirect_chain)
        self.assertFalse(default_storage.exists(temp_path))

    def test_upload(self):
        url = reverse("fb_upload")
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

    def test_do_upload(self):
        url = reverse("fb_do_upload")
        test_file = ContentFile(b"Test File content", name="test-file-upload.txt")
        test_file_path = os.path.join(self.upload_dir, test_file.name)
        self.assertFalse(default_storage.exists(test_file_path))
        response = self.client.post(url, data={"folder": "", "Filedata": test_file})
        self.assertEqual(200, response.status_code)
        self.assertTrue(default_storage.exists(test_file_path))
        with default_storage.open(test_file_path) as uploaded_file:
            test_file.seek(0)
            self.assertEqual(uploaded_file.read(), test_file.read())
        # Cleanup uploaded file
        default_storage.delete(test_file_path)
