from __future__ import unicode_literals

from django.shortcuts import get_object_or_404
from django.conf import settings

from mezzanine.utils.models import get_user_model


def flash_login_required(function):
    """
    Decorator to recognize a user by its session.
    Used for Flash-Uploading.
    """

    def decorator(request, *args, **kwargs):
        try:
            engine = __import__(settings.SESSION_ENGINE, {}, {}, [''])
        except:
            import django.contrib.sessions.backends.db
            engine = django.contrib.sessions.backends.db
        session_data = engine.SessionStore(request.POST.get('session_key'))

        # Check to see if the request has already set a user (probably from middleware above). If it has,
        # use the user from the request, as we trust it has been set for a reason
        if request.user:
            user_id = request.user.id
        else:
            user_id = session_data['_auth_user_id']

        # will return 404 if the session ID does not resolve to a valid user
        request.user = get_object_or_404(get_user_model(), pk=user_id)
        return function(request, *args, **kwargs)
    return decorator
