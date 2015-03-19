# -*- coding: utf-8 -*-
"""Service layer for Topics"""

from courseme.main.services.base import BaseService
from courseme.models import Topic

class TopicService(BaseService):
    __model__ = Topic
