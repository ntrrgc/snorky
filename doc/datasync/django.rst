Using Snorky with Django
========================

Snorky comes with a Django connector which can prove useful if you develop the server side of your application using Django.

Subscribable models
~~~~~~~~~~~~~~~~~~~

Adding the :py:func:`snorky.backend.django.subscribable` decorator to a model class will automatically take care of sending notifications to Snorky with each change.

You only need to provide a ``jsonify()`` method in the model which returns the representation of the model in a format which can be transformed into JSON.

Example
-------

.. code-block:: python

    from django.db import models
    from snorky.backend.django import subscribable

    @subscribable
    class Task(models.Model):
        title = models.CharField(max_length=100)
        completed = models.BooleanField(default=False)

        def jsonify(self):
            return {
                "title": self.title,
                "completed": self.completed,
            }


Subscribable REST views
~~~~~~~~~~~~~~~~~~~~~~~

If you use `Django REST Framework <http://www.django-rest-framework.org/>`_ for offering a REST API, you can also use the :py:class:`ListSubscribeModelMixin` which extends ``ListModelMixin`` to provide Snorky subscription support.

.. py:class:: snorky.backend.django.rest_framework.ListSubscribeModelMixin

    Provides a ``list()`` method which understands the ``X-Snorky`` header.

    .. py:function:: get_subscription_items()

        Returns a list of dictionaries of dealer and queries which will be sent to Snorky to authorize a subscription.

        By default it returns a list of only one item, with :py:func:`get_dealer` as dealer and :py:func:`get_dealer_query` as query.

    .. py:function:: get_dealer()

        Returns the dealer this model is associated with.

        By default it returns the value of the property :py:attr:`dealer`, if any.

    .. py:function:: get_dealer_query()

        Returns the query which will be sent to the dealer.

        By default it returns the value of the property :py:attr:`dealer_query`.

    .. py:attribute:: dealer

        The dealer name to whom subscription will be bound, if :py:func:`get_dealer()` is not redefined.

    .. py:attribute:: dealer_query

        The query which will be sent to the dealer, if :py:func:`get_dealer_query` is not redefined.

Example
-------

.. code-block:: python

    from rest_framework import viewsets
    import snorky.backend.django.rest_framework as snorky


    class TaskViewSet(snorky.ListSubscribeModelMixin,
                      viewsets.ModelViewSet):
        model = models.Task
        dealer = "AllTasks"
        dealer_query = None
