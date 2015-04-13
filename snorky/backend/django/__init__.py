# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import
import json
from snorky.backend import SnorkyHTTPTransport, SnorkyBackend, SnorkyError
from django.conf import settings
from django.utils.module_loading import import_by_path
from django.db.models.signals import pre_save, post_save, pre_delete, \
        post_delete

SNORKY_DATASYNC_SERVICE = getattr(settings, "SNORKY_DATASYNC_SERVICE",
                                  "datasync_backend")
"""The name of the DataSyncService instance registered in Snorky."""

SNORKY_JSON_ENCODER = getattr(settings, 'SNORKY_JSON_ENCODER',
                              json.JSONEncoder)
SNORKY_JSON_ENCODER = import_by_path(SNORKY_JSON_ENCODER)
"""JSON encoder class used to send messages to Snorky, by default it is
`json.JSONEncoder`."""

class JSONModule(object):
    @staticmethod
    def dumps(obj, *args, **kwargs):
        kwargs['cls'] = SNORKY_JSON_ENCODER
        return json.dumps(obj, *args, **kwargs)

    @staticmethod
    def loads(obj, *args, **kwargs):
        return json.loads(obj, *args, **kwargs)

http_transport = SnorkyHTTPTransport(url=settings.SNORKY_BACKEND_URL,
                                     key=settings.SNORKY_API_KEY)
snorky_backend = SnorkyBackend(http_transport, json=JSONModule)

def publish_deltas(deltas):
    """Send deltas to the Snorky server."""
    snorky_backend.call(SNORKY_DATASYNC_SERVICE,
                        "publishDeltas", deltas=deltas)

def authorize_subscription(items):
    """Authorize a subscription with the specified items.

       :param items: A list of dictionaries containing the subscription
       requests. Each dictionary must specify the fields ``dealer`` and
       ``query``.
    """
    try:
        response = snorky_backend.call(SNORKY_DATASYNC_SERVICE,
                                       "authorizeSubscription",
                                       items=items)
        return response
    except SnorkyError as err:
        raise RuntimeError("Error from Snorky server: %s" % err.args[0])

def handle_post_save(sender, instance, created, raw, using, update_fields,
        **kwargs):
    """Called after a subscribable model is saved.

    If the item was created it publishes an insertion delta with the current
    data (which will include also the ``id`` field even if it was not assigned
    before saving).

    If the item was updated it publishes the update delta stored in the
    `_snorky_delta` property..
    """
    if created:
        publish_deltas([{
            "type": "insert",
            "model": sender.__name__,
            "data": instance.jsonify(),
        }])
    else:
        # Send a saved delta now that it"s been saved
        publish_deltas([instance._snorky_delta])
        instance._snorky_delta = None


def handle_pre_save(sender, instance, raw, using, update_fields, **kwargs):
    """Called when a subscribable model is about to be saved.

    Queries the database to get the old data. If no data is found the item is assumed to be new.

    If the item did exist before, stores an update delta in ``_snorky_delta``.
    """
    existent_object_query = sender.objects.filter(id=instance.id)
    created = (len(existent_object_query) == 0)
    if not created:
        new_data = instance.jsonify()
        old_data = existent_object_query[0].jsonify()
        delta = {
            "type": "update",
            "model": sender.__name__,
            "newData": new_data,
            "oldData": old_data,
        }
        # post_save will send this delta
        instance._snorky_delta = delta

def handle_pre_delete(sender, instance, using, **kwargs):
    """Called when a subscribable model is about to be deleted.

    Fetches the current data of the object from the databases and stores it in
    an internal property within the model, ``_snorky_delta``."""
    data = sender.objects.get(id=instance.id).jsonify()
    delta = {
        "type": "delete",
        "model": sender.__name__,
        "data": data,
    }
    instance._snorky_delta = delta

def handle_post_delete(sender, instance, using, **kwargs):
    """Called after a subscribable model is removed.

    Publishes a deletion delta, using the data stored in ``_snorky_delta``.
    """
    publish_deltas([instance._snorky_delta])
    instance._snorky_delta = None

def rest_framework_jsonify(self):
    """Serialize a model with the default serializer class of Django REST
    Framework."""
    from rest_framework.settings import api_settings
    from rest_framework.renderers import UnicodeJSONRenderer
    default_serializer_base = api_settings.DEFAULT_MODEL_SERIALIZER_CLASS

    class DefaultSerializer(default_serializer_base):
        class Meta:
            model = self.__class__

    data = DefaultSerializer(self).data
    return data


def subscribable(model_class):
    """Decorator that adds signals to make a Django model class emit change
    notifications automatically."""
    pre_save.connect(receiver=handle_pre_save, sender=model_class)
    post_save.connect(receiver=handle_post_save, sender=model_class)
    pre_delete.connect(receiver=handle_pre_delete, sender=model_class)
    post_delete.connect(receiver=handle_post_delete, sender=model_class)

    # Default jsonify method
    if not hasattr(model_class, "jsonify"):
        model_class.jsonify = rest_framework_jsonify
    return model_class
