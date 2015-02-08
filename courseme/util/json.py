# -*- coding: utf-8 -*-
"""JSON utility functions"""

from __future__ import absolute_import
import json as j

from datetime import datetime

class _CustomEncoder(j.JSONEncoder):
    """Provide serialisation for types not handled by default encoder"""

    def default(self, obj):
        if isinstance(obj, datetime):
            encoded_object = obj.isoformat()
        else:
            encoded_object = j.JSONEncoder.default(self, obj)
        return encoded_object


def loads(s, *args, **kwargs):
    """De-serialise s to a Python object"""
    return j.loads(s, *args, **kwargs)


def dumps(obj, pretty=False, **kwargs):
    """Serialise obj to a JSON formatted byte string.

    :param pretty: pretty-printed output
    """
    seps = (', ', ': ') if pretty else (',', ':')
    indent = 2 if pretty else None
    return j.dumps(obj, separators=seps, cls=_CustomEncoder,
                   indent=indent, **kwargs)
