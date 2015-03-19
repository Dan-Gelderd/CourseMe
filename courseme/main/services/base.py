# -*- coding: utf-8 -*-

from courseme.errors import NotFound

class BaseService(object):
    """Base class to inherit Service implementations from.

    Provides a few convenience methods.
    Requires that `__model__` is populated with the model that the Service
    implementation manages.
    """

    __model__ = None

    def __init__(self, service_layer):
        self.services = service_layer

    def by_id(self, id):
        """Lookup model by id, returns None if no matching model is found"""
        return self.__model__.query.get(id)

    def require_by_id(self, id):
        """Lookup model by id, raises NotFound if no matching model is found"""
        v = self.by_id(id)
        if v:
            return v
        else:
            raise NotFound(self.__model__, 'id', id)
