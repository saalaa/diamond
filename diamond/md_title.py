from markdown import Extension
from markdown.treeprocessors import Treeprocessor

class TitleTreeProcessor(Treeprocessor):
    def __init__(self, md):
        self.md = md

    def run(self, root):
        for child in root.getchildren():
            if child.tag == 'h1':
                self.md.Title = (child.text or '').strip()
                break

class TitleExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        md.treeprocessors.add('title', TitleTreeProcessor(md), '_end')
