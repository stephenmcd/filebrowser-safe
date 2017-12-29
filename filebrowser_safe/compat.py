import django

django_version = django.VERSION

is_gte_django2 = (django_version >= (2, 0))

if is_gte_django2:
    from django.urls import reverse
else:
    from django.core.urlresolvers import reverse #noqa
