
from django.shortcuts import render_to_response
from django.template import RequestContext
from pygmentize import pygmentizer

def pygmentize_example(request):

    some_text = """
    {% pygmentize 'python' %}
    '''this text comes from database or from other source'''
    def python_function(arg):
        pass
    {% endpygmentize %}
    """

    vars = {
        "pygmentized_text": pygmentizer.pygmentize(some_text),
        "not_pygmentized_text": some_text
    }
    return render_to_response('pygmentize_example.html', vars, context_instance=RequestContext(request))
