from jinja2 import Environment
from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import reverse

# Custom URL function that can handle keyword arguments
def url(view_name, *args, **kwargs):
    return reverse(view_name, args=args, kwargs=kwargs)

def environment(**options):
    env = Environment(**options)
    env.globals.update({
        'static': staticfiles_storage.url,
        'url': url,  # Use our custom url function
        'hasattr': hasattr
    })
    return env