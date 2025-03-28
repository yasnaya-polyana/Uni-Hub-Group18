import bleach
import markdown

from md_extensions.tailwind import TailwindExtension

md = markdown.Markdown(extensions=["extra", TailwindExtension()])

def parse_md(txt: str) -> str:
    md = markdown.Markdown(extensions=["extra", "sane_lists", "codehilite", "nl2br", "admonition", "toc", TailwindExtension()])
    html = md.convert(txt)

    return bleach.clean(
        html,
        tags=[
            'p', 'blockquote', 'code', 'pre', 'ul', 'ol', 'li',
            'a', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'strong', 'em', 'br'
        ], attributes={
            'a': ['href', 'class'],
            'span': ['class'],
            '*': ['class'],
        },
        strip=True
    )

def translate_repost(data):
    if data.ref_post != None:
        return data.ref_post
    return data
