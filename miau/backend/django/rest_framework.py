from __future__ import absolute_import
from rest_framework import mixins, generics
from . import authorize_subscription
from functools import wraps


class SubscribeModelMixin(object):
    dealer_name = None
    model_key = None

    def get_dealer_name(self):
        if self.dealer_name:
            return self.dealer_name
        elif hasattr(self, 'model') and self.model:
            return self.model.__name__
        else:
            raise AttributeError("Missing dealer_name")

    def get_model_key(self):
        return self.model_key

    def get_subscription_items(self):
        return [{
            'dealer_name': self.get_dealer_name(),
            'model_key': self.get_model_key()
        }]

    def requested_subscription(self):
        return self.request.META.get('HTTP_X_MIAU', '').lower() == 'subscribe'


def subscription_in_response(method):
    """
    Decorates a response-returning method so it authorizes a subscription if
    the requests asks for it.
    """
    @wraps(method)
    def _subscription_in_response(self, *args, **kwargs):
        if self.requested_subscription():
            items = self.get_subscription_items()
            token = authorize_subscription(items)
            response = method(self, *args, **kwargs)
            response['X-Miau-Token'] = token
            return response
        else:
            return method(self, *args, **kwargs)
    return _subscription_in_response
    

class ListSubscribeModelMixin(SubscribeModelMixin,
                              mixins.ListModelMixin):
    @subscription_in_response
    def list(self, request, *args, **kwargs):
        return super(ListSubscribeModelMixin, self).list(request, *args, 
                                                         **kwargs)


class ListSubscribeAPIView(ListSubscribeModelMixin,
                           generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ListSubscribeCreateAPIView(ListSubscribeModelMixin,
                                 mixins.CreateModelMixin,
                                 generics.GenericAPIView):
    """
    Concrete view for listing a queryset or creating a model instance.

    Supports subscription.
    """
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
