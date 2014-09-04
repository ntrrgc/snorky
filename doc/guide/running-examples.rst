Running the examples
====================

Snorky bundles with a few small demonstration applications that you can use to verify it works.

You can find them in ``snorky/demos`` inside the project root.

Snorky ToDo demo
~~~~~~~~~~~~~~~~

In ``snorky/demos/snorky_todo`` you can find a simple note taking application. The demo is based in `TodoMVC <http://todomvc.com/>`_. It works with Django and AngularJS.

In order to run it, first you must install its dependencies (e.g. Django). To do so you can run the following command:

.. code-block:: bash

    pip install -r requirements.txt

.. note::

    If you are on Windows and you get "not recognized as an internal or external command" error, check your PATH.

    You must add both the Python directory (e.g. ``C:\Python34``) and the Python script directory where pip is installed (e.g. ``C:\Python34\Script``).

Django requires a database to run. The demo uses SQLite, which is included in Python by default. In order to create the database run:

.. code-block:: bash

    python manage.py syncdb

Reply ``no`` when it asks you to create a super user, you don't need it.

After that, you can run the Django production server.

.. code-block:: bash

    python manage.py runserver

Open another terminal, go to the demo directory and run the Snorky server.

.. code-block:: bash

    python run_snorky_server.py

You can open http://localhost:8000/ in your browser and try adding some notes. Opening it in several browser windows should show how changes are applied on both automatically.
