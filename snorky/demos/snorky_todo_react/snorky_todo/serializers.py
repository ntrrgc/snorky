# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from . import models
from rest_framework import serializers


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Task
        fields = ("id", "title", "completed")
