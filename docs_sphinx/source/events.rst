Event system
============

Nodedge uses its own events (and tries to avoid using ``Signal``) to handle logic
happening inside the Scene. If a class does handle some events, they are usually described
at the top of the page in this documentation.

Any of the events is subscribable to and the methods for registering callback are called:

.. code-block:: python

    add<EventName>Listener(callback)

You can register to any of these events any time.

Events used in Nodedge:
--------------------------

:class:`~nodedge.scene.Scene`
+++++++++++++++++++++++++++++++++++++

.. include:: events_scene.rst


:class:`~nodedge.scene_history.SceneHistory`
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

.. include:: events_scene_history.rst
