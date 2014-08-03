from django.db import models
from snorky.backend.django import subscriptable


@subscriptable
class Task(models.Model):
    title = models.CharField(max_length=100)
    completed = models.BooleanField(default=False)

    def __unicode__(self):
        return self.body

    def jsonify(self):
        from .serializers import TaskSerializer
        return TaskSerializer(self).data
