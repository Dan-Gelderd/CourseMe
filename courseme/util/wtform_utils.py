# -*- coding: utf-8 -*-
"""WTForm utility functions"""

def blank_to_none(v):
    return v or None

def select_choices(list, add_blank=False):
    choices = [(str(obj.id), obj.name) for obj in list]
    if add_blank:
        choices.insert(0, ('', ''))
    return choices