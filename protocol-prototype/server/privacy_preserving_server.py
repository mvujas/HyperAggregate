import os,sys,inspect
current_dir = os.path.dirname(
    os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
from netutils.zmqsockets import ZMQDirectSocket
from netutils.message import Message, MessageType


TARGET_SIZE = 2


class SchedulingServer:
    def __init__(self, port, debug_mode=False):
        self.__address = 'tcp://*:' + port
        self.__debug = debug_mode
        self.__socket = ZMQDirectSocket(self.__address, debug_mode=debug_mode)
        self.__aggregation_queue = set()
        self.__initialize_handlers()

    def __initialize_handlers(self):
        self.__message_handlers = {
            MessageType.HEALTH_CHECK:
                lambda address, payload: self.__confirm_health(address),
            MessageType.AGGREGATION_SIGNUP:
                lambda address, payload: self.__aggregation_signup(address)
        }

    def start(self):
        self.__socket.start(self.__message_callback)

    def __message_callback(self, address, message):
        # TODO: Implement invalid message handling later and checks...
        payload = message.payload
        message_type = message.message_type
        self.__message_handlers[message_type](address, payload)

    def __confirm_health(self, address):
        if self.__debug:
            print(f'Health confirmation sent to {address}')
        confirmation_message = Message(MessageType.HEALTH_CONFIRMATION)
        self.__socket.send(address, confirmation_message)

    def __aggregation_signup(self, address):
        if address not in self.__aggregation_queue:
            self.__aggregation_queue.add(address)
            self.__socket.send(address, Message(MessageType.SIGNUP_CONFIRMATION))
            print(f'Signed up {address}')
            if len(self.__aggregation_queue) == TARGET_SIZE:
                self.__create_aggregation_tree_and_send_jobs()

    def __create_aggregation_tree_and_send_jobs(self):
        self.__aggregation_queue = set()
