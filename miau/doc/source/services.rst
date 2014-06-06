========
Services
========

In order to ease the development of real-time collaborative applications, Miau provides several *services*. Services are data handlers which process information from clients and other processes and do something with it, usually transforming and routing the information to interested parties.

Built-in services
=================

The following services come built-in with Miau. They're fully supported by core developers.

Data notification service
-------------------------

This service allow web applications to receive notifications about changes occurred in the data model on real time. For this to work, applications that make changes must inform of them to Miau using an specific API.

User to user messaging
----------------------

Sometimes it is desired for users to be able to communicate in a real-time fashion without persisting data anywhere. This often needed e.g. for multi-player games.

This service acts like a broker, receiving messages with a documented envelope and delivering them to one or more users.

Miau does not inspect messages body, which can be arbitrary JSON-encoded entities as long as they are well formed, so applications must process messages received from this service with care.

Pub-Sub messaging
-----------------

*Pub-Sub* or publish-subscribe messaging allows several parties within a group to send messages to all the other parties, similarly to a group chat.

For a group of entities to use *Pub-Sub* they must get a *channel* first (like a chat room). Channels may be free to create and join or they may require permissions.

Authentication service
----------------------

Some services, like user messaging and Pub-Sub need authentication in order to be secure. Miau can expose several authentication mechanisms no clients. Once users have been authenticated, messages sent by them through other services may be enveloped with the user credentials if required.
