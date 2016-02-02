from __future__ import unicode_literals

from django.conf.urls import url

from filebrowser_safe import views


urlpatterns = [
    url(r'^browse/$', views.browse, name="fb_browse"),
    url(r'^mkdir/', views.mkdir, name="fb_mkdir"),
    url(r'^upload/', views.upload, name="fb_upload"),
    url(r'^rename/$', views.rename, name="fb_rename"),
    url(r'^delete/$', views.delete, name="fb_delete"),
    url(r'^check_file/$', views._check_file, name="fb_check"),
    url(r'^upload_file/$', views._upload_file, name="fb_do_upload"),
]
