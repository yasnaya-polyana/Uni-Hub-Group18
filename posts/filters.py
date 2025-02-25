import bleach
import markdown

from md_extensions.tailwind import TailwindExtension

md = markdown.Markdown(extensions=["fenced_code", TailwindExtension()])


def parse_md(txt: str):
    clean_txt = bleach.clean(txt)
    return md.convert(clean_txt)


def translate_repost(data):
    if data.ref_post != None:
        return data.ref_post
    return data
