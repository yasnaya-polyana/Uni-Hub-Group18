from jinja2 import Environment
from django.templatetags.static import static
from django.urls import reverse
from django.middleware.csrf import get_token
from django.utils.timezone import template_localtime
from django.template.defaultfilters import date as date_filter
from recommendations.kmeans import get_recommendations_for_user

def environment(**options):
    env = Environment(**options)
    
    # Add custom functions to the Jinja2 environment
    env.globals.update({
        'get_recommendations': get_recommendations,
        'static': static,
        'url': reverse,
        'csrf_token': get_csrf_token,
    })
    
    # Add filters
    env.filters.update({
        'date': lambda value, format=None: date_filter(template_localtime(value), format),
        'truncate': lambda value, length=255, killwords=False, end='...': (value[:length] + end) if len(value) > length else value,
    })
    
    return env

def get_csrf_token(request):
    """Get the CSRF token for the current request"""
    return get_token(request)

def get_recommendations(context, max_items=3, component_type='both'):
    """
    Gets recommendations for the current user
    
    Args:
        context: The template context
        max_items: Maximum number of recommendations to show
        component_type: 'communities', 'events', or 'both'
    """
    user = context['request'].user
    recommended_communities, recommended_events = get_recommendations_for_user(user, max_items)
    
    return {
        'recommended_communities': recommended_communities if component_type in ['communities', 'both'] else [],
        'recommended_events': recommended_events if component_type in ['events', 'both'] else [],
        'component_type': component_type,
    } 