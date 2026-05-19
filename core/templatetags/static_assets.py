from pathlib import Path

from django import template
from django.contrib.staticfiles import finders
from django.templatetags.static import static


register = template.Library()


@register.simple_tag
def static_version(path):
    path = str(path or "").strip()
    if not path:
        return ""

    url = static(path)
    absolute_path = finders.find(path)
    if not absolute_path:
        return url

    try:
        version = Path(absolute_path).stat().st_mtime_ns
    except OSError:
        return url

    separator = "&" if "?" in url else "?"
    return f"{url}{separator}v={version}"
