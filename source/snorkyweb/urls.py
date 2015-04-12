from django.conf.urls import url, patterns, include
from snorkyweb import views
#from django.contrib import admin

#admin.autodiscover()

urlpatterns = patterns('',
    #url(r'^admin/', include(admin.site.urls)),  # NOQA
    url(r"^$", views.HomeView.as_view())
)
