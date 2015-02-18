# -*- coding: utf-8 -*-

from courseme.errors import NotFound

class BaseService(object):

    __model__ = None

    def __init__(self, service_layer):
        self.services = service_layer

    def by_id(self, id):
        return self.__model__.query.get(id)

    def require_by_id(self, id):
        v = self.by_id(id)
        if v:
            return v
        else:
            raise NotFound(self.__model__, 'id', id)
