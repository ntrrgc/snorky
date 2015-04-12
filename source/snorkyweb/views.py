from django.views.generic.base import TemplateView

def read_version():
    with open('version.txt', 'r') as f:
        return f.read().strip()

class HomeView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        return {
            'version': read_version()
        }

