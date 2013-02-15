
from django.utils.translation import ugettext_lazy as _

from mezzanine.conf import register_setting


register_setting(
    name="MEDIA_LIBRARY_PER_SITE",
    label=_("Media library per site"),
    description=_("Segregate the media library based on the current site."),
    editable=True,
    default=False,
)
