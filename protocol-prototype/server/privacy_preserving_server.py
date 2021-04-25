import os,sys,inspect
current_dir = os.path.dirname(
    os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
from netutils.zmqsockets import ZMQDirectSocket
from netutils.message import Message, MessageType
from netutils.abstract_message_router import AbstractMessageRouter
from utils.aggregation_tree_generation import generate_aggregation_tree

TARGET_SIZE = 6


class SchedulingServer(AbstractMessageRouter):
    def __init__(self, port, debug_mode=False):
        address = 'tcp://*:' + port
        super().__init__(address, debug_mode=debug_mode)
        self.__aggregation_queue = set()

    def register_callbacks(self):
        return {
            MessageType.HEALTH_CHECK:
                lambda address, payload: self.__confirm_health(address),
            MessageType.AGGREGATION_SIGNUP:
                lambda address, payload: self.__aggregation_signup(address)
        }

    def __confirm_health(self, address):
        if self.debug:
            print(f'Health confirmation sent to {address}')
        confirmation_message = Message(MessageType.HEALTH_CONFIRMATION)
        self.send(address, confirmation_message)

    def __aggregation_signup(self, address):
        if address not in self.__aggregation_queue:
            self.__aggregation_queue.add(address)
            self.send(address, Message(MessageType.SIGNUP_CONFIRMATION))
            print(f'Signed up {address}')
            if len(self.__aggregation_queue) == TARGET_SIZE:
                self.__create_aggregation_tree_and_send_jobs()

    def __create_aggregation_tree_and_send_jobs(self):
        aggregation_tree, aggregation_pointer_dict =    \
            generate_aggregation_tree(list(self.__aggregation_queue), 3, 2)
        self.__aggregation_queue = set()
        print(aggregation_tree)
        print(aggregation_pointer_dict)
