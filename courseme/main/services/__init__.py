# -*- coding: utf-8 -*-

from objective import ObjectiveService
from topic import TopicService

class Services(object):
    """Combines together the various services"""

    def __init__(self,
                 objective_factory=ObjectiveService,
                 topic_factory=TopicService):
        self.objectives = objective_factory(self)
        self.topics = topic_factory(self)
