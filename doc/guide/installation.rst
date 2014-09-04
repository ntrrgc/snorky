Installation
============

In order to run the Snorky server you need a system with a working Python installation and a series of dependencies.

Supported systems
~~~~~~~~~~~~~~~~~

Snorky will work on any platform supported by `Tornado <http://www.tornadoweb.org/>`_. These include Windows, Mac, Linux and BSD.

In order to achieve the maximum performance in a production server, Linux and BSD are recommended, as they have fast event selection system calls which are supported by Tornado (``epoll`` in Linux and ``kqueue`` in BSD). At the moment of writing Tornado does not support ``IOCP`` on Windows.

For development, any system is fine.

Which Python version should I choose
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There are two versions of the Python language in use, the 2.x branch and the 3.x one.

Python 3.x changes a number of things, for example...

* In Python 2 strings were byte-based and had arbitrary encodings, whilst strings in Python 3 are character-based by default in order to manage Unicode text better.

* Some old features of the language were removed and other slightly modified. For example, ``print`` was an statement in Python 2 but it is a function in Python 3 and as a consequence, requires parentheses (i.e. ``print("Hello World")``, not ``print "Hello World"``).

* Although Python 3 has been out there for a long time, there are still some libraries that only work in Python 2. Still, it is possible to write code that works in both systems without changes, and many Python packages do this.

Snorky can work with both branches of Python. If you need to use any library which works only in Python 2, use that; in other case, use Python 3.

Installing a Python interpreter
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can download a Python installer for your platform at the `official Python web site <https://www.python.org/>`_.

If you use Windows, it is recommended that you check `Add Python to PATH` during the installation.

In Linux based systems it is often either already installed or available through the usual distribution channels.

Supported versions
------------------

Snorky works in either:

* Python 3.3 or later

* Python 2.7.7 or later. **Note it does not work with 2.7.6 or any other earlier version!**

This version requirement is because :py:func:`hmac.compare_digest` is new in Python 2.7.7. That function is needed in order to perform time attack-resilient string comparison.

You can check what version of Python you have writing ``python --version`` in a command shell.

.. note::

    **Got "not recognized as an internal or external command" error on Windows?**

    In that case you probably either did not installed a Python interpreter or, if you did, you did not add it to the system ``PATH``.

    Try running ``C:\Python34\python.exe --version`` instead, changing ``Python34`` with the version of Python that you installed (in this case it would be 3.4).

    If that works, you can either run Python everytime using the full path every time or `add it to the environmental variables of the system <http://stackoverflow.com/a/6318188>`_.

Installing the Python package manager
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Snorky carries a series of dependencies. In order to be able to install them, you need *pip*, the Python package manager.

If you use Python 3.4 or later, you already have it installed. Otherwise you can `install it following its official guide <http://pip.readthedocs.org/en/latest/installing.html>`_.

Installing Snorky from the tarball
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Download and the `last Snorky package </download>`_ and extract it. In a terminal, change to the directory where you extracted the package and run the following command.

.. code-block:: bash

    python setup.py install

That's it.
