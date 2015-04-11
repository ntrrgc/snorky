# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import
from rest_framework import mixins, generics
from . import authorize_subscription
from functools import wraps


class SubscribeModelMixin(object):
    dealer = None
    dealer_query = None

    def get_dealer(self):
        """Returns the dealer this model is associated with.

        By default it returns the value of the property ``dealer``, if any.
        """
        if self.dealer:
            return self.dealer
        elif hasattr(self, 'model') and self.model:
            return self.model.__name__
        else:
            raise AttributeError("Missing dealer")

    def get_dealer_query(self):
        """Returns the query which will be sent to the dealer.

        By default it returns the value of the property ``dealer_query``.
        """
        return self.dealer_query

    def get_subscription_items(self):
        """Returns a list of dictionaries of dealer and queries which will be
        sent to Snorky to authorize a subscription.

        By default it returns a list of only one item, with
        :py:func:`get_dealer` as dealer and :py:func:`get_dealer_query` as
        query.
        """
        return [{
            'dealer': self.get_dealer(),
            'query': self.get_dealer_query()
        }]

    def requested_subscription(self):
        return self.request.META.get('HTTP_X_SNORKY', '').lower() == 'subscribe'


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
            response['X-Subscription-Token'] = token
            return response
        else:
            return method(self, *args, **kwargs)
    return _subscription_in_response


class ListSubscribeModelMixin(SubscribeModelMixin,
                              mixins.ListModelMixin):
    """Provides a ``list()`` method which understands the ``X-Snorky`` header.
    """
    @subscription_in_response
    def list(self, request, *args, **kwargs):
        return super(ListSubscribeModelMixin, self).list(request, *args,
                                                         **kwargs)


class ListSubscribeAPIView(ListSubscribeModelMixin,
                           generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        """Returs a list of models."""
        return self.list(request, *args, **kwargs)


class ListSubscribeCreateAPIView(ListSubscribeModelMixin,
                                 mixins.CreateModelMixin,
                                 generics.GenericAPIView):
    """
    Concrete view for listing a queryset or creating a model instance.

    Supports subscription.
    """
    def get(self, request, *args, **kwargs):
        """Returs a list of models."""
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Creates a new instance of the model."""
        return self.create(request, *args, **kwargs)
