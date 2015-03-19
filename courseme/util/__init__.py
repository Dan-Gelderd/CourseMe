# -*- coding: utf-8 -*-

def merge(d1, *ds):
    """Merge given dicts, giving precedence to the right"""
    res = {}
    res.update(d1)
    for d in ds:
        res.update(d)
    return res
