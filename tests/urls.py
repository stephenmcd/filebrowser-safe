from django.conf.urls import url, include
from django.contrib import admin


admin.autodiscover()

urlpatterns = [
    url(r"^admin/filebrowser/", include("filebrowser_safe.urls")),
    url(r"^admin/", admin.site.urls),
]
