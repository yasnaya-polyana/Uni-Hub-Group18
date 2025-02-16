from django.shortcuts import redirect
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.conf import settings

def anonymous_required(function=None, redirect_field_name=None, login_url=None):
    """
    Decorator for views that checks that the user is NOT authenticated,
    redirecting to the specified page if they are.
    """
    if redirect_field_name is None:
        redirect_field_name = REDIRECT_FIELD_NAME

    if login_url is None:
        login_url = settings.LOGIN_URL

    def decorator(view_func): # This is the actual decorator
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated: # Check if the user is authenticated
                path = request.build_absolute_uri() # Current path
                # If redirect_field_name is set, use it. Otherwise, use default settings.LOGIN_REDIRECT_URL
                redirect_to = request.GET.get(redirect_field_name, settings.LOGIN_REDIRECT_URL)
                from urllib.parse import urlparse, urlunparse
                parsed_url = urlparse(redirect_to)
                if not parsed_url.netloc and parsed_url.path == path:
                    redirect_to = settings.LOGIN_REDIRECT_URL
                return redirect(redirect_to) # Redirect if authenticated

            return view_func(request, *args, **kwargs) # Execute the view if not authenticated
        return _wrapped_view
    if function:  # If the decorator is used without arguments
        return decorator(function)
    return decorator  # If the decorator is used with arguments