from __future__ import absolute_import
from snorky.backend import SnorkyHTTPTransport, SnorkyBackend, SnorkyError
from django.conf import settings
from django.utils.module_loading import import_by_path
from django.db.models.signals import pre_save, post_save, pre_delete, \
        post_delete

SNORKY_DATASYNC_SERVICE = getattr(settings, "SNORKY_DATASYNC_SERVICE",
                                  "datasync_backend")

http_transport = SnorkyHTTPTransport(url=settings.SNORKY_BACKEND_URL,
                                     key=settings.SNORKY_API_KEY)
snorky_backend = SnorkyBackend(http_transport)

def publish_deltas(deltas):
    snorky_backend.call(SNORKY_DATASYNC_SERVICE,
                        "publishDeltas", deltas=deltas)

def authorize_subscription(items):
    try:
        response = snorky_backend.call(SNORKY_DATASYNC_SERVICE,
                                       "authorizeSubscription", items=items)
        return response
    except SnorkyError as err:
        raise RuntimeError("Error from Snorky server: %s" % err.args[0])

def handle_post_save(sender, instance, created, raw, using, update_fields,
        **kwargs):
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
    data = sender.objects.get(id=instance.id).jsonify()
    delta = {
        "type": "delete",
        "model": sender.__name__,
        "data": data,
    }
    instance._snorky_delta = delta

def handle_post_delete(sender, instance, using, **kwargs):
    publish_deltas([instance._snorky_delta])
    instance._snorky_delta = None

def rest_framework_jsonify(self):
    from rest_framework.settings import api_settings
    from rest_framework.renderers import UnicodeJSONRenderer
    default_serializer_base = api_settings.DEFAULT_MODEL_SERIALIZER_CLASS

    class DefaultSerializer(default_serializer_base):
        class Meta:
            model = self.__class__

    data = DefaultSerializer(self).data
    return data


def subscriptable(model_class):
    pre_save.connect(receiver=handle_pre_save, sender=model_class)
    post_save.connect(receiver=handle_post_save, sender=model_class)
    pre_delete.connect(receiver=handle_pre_delete, sender=model_class)
    post_delete.connect(receiver=handle_post_delete, sender=model_class)

    # Default jsonify method
    if not hasattr(model_class, "jsonify"):
        model_class.jsonify = rest_framework_jsonify
    return model_class