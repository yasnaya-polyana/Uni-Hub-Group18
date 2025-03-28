import re
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor
from markdown.preprocessors import Preprocessor

from communities.models import Communities
from posts.models import Post

# Tailwind Extension
class TailwindExtension(Extension):
    """An extension to add classes to tags"""

    def extendMarkdown(self, md):
        md.preprocessors.register(MentionPreprocessor(md), "mention_preprocessor", 25)
        md.preprocessors.register(CommunityPreprocessor(md), "community_preprocessor", 25)
        md.preprocessors.register(PostPreprocessor(md), "post_preprocessor", 25)
        md.treeprocessors.register(TailwindTreeProcessor(md), "tailwind", 25)

class TailwindTreeProcessor(Treeprocessor):
    """Walk the root node and modify any discovered tag"""

    classes = {
        "h1": "text-4xl font-bold mt-0 mb-2",
        "h2": "text-3xl font-bold mt-0 mb-2",
        "h3": "text-2xl font-bold mt-0 mb-2",
        "h4": "text-xl font-bold mt-0 mb-2",
        "h5": "text-lg font-bold mt-0 mb-2",
        "h6": "text-base font-bold mt-0 mb-2",
        "p": "mt-0 mb-4 text-base",
        "a": "text-blue-700 hover:text-blue-500 underline",
        "blockquote": "border-l-4 border-gray-300 italic pl-6 text-gray-800 text-lg my-6",
        "code": "bg-gray-100 px-1 py-0.5 rounded text-sm font-mono",
        "pre": "bg-gray-100 p-4 rounded overflow-x-auto text-sm",
        "ul": "list-disc list-inside mt-4 mb-4",
        "ol": "list-decimal list-inside mt-4 mb-4",
        "li": "mb-2",
    }

    def run(self, root):
        for node in root.iter():
            tag_class = self.classes.get(node.tag)
            if tag_class:
                existing = node.attrib.get("class", "")
                node.attrib["class"] = f"{existing} {tag_class}".strip()


# Regex for Mention [@]
MENTION_PATTERN = re.compile(r'\[@([a-zA-Z0-9_]+)\]')
COMMUNITY_PATTERN = re.compile(r'\[#([a-zA-Z0-9_-]+)\]')
POST_PATTERN = re.compile(r'\[!([a-zA-Z0-9_-]+)\]')

# Mention Preprocessor
class MentionPreprocessor(Preprocessor):
    def run(self, lines):
        new_lines = []
        for line in lines:
            # Replace all [@username] with <a href="/p/username">@username</a>
            line = MENTION_PATTERN.sub(self.mention_to_link, line)
            new_lines.append(line)
        return new_lines

    def mention_to_link(self, match):
        username = match.group(1)
        return f'<a target="_blank" href="/u/{username}"  class="text-blue-600 bg-blue-100 font-medium px-1 py-0.5 rounded">@{username}</a>'

# TODO: Add functionality for other mention types.

# Community Preprocessor
class CommunityPreprocessor(Preprocessor):
    def run(self, lines):
        new_lines = []
        for line in lines:
            line = COMMUNITY_PATTERN.sub(self.mention_to_link, line)
            new_lines.append(line)
        return new_lines

    def mention_to_link(self, match):
        id = match.group(1)
        name = Communities.objects.get(id=id).name

        return f'<a target="_blank" href="/c/{id}"  class="text-green-600 bg-blue-100 font-medium px-1 py-0.5 rounded">#{name}</a>'

# Post Preprocessor
class PostPreprocessor(Preprocessor):
    def run(self, lines):
        new_lines = []
        for line in lines:
            line = POST_PATTERN.sub(self.mention_to_link, line)
            new_lines.append(line)
        return new_lines

    def mention_to_link(self, match):
        id = match.group(1)
        title = Post.objects.get(id=id).title

        return f'<a target="_blank" href="/p/{id}"  class="text-orange-600 bg-blue-100 font-medium px-1 py-0.5 rounded">{title}</a>'


# TODO: Add functionality for other mention types.