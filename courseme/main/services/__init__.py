# -*- coding: utf-8 -*-

from objective import ObjectiveService
from topic import TopicService
from user import UserService
from message import MessageService

class Services(object):
    """Combines together the various services"""

    def __init__(self,
                 objective_factory=ObjectiveService,
                 topic_factory=TopicService,
                 user_factory=UserService,
                 message_factory=MessageService):
        self.objectives = objective_factory(self)
        self.topics = topic_factory(self)
        self.users = user_factory(self)
        self.messages = message_factory(self)
