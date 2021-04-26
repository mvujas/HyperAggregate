import os,sys,inspect
current_dir = os.path.dirname(
    os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
from netutils.abstract_message_router import AbstractMessageRouter
from netutils.message import Message, MessageType

class ResponsiveMessageRouter(AbstractMessageRouter):
    def __init__(self, address, debug_mode):
        super().__init__(address, debug_mode=debug_mode)

    def register_callbacks(self):
        return {
            MessageType.HEALTH_CHECK:
                lambda address, payload: self.__confirm_health(address)
        }

    def __confirm_health(self, address):
        if self.debug:
            print(f'Health confirmation sent to {address}')
        confirmation_message = Message(MessageType.HEALTH_CONFIRMATION)
        self.send(address, confirmation_message)
