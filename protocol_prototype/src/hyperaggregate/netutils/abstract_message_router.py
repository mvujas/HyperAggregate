from abc import ABC, abstractmethod
from .zmqsockets import ZMQDirectSocket


class AbstractMessageRouter(ABC):
    """Boilerplate class that starts a socket and routes messages it receives
    to appropriate callback function based on the type of messages. This class
    only provides getters to internal attributes or hides them in order to
    protect integrity of the state of the attributes of the object"""
    def __init__(self, address, debug_mode=False):
        self.__debug = debug_mode
        self.__socket = ZMQDirectSocket(address, debug_mode=self.debug)
        self.__message_handlers = {}

    @abstractmethod
    def register_callbacks(self):
        """Method that should return a dictionary of message types as
        keys associated with their coresponding callbacks as values

        :rtype: dict(MessageType, (str, object) => ())
        """
        raise NotImplementedError("Method not implemented")

    def __message_callback(self, address, message):
        """Identifies appropriate callback for the given message type and
        calls it on required parameters

        :param address: The address of the sender of the message
        :type address: str

        :param message: The message
        :type message: object
        """
        # TODO: Implement invalid message handling later and checks...
        payload = message.payload
        message_type = message.message_type
        self.__message_handlers[message_type](address, payload)

    def start(self):
        """Initializes callbacks and starts the socket"""
        self.__message_handlers = self.register_callbacks()
        self.__socket.start(self.__message_callback)

    def stop(self):
        """Stops the socket"""
        self.__socket.stop()

    def send(self, address, message):
        """Function aimed at simplyfing code and hiding socket object

        :param address: The address of the sender of the message
        :type address: str

        :param message: The message
        :type message: object
        """
        self.__socket.send(address, message)

    @property
    def debug(self):
        """Returns whether debug mode is active

        :return: Is debug mode active
        :rtype: bool
        """
        return self.__debug

    @property
    def address(self):
        """Returns the address that socket is running on

        :return: The address of the socket
        :rtype: str
        """
        return self.__socket.address
