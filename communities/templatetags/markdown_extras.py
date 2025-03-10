from django import template
import markdown

register = template.Library()

@register.filter(name='markdown')
def markdown_to_html(text):
    return markdown.markdown(text, extensions=['extra', 'codehilite']) 