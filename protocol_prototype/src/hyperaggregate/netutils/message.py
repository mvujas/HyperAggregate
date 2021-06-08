from enum import Enum

class MessageType(Enum):
    """Enum of possible message types"""
    HEALTH_CHECK, \
    HEALTH_CONFIRMATION, \
    AGGREGATION_SIGNUP, \
    SIGNUP_CONFIRMATION, \
    GROUP_ASSIGNMENT, \
    PARTIAL_MODEL_SHARE, \
    FINAL_PARTIAL_SHARES, \
    MODEL_UPDATE, \
    NO_MODEL_NEEDED = range(9)


class Message(object):
    """The class representing messages exhanged between nodes on the network"""
    def __init__(self, message_type, payload=None):
        """:param message_type: The type of the message
        :type message_type: MessageType

        :param payload: The payload of the message (optional)
        :type payload: object or None
        """
        self.message_type = message_type
        self.payload = payload

    def __str__(self):
        return f'Message({self.message_type}; {self.payload})'

    def __repr__(self):
        return self.__str__()
