# -*- coding: utf-8 -*-
"""WTForm utility functions"""

def blank_to_none(v):
    return v or None

def list_to_tuples(list):
    return [(str(obj.id), obj.name) for obj in list]