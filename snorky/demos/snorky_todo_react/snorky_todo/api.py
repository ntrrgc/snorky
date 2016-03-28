# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from . import models, serializers
from rest_framework import mixins, viewsets, generics
from rest_framework import status
from rest_framework.response import Response
import snorky.backend.django.rest_framework as snorky


class TaskViewSet(snorky.ListSubscribeModelMixin,
                  viewsets.ModelViewSet):
    model = models.Task
    queryset = models.Task.objects.all()
    dealer = "AllTasks"
    serializer_class = serializers.TaskSerializer
