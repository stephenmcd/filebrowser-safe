# Make available mezzanine_tags template tags library
# withouth the need of adding `mezzanine.core` to INSTALLED_APPS
from mezzanine.core.templatetags.mezzanine_tags import register  # NOQA
