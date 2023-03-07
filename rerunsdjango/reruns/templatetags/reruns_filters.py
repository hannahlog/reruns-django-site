from django import template
from django.utils import timezone

register = template.Library()

@register.filter
def datetime_long(dt):
    """Longer format for datetimes.

    (I'm being very fussy, and I might want to further customize this later.
    Otherwise I would just use DATETIME_FORMAT or the `now` filter with some other
    format string.)
    """
    return dt.strftime("%I:%M:%S %P, %B %d %Y (%Z)")

@register.filter
def datetime_short(dt):
    """Shorter format for datetimes, omitting the year if it's the current year.

    (I'm being very fussy, otherwise I would just use SHORT_DATETIME_FORMAT or the `now`
    filter with some other format string.)
    """
    return dt.strftime("%b %-d, %-I:%M %P") \
        if dt.year == timezone.now().astimezone(dt.tzinfo).year \
        else dt.strftime("%b %-d '%y, %-I:%M %P")

@register.filter
def in_past(dt):
    """Datetime predicate, true if the datetime has already passed, false otherwise."""
    return dt < timezone.now()

@register.filter
def strip_url_prefix(url):
    """Removes [http[s]://][www.] from the beginning of a url string.

    I would just import the re module if the casework were any more complicated. This
    is just simple enough that the manual casework is acceptable to me.

    The single loop takes care of 'https://www.' and 'http://www.' as well as
    'www.' by itself, because the check for 'www.' comes last
    (so 'http[s]://' will already have been stripped if applicable.)
    """
    for prefix in ("https://", "http://", "www."):
        if url.startswith(prefix):
            url = url[len(prefix):]
    return url

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def get_attribute(object, name):
    return object.__getattribute__(name)

@register.filter
def get_attributes(object, names):
    return ((name, object.__getattribute__(name)) for name in names)

@register.filter
def verbose(name, meta=None):
    return meta.get_field(name).verbose_name.title() \
        if name in {f.name for f in meta.fields} \
        else name.replace("_"," ").title()

@register.filter
def get_items(dictionary, keys):
    return ((key, dictionary[key]) for key in keys)