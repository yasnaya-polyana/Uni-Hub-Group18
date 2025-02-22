# extensions.py
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor


class TailwindExtension(Extension):
    """An extension to add classes to tags"""

    def extendMarkdown(self, md):
        md.treeprocessors.register(TailwindTreeProcessor(md), "tailwind", 20)


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
