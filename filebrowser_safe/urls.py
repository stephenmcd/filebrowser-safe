from django.urls import re_path

from filebrowser_safe import views

urlpatterns = [
    re_path(r"^browse/$", views.browse, name="fb_browse"),
    re_path(r"^mkdir/", views.mkdir, name="fb_mkdir"),
    re_path(r"^upload/", views.upload, name="fb_upload"),
    re_path(r"^rename/$", views.rename, name="fb_rename"),
    re_path(r"^delete/$", views.delete, name="fb_delete"),
    re_path(r"^check_file/$", views._check_file, name="fb_check"),
    re_path(r"^upload_file/$", views._upload_file, name="fb_do_upload"),
]
