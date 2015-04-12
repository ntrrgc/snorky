import re
from pygments import highlight
from pygments.lexers import *
from pygments.formatters import HtmlFormatter
from django.http import HttpResponse
from pygments.lexers import HtmlLexer
from django.conf import settings

def add_pygment(matchobj):
    #string = matchobj.group(0)
    lang = matchobj.group(2)
    text = matchobj.group(4)
    #print text, lang
    try:
        lexer = get_lexer_by_name(lang, encoding='UTF-8')
    except:
        lexer = HtmlLexer()
    return highlight(text, lexer, HtmlFormatter())

""" look for {% pygmentize 'language' %} tags """
def pygmentize(text):
    #print "trying to pygmentize", text
    return re.sub(r'(?s)\{\%\ *pygmentize\ *(\'|\")([a-zA-Z0-9\+\-]*)(\'|\")\ *\%\}(.*?)\{\%\ *endpygmentize\ *\%\}', lambda x: add_pygment(x), text)


def get_css(request):
    style = getattr(settings, "PYGMENT_THEME", "native")
    return HttpResponse(unicode(HtmlFormatter(style=style).get_style_defs('.highlight')), mimetype="text/css")



