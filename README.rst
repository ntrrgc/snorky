.. image:: https://raw.githubusercontent.com/ntrrgc/snorky/master/doc/logo.png

Snorky is a framework for building WebSocket servers based on patterns.

.. image:: https://travis-ci.org/ntrrgc/snorky.svg?branch=master
    :target: https://travis-ci.org/ntrrgc/snorky

.. image:: https://readthedocs.org/projects/snorky/badge/?version=latest
    :target: http://docs.snorkyproject.org/en/latest/

Snorky runs on top of `Tornado <http://www.tornadoweb.org/>`_ a fast, performant, asynchronous web server. Snorky is intended to run as a separated process, therefore being able to communicate with web applications written in any programming language or web framework.

You can use Snorky DataSync service to synchronize a server-side database with a web view. You only need to add hooks somewhere (e.g. in an ORM layer) so that Snorky is notified of them. Clients need a *subscription token* in order to get data from Snorky.

Snorky integrates in the server side with `Django <https://www.djangoproject.com/>`_ ORM and `Django REST Framework <http://www.django-rest-framework.org/>`_ in order to streamline this process, but you can use it with any server technology with a bit more coding. On the client side, Snorky provides a JavaScript library that handles connections and notifications. You can also connect it easily with client-side MVC-like frameworks like `AngularJS <https://angularjs.org/>`_ in order to close the gap between server and client MVC.

You can use the Snorky architecture of self-contained services with an RPC over JSON interface to add new functionality other than data entities synchronization: e.g. PubSub, person to person chat or cursor synchronization.

Installation
============

To run a Snorky server you only need a Python interpreter (both Python 2 and Python 3 are fine) and a few dependencies.

You can install Snorky from the Python package index:

.. code:: bash

    pip install snorky

Documentation
=============

Snorky documentation is hosted in *Read the Docs*. You can check it out at http://docs.snorkyproject.org/.

Simple PubSub server
====================

Snorky groups functionality in *services*, which are classes intended to attend user events in different ways. The following code shows a Snorky server with an PubSub service.

.. code:: python

    from tornado.ioloop import IOLoop
    from tornado.web import Application
    from snorky import ServiceRegistry

    from snorky.request_handlers.websocket import SnorkyWebSocketHandler
    from snorky.services.pubsub import PubSubService

    if __name__ == "__main__":
        service_registry = ServiceRegistry()
        # Every service instance has a name, here: pubsub
        service_registry.register_service(PubSubService("pubsub"))

        # Register HTTP endpoint: ws://localhost:8002/websocket
        application = Application([
            # Each endpoint connects clients with the services of a registry
            SnorkyWebSocketHandler.get_route(service_registry, "/websocket"),
        ])
        application.listen(8002, address="") # listen on all network interfaces

        try:
            print("Snorky running...")
            IOLoop.instance().start()
        except KeyboardInterrupt:
            pass

This is the HTML code of a minimal application making use of this service:

.. code:: html

    <!DOCTYPE html>
    <html lang="en">
    <head>
      <title>Snorky is easy</title>
      <script src="lib/jquery.min.js"></script>
      <script src="lib/snorky.bundle.js"></script>
    </head>
    <body>
      <form>
        <input type="text" id="message">
        <button type="submit">Send</button>
      </form>
      <ul id="messages">
      </ul>
      <script src="pubsub.js"></script>
    </body>
    </html>

This is the JavaScript code:

.. code:: javascript

    var snorky = new Snorky(WebSocket, "ws://localhost:8002/websocket", {
      "pubsub": Snorky.PubSub
    });
    var pubsub = snorky.services.pubsub;

    pubsub.subscribe({channel: 'messages'})
    .then(function() {
      // Confirmation received! (optional)
    });

    pubsub.messagePublished.add(function(messageObject) {
      $('#messages').append(
        $('<li/>', {
        text: messageObject.message
      }));
    });

    $('form').on('submit', function(event) {
      event.preventDefault(); // don't reload the page

      pubsub.publish({
        channel: 'messages',
        message: $('#message').val()
      });
    });

DataSync service with Django and Angular
========================================

The following code shows a Django model integrated with Snorky. The ``@subscribable`` decorator adds event handlers that send notifications to the Snorky server configured in Django's ``settings.py`` file.

.. code:: python

    from django.db import models
    from snorky.backend.django import subscribable

    @subscribable
    class Task(models.Model):
        title = models.CharField(max_length=100)
        completed = models.BooleanField(default=False)

        def jsonify(self):
            # This is the model representation sent to Snorky
            # In this case it is generated by Django REST Framework,
            # but it could a simple `return json.dumps(...)`.
            from .serializers import TaskSerializer
            return TaskSerializer(self).data

The following code shows the Snorky server. It contains two registries, a frontend one (public), which is exposed to the end users and a backend one (private) who is exposed only to the server applications, protected by a password.

