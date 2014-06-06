Miau Server
===========

*Miau* is a data notification server intended to ease development of data-driven web applications with real-time functionality like notifications and automatic updates.

These capabilities rely on either `WebSocket <http://www.websocket.org/>`_, which provides full-duplex long-lived communication between the browser and the server, or `SockJS <https://github.com/mrjoes/sockjs-tornado>`_, which provides a WebSocket emulation for ancient, yet still used browsers like IE8.

Architecture
------------

::

    +----+    +-------------+    +--------------+
    | DB |<-->| Main server |<-->| User browser |
    +----+    +------+------+    +--------------+
                     |                  ^
                     v                  |
              +-------------+           |
              | Miau server |<----------·
              +-------------+
   
* *Main server* represents your usual web server where you run your web application. Miau is independent from the technology used here, so this server could run whatever you like, like a regular Django application or a PHP one served by Apache.

* Miau runs as an standalone server listening on two ports:

  - a **frontend port**, accessible by users. Communication is done either via WebSocket or via HTTP long polling (for ancient browsers).

  - a **backend port**, expected to be firewalled, used to receive commands from the main server. Communication is done through a JSON-based HTTP API.

* Each time a change in the data model occurs, e.g. writing in a database a piece of information, the Miau server shall be notified. You may implement this as part of your database abstraction API, assuming you have one. Miau provides *backend connectors* which ease this for some platforms. 
  
  - At the moment there is basic support for Python and Django ORM, but it should not be hard to port to other languages and systems.

* Users cannot subscribe directly with the Miau server but must request that to the main server.
  
  - The main server examines the request and if it finds it right (e.g. the user is logged and has appropriate permissions), the main server sends a subscription authorization to the Miau server.

   - This authorization specifies which information the user must be notified, e.g. *"message replies whose parent message id is 145"*.

   - The Miau server returns an authorization token to the main server. The main server will forward this token to the user as part of an HTTP response.

   - The user browser will connect to the Miau server and identify itself with the token. The Miau server will forward through this connection any change (insertions, updates and deletions) on the subscripted data.

* Notifications receipt on the browser are processed in Javascript code. The programmer will decide what to do with them, e.g. show pop-up notifications [1]_, reload the page or update the data in the page in real time. 
  
  - In the later case, the programmer may benefit from frameworks like AngularJS or KnockoutJS, which provide client-side templating with two-way binding. Miau comes with a *frontend connector* to ease integration with these frameworks.

Requirements
------------

* A Python 2.7 or Python 3.3+ interpreter. Miau uses the following dependencies:

  - `Tornado <http://www.tornadoweb.org/>`_

  - `simplejson <http://simplejson.readthedocs.org/en/latest/>`_

  - `SockJS <https://github.com/mrjoes/sockjs-tornado>`_ (optional for WebSocket emulation)

* Miau can run on most platforms, but for deployment Linux or UNIX based systems are recommended.

Contents
--------

.. toctree::
   services
   :maxdepth: 2

Indices tables
==============

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Footnotes
=========

.. [1] https://developer.mozilla.org/en-US/docs/Web/API/notification
