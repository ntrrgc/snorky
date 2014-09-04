from docutils.nodes import General, Element, SkipNode
from docutils.parsers.rst import Directive

class nopagebreak(General, Element):
    pass

def latex_visit_nopagebreak(self, node):
    import ipdb; ipdb.set_trace()
    self.body.append(r"\nopagebreak")
    raise SkipNode

class NoPageBreakDirective(Directive):
    def run(self):
        return [nopagebreak("")]

def setup(app):
    app.add_directive("nopagebreak", NoPageBreakDirective)

    app.add_node(nopagebreak,
                 latex=(latex_visit_nopagebreak, None))
