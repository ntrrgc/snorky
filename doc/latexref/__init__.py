from docutils.nodes import reference, SkipNode
from docutils.parsers.rst import Directive
from sphinx.roles import XRefRole

class num_ref(reference):
    pass

def latex_visit_num_ref(self, node):
    self.body.append(r"\ref{%s:%s}" %
                     (node["refdoc"], node["reftarget"]))
    raise SkipNode

def setup(app):
    app.add_node(num_ref,
                 latex=(latex_visit_num_ref, None))

    app.add_role("num", XRefRole(nodeclass=num_ref))