.. code:: python

    #-----------------------------------------------------------------------------#
    # Dealers (model classes and filters)                                         #
    #-----------------------------------------------------------------------------#

    class AllTodos(BroadcastDealer):
        name = "AllTasks"
        model = "Task"

    #-----------------------------------------------------------------------------#
    # Server startup                                                              #
    #-----------------------------------------------------------------------------#
    if __name__ == "__main__":
        # Create two services
        datasync = DataSyncService("datasync", [AllTodos])
        datasync_backend = DataSyncBackend("datasync_backend", datasync)

        logging.basicConfig(level=logging.INFO)

        # Register the frontend and backend services in different handlers
        frontend = ServiceRegistry([datasync])
        backend = ServiceRegistry([datasync_backend])

        # Create a WebSocket frontend
        app_frontend = Application([
            SnorkyWebSocketHandler.get_route(frontend, "/ws"),
        ])
        app_frontend.listen(5001)

        # Create a backend, set a secret key, port and address
        app_backend = Application([
            ("/backend", BackendHTTPHandler, {
                "service_registry": backend,
                "api_key": "swordfish"
            })
        ])
        app_backend.listen(5002)

        # Start processing
        try:
            IOLoop.instance().start()
        except KeyboardInterrupt:
            pass


Dealers, like ``AllTodos`` are classes that track client subscriptions to certain kinds of models. There are several kinds of dealers. *Broadcast* dealers notify of all changes to all subscribers, but there are other dealers that allow to specify arbitrary filtering.

Data change notifications are sent from Django ORM to the ``DataSyncBackend`` service in the backend registry, accessible through port 5002. Clients connect to receive notifications to the ``DataSyncService`` from the frontend registry, accessible through port 5001.

This is the API views file, built with `Django REST Framework <http://www.django-rest-framework.org/>`_. It supports ``GET``, ``POST``, ``PUT`` and ``DELETE``.

.. code:: python

    from . import models
    from rest_framework import viewsets
    import snorky.backend.django.rest_framework as snorky

    class TaskViewSet(snorky.ListSubscribeModelMixin,
                      viewsets.ModelViewSet):
        model = models.Task
        dealer = "AllTasks"

Using ``ListSubscribeModelMixin``, the view will accept an optional HTTP header, ``X-Snorky: Subscribe`` allowing the client to request a *subscription token* that can be exchanged for real time notifications over WebSocket.

Finally, the following code shows how data can be fetched in AngularJS, in this case querying the REST API with `Restangular <https://github.com/mgonto/restangular>`_:

.. code:: javascript

    var snorky = new Snorky(WebSocket, "ws://localhost:5001/ws", {
      "datasync": Snorky.DataSync
    });
    var deltaProcessor = new Snorky.DataSync.CollectionDeltaProcessor();
    snorky.services.datasync.onDelta = function(delta) {
      // Called each time a data change notification (delta) is received.
      // CollectionDeltaProcessor is a class that applies these deltas
      // in a collection (usually an array).
      deltaProcessor.processDelta(delta);

      // Here we could also inspect the delta element and show alerts to the
      // user or play a sound when data changes.
    };

    var tasks = Restangular.all("tasks").getListAndSubscription()
    .then(function(response) {
      var taskArray = response.data;

      // A collection wraps an array over an interface which is understood
      // by deltaProcessor.
      //
      // e.g. when an insertion delta is received, deltaProcessor will push
      // an element in the collection.
      //
      var taskCollection = new Snorky.DataSync.ArrayCollection(taskArray, {
        transformItem: function(item) {
          // Allows us to define how a data element received from a delta as
          // simple JSON will be translated to an element of this array.

          // This is useful if we use fat elements (e.g. each element has a
          // .delete() method).
          return Restangular.restangularizeElement(
            null, item, "tasks", true, response.data, null
          );
        }
      })

      // Tell the collection delta processor: updates of elements of class Task
      // should be applied to taskCollection.
      deltaProcessor.collections["Task"] = taskCollection;

      // Send our new subscription token to Snorky, so that we can receive
      // notifications for changes in tasks.
      snorky.services.datasync.acquireSubscription({
        token: response.subscriptionToken
      });

      // Return the array, which will be automatically updated thanks to
      // Snorky deltaProcessor.
      return taskArray;
    });

``.getListAndSubscription()`` is an `extension method <https://github.com/mgonto/restangular#adding-custom-methods-to-collections>`_ that adds the ``X-Snorky: Subscribe`` header to the request and puts the content of the ``X-Subscription-Token`` response header in ``response.subscriptionToken``. Changes to taskArray will be automatically detected by AngularJS and will trigger the template code to update the view.

The following code shows how this array of tasks could be used in an AngularJS template:

.. code:: html

    <ul id="todo-list">
      <li ng-repeat="todo in todos track by $index">
        <div class="view">
          <input class="toggle" type="checkbox"
           ng-model="todo.patchCompleted"
           ng-model-options="{ getterSetter: true }">

          <label ng-dblclick="editTodo(todo)">{{todo.title}}</label>

          <button class="destroy" ng-click="removeTodo(todo)"></button>
        </div>
      </li>
    </ul>

The full demo code is available in `snorky/demos/snorky_todo_angular`, based on `TodoMVC <http://todomvc.com/>`_.

Other protocols
===============

Although Snorky was built upon WebSocket, there is nothing in it preventing you to use other protocols. Indeed, Snorky comes with a `SockJS <https://github.com/mrjoes/sockjs-tornado>`_ so that you can use it with jurassic browsers (IE6+) with no WebSocket support, should you ever need that.

License
=======

Snorky is licensed under the terms of `Mozilla Public License 2.0 <https://www.mozilla.org/MPL/2.0/>`_.

This means you can use the software in both free and proprietary works of any other license without restrictions.

In case you modify the library code **and** make it available to others, those modifications are covered by the license too, which implies you must make source code available **for the modified library files**. This does not forbid you from developing extensions with other licenses though, as long as they don't modify Snorky source code or maintain the MPL license for these parts.

