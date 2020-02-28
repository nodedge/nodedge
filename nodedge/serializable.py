# -*- coding: utf-8 -*-
"""
A module containing Serializable "Interface". We pretend its an abstract class
"""

from collections import OrderedDict
from typing import Optional


class Serializable:
    def __init__(self):
        """
        Create data which are common to any serializable object.
        In our case we create ``self.id`` which we use in every object in Nodedge.
        """
        self.id = id(self)

    def serialize(self) -> OrderedDict:
        """
        Serialization method to serialize this class data into ``OrderedDict`` which can be stored
        in memory or file easily.

        :return: data serialized in ``OrderedDict``
        :rtype: ``OrderedDict``
        """
        raise NotImplementedError()

    def deserialize(
        self, data: dict, hashmap: Optional[dict] = None, restoreId: bool = True
    ) -> bool:
        """
        Deserialization method which take data in python ``dict`` format with helping `hashmap` containing
        references to existing entities.

        :param data: Dictionary containing serialized data
        :type data: ``dict``
        :param hashmap: Helper dictionary containing references (by id == key) to existing objects
        :type hashmap: ``dict``
        :param restoreId: True if we are creating new Sockets. False is useful when loading existing
            Sockets which we want to keep the existing object's `id`.
        :type restoreId: ``bool``
        :return: ``True`` if deserialization was successful, otherwise ``False``
        :rtype: ``bool``
        """

        if hashmap is None:
            hashmap = {}
        raise NotImplementedError()
