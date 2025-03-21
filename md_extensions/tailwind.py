import re
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor
from markdown.preprocessors import Preprocessor

# Tailwind Extension
class TailwindExtension(Extension):
    """An extension to add classes to tags"""

    def extendMarkdown(self, md):
        md.preprocessors.register(MentionPreprocessor(md), "mention_preprocessor", 25)
        md.treeprocessors.register(TailwindTreeProcessor(md), "tailwind", 20)

# Tailwind Preprocessor
class TailwindTreeProcessor(Treeprocessor):
    """Walk the root node and modify any discovered tag"""

    classes = {
        "h1": "text-4xl font-bold mt-0 mb-2",
        "h2": "text-3xl font-bold mt-0 mb-2",
        "h3": "text-2xl font-bold mt-0 mb-2",
        "h4": "text-xl font-bold mt-0 mb-2",
        "h5": "text-lg font-bold mt-0 mb-2",
        "h6": "text-base font-bold mt-0 mb-2",
        "p": "mt-0 mb-4 text-normal",
        "a": "text-blue-700 hover:text-blue-500",
        "blockquote": "border-grey-300 border-l-4 text-normal italic mt-8 mb-8 pl-6 text-grey-800 text-lg",
        "code": "bg-grey-300 p-2 rounded-lg text-sm",
        "ul": "list-disc list-inside mt-4 mb-4",
        "ol": "list-decimal list-inside mt-4 mb-4",
    }

    def run(self, root):
        for node in root.iter():
            tag_classes = self.classes.get(node.tag)
            if tag_classes:
                node.attrib["class"] = tag_classes

# Regex for Mention [@]
MENTION_PATTERN = re.compile(r'\[@([a-zA-Z0-9_]+)\]')

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