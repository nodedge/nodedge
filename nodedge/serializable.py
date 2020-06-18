# -*- coding: utf-8 -*-
"""
Serializable "interface" module. It is an abstract class.
"""

from collections import OrderedDict
from typing import Optional


class Serializable:
    """
    :class:`~nodedge.serializable.Serializable` class
    """

    def __init__(self):
        """
        Create data which are common to any serializable object.

        It stores the id of the object used in the
        :class:`~nodedge.scene_history.SceneHistory`,
        the :class:`~nodedge.scene_clipboard.SceneClipboard`, and the file structure.
        """
        self.id = id(self)

    def serialize(self) -> OrderedDict:
        """
        Serialization method to serialize this class data into ``OrderedDict`` which
        can be stored in memory or file easily.

        :return: data serialized in ``OrderedDict``
        :rtype: ``OrderedDict``
        """
        raise NotImplementedError()

    def deserialize(
        self,
        data: dict,
        hashmap: Optional[dict] = None,
        restoreId: bool = True,
        *args,
        **kwargs
    ) -> bool:
        """
        Deserialization method which take data in python ``dict`` format with helping
        `hashmap` containing references to existing entities.

        :param data: dictionary containing serialized data
        :type data: ``dict``
        :param hashmap: helper dictionary containing references (by id == key) to
            existing objects
        :type hashmap: ``dict``
        :param restoreId: ``True`` if we are creating new sockets. ``False`` is useful
            when loading existing sockets which we want to keep the existing
            object's `id`
        :type restoreId: ``bool``
        :return: ``True`` if deserialization was successful, ``False`` otherwise
        :rtype: ``bool``
        """

        if hashmap is None:
            hashmap = {}
            hashmap.clear()
        raise NotImplementedError()
