Serialization
=============

All of serializable classes derive from :class:`~nodedge.serializable.Serializable` class.
`Serializable` does create commonly used parameters for our classes. In our case it is just ``id``
attribute.

`Serializable` defines two methods which should be overridden in child classes:

- :py:func:`~nodedge.serializable.Serializable.serialize`
- :py:func:`~nodedge.serializable.Serializable.deserialize`

According to coding-standards we keep these two functions on the bottom of the class source code.

To contain all of the data we use ``OrderedDict`` instead of regular `dict`. Mainly because we want
to retain the order of parameters serialized in files.

Classes which derive from :class:`~nodeeditr.serializable.Serializable`:

- :class:`~nodedge.scene.Scene`
- :class:`~nodedge.node.Node`
- :class:`~nodedge.content_widget.QDMNodeContentWidget`
- :class:`~nodedge.edge.Edge`
- :class:`~nodedge.socket.Socket`
