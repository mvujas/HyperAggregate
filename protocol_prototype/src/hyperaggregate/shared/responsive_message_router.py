from ..netutils.abstract_message_router import AbstractMessageRouter
from ..netutils.message import Message, MessageType

class ResponsiveMessageRouter(AbstractMessageRouter):
    """Implements network response functionality that is shared between client
    and server
    """
    def __init__(self, address, debug_mode):
        super().__init__(address, debug_mode=debug_mode)

    def register_callbacks(self):
        return {
            MessageType.HEALTH_CHECK:
                lambda address, payload: self.__confirm_health(address)
        }

    def __confirm_health(self, address):
        """Sends health confirmation message (meaning the node is still up and
        running) to the node on the passed address

        :param address: The address of the node that asked for the health update
        :type address: str
        """
        if self.debug:
            print(f'Health confirmation sent to {address}')
        confirmation_message = Message(MessageType.HEALTH_CONFIRMATION)
        self.send(address, confirmation_message)
