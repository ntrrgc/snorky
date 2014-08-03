from django.contrib.staticfiles.views import serve

def home_view(request):
    return serve(request, "/index.html")
