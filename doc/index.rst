.. title:: Snorky

|Snorky|
========

.. |Snorky| image:: logo.png
    :alt: Snorky Project

Snorky is a framework for building WebSocket servers based on common patterns.

Snorky runs on top of `Tornado <http://www.tornadoweb.org/>`_ a fast, performant, asynchronous web server and is intended to run as a separated process, therefore being able to communicate with web applications written in any programming language or framework.

Quick links
===========

* Download version 0.1.0-a4: `snorky-0.1.0-a4.tar.gz <snorky-0.1.0-a4.tar.gz>`_ (:doc:`release notes <releases>`)

* :doc:`guide`

* :doc:`datasync`

Installation
============

Snorky runs on top of Python. Versions 2.7.7+ and 3.3+ are supported.

The tarball comes with an installer, just run:

.. code::

    python setup.py install

Note you need to have pip installed in your system in order to get all the dependencies installed.

For more details, please refer to the `installation guide <guide/installation>`_.

Documentation
=============

.. toctree::
   :maxdepth: 2

   guide
   datasync
   releases
