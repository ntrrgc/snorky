Introduction
============

The DataSync service provides a systematic way to allow browser clients to fetch data from a database and keep it synchronized as changes occur.

It's important to note that DataSync **is not a database**. You still have to provide the database, the DataSync service only manages routing of change notifications from the source of the changes to the browser clients.

In order to use DataSync in your system you need to fulfill the following requirements:

* Establish which data models you have and a systematic JSON representation for each one.

  For example, in a simple SQL database each relevant table could be a model, and the JSON representation could be a dictionary with all the values of the columns, labeled by field name.

   .. code:: javascript

        {
            "title": "Something that needs to be done",
            "completed": false
        }

* Find the code paths that make changes to the database and hook them to :doc:`send notifications to Snorky <deltas>`.

  You could do this with database triggers, listening to ORM events (if you use an ORM) or simply looking for the functions who make changes in the database and modifying them.

  On the Snorky side, in order to work, the only thing that matters is that the change notifications arrive, no matter where they come from.

* Write the :doc:`dealers <dealers>`. These are small Snorky classes that receive both the data change notifications and client subscriptions. They job is to match every change notification to the adequate subscripted clients.

* Make subscription endpoints in your web application. Browser clients cannot ask Snorky directly for a subscription. Instead, they should ask the server which has access to the database. It's the duty of this server to only allow subscriptions to data the client has access right to access.
