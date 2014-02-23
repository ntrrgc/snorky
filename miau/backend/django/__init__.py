from __future__ import absolute_import
import requests
import json
from django.conf import settings
from django.utils.module_loading import import_by_path
from django.db.models.signals import pre_save, post_save, pre_delete, \
        post_delete

MIAU_JSON_ENCODER = getattr(settings, 'MIAU_JSON_ENCODER', json.JSONEncoder)
MIAU_JSON_ENCODER = import_by_path(MIAU_JSON_ENCODER)

websession = requests.session()

def send_delta(delta):
    websession.post(settings.MIAU_URL_BASE+'notify_delta',
            data=json.dumps(delta, cls=MIAU_JSON_ENCODER),
            auth=(settings.MIAU_SECRET_KEY,''))

def authorize_subscription(items):
    response = websession.post(settings.MIAU_URL_BASE+'subscription',
            data=json.dumps({'items':items}, cls=MIAU_JSON_ENCODER),
            auth=(settings.MIAU_SECRET_KEY,''))
    try:
        return response.json()['token']
    except:
        raise RuntimeError("Error from Miau server: %s" % response.content)

def handle_post_save(sender, instance, created, raw, using, update_fields, 
        **kwargs):
    if created:
        item = {
            'model_class_name': sender.__name__,
            'data': instance.jsonify()
        }
        delta = {
            'created': [item],
            'updated': [],
            'deleted': []
        }
        send_delta(delta)
    else:
        # Send a saved delta now that it's been saved
        send_delta(instance._miau_delta)
        instance._miau_delta = None


def handle_pre_save(sender, instance, raw, using, update_fields, **kwargs):
    existent_object_query = sender.objects.filter(id=instance.id)
    created = (len(existent_object_query) == 0)
    if not created:
        new_data = instance.jsonify()
        old_data = existent_object_query[0].jsonify()
        item = {
            'model_class_name': sender.__name__,
            'new_data': new_data,
            'old_data': old_data,
        }
        delta = {
            'created': [],
            'updated': [item],
            'deleted': []
        }
        # post_save will send this delta
        instance._miau_delta = delta

def handle_pre_delete(sender, instance, using, **kwargs):
    data = sender.objects.get(id=instance.id).jsonify()
    item = {
        'model_class_name': sender.__name__,
        'data': data,
    }
    delta = {'created': [], 'updated': [], 'deleted': [item]}
    instance._miau_delta = delta

def handle_post_delete(sender, instance, using, **kwargs):
    send_delta(instance._miau_delta)
    instance._miau_delta = None

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
    if not hasattr(model_class, 'jsonify'):
        model_class.jsonify = rest_framework_jsonify
    return model_class
