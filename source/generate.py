#!/usr/bin/env python
import os
import sys

from django.core.handlers.wsgi import WSGIRequest
from io import StringIO

def render(view):
    request = WSGIRequest({
        'REQUEST_METHOD': 'GET',
        'PATH_INFO': '/',
        'wsgi.input': StringIO()
    })

    view_call = view()
    view_call.request = request
    output = view_call.get(request)
    output.render()
    return output.content

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "snorkyweb.settings")

    from snorkyweb import views
    with open('../index.html', 'wb') as f:
        f.write(render(views.HomeView))
