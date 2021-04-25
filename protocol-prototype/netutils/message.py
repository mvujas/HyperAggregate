from enum import Enum

class MessageType(Enum):
    HEALTH_CHECK, \
    HEALTH_CONFIRMATION, \
    AGGREGATION_SIGNUP, \
    SIGNUP_CONFIRMATION, \
    GROUP_ASSIGNMENT = range(5)


class Message(object):
    def __init__(self, message_type, payload=None):
        self.message_type = message_type
        self.payload = payload

    def __str__(self):
        return f'Message({self.message_type}; {self.payload})'

    def __repr__(self):
        return self.__str__()
