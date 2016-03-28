# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from django.conf.urls import patterns, include, url
from rest_framework import viewsets, routers
from . import views, api

router = routers.DefaultRouter(trailing_slash=False)
router.register("tasks", api.TaskViewSet)

urlpatterns = patterns('',
    url(r"^api/", include(router.urls)),
    url(r"^(?:|active|completed)$", "snorky_todo.views.home_view"),
)
