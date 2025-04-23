from django import template
from recommendations.kmeans import get_recommendations_for_user

register = template.Library()

@register.inclusion_tag('recommendations/recommendation_component.jinja', takes_context=True)
def show_recommendations(context, max_items=3, component_type='both'):
    """
    Renders recommendations for the current user
    
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