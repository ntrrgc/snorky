from . import models, serializers, permissions
from rest_framework import mixins, viewsets, generics
from rest_framework import status
from rest_framework.response import Response
import snorky.backend.django.rest_framework as snorky


class TaskViewSet(snorky.ListSubscribeModelMixin,
                  viewsets.ModelViewSet):
    model = models.Task
    dealer = "AllTasks"
