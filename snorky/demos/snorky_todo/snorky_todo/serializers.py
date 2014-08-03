from . import models
from rest_framework import serializers


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Task
        fields = ("id", "title", "completed")
