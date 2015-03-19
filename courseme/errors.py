# -*- coding: utf-8 -*-
"""Domain model errors"""

from courseme.util import merge

class CMBaseException(Exception):
    pass

class NotAuthorised(CMBaseException):
    pass

class ValidationError(CMBaseException):

    def __init__(self, errors=None, **kwargs):
        """
        :param errors: a dict of fieldname to strings describing accumulated
                       errors.
        :param kwargs: key, value pairs mapping fieldnames to error strings
        """
        super(ValidationError, self).__init__("Validation Error")
        errors = errors if errors else {}
        self.errors = merge(errors, kwargs)

class NotFound(CMBaseException):

    def __init__(self, model, field, field_value):
        msg = "{} not found with {}={}".format(
                str(model), field, field_value)
        super(NotFound, self).__init__(msg)
        self.model = model
        self.field = field
        self.field_value = field_value
