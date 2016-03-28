# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from django.db import models
from snorky.backend.django import subscribable


@subscribable
class Task(models.Model):
    title = models.CharField(max_length=100)
    completed = models.BooleanField(default=False)

    def __unicode__(self):
        return self.title
        #return self.body

    def jsonify(self):
        from .serializers import TaskSerializer
        return TaskSerializer(self).data
