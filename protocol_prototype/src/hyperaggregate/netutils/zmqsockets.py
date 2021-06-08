import zmq
import dill
import time
import queue
import threading

from multiprocessing import Queue, Process, Value
from ctypes import c_bool

# To simulate bandwidth
from pympler.asizeof import asizeof
SIMULATED_SPEED = 100e+6

class MessageWrapper(object):
    """Message wrapper that includes important additional information
    with the message (namely sender and destination address)
    """
    def __init__(self, sender_addr, dest_addr, message):
        self.sender_addr = sender_addr
        self.destination_address = dest_addr
        self.message = message

    def __str__(self):
        return f'''MessageWrapper(
\tsender: {self.sender_addr},
\tdestination: {self.destination_address}
)'''

    def __repr__(self):
        return self.__str__()


class ZMQDirectSocket:
    """Abstraction of peer to peer network communication interface implemented
    with ZeroMQ
    """
    def __init__(self, address, debug_mode=False):
        self.__address = address
        self.__debug = debug_mode
        self.__send_sockets = {}
        self.__send_sockets_lock = threading.Lock()
        self.__message_queue = Queue()
        self.__receive_messages_process = None
        self.__process_messages_thread = None
        self.__running = Value(c_bool, False)

    @property
    def address(self):
        """Returns the address that socket is running on

        :return: Address of the socket
        :rtype: str
        """
        return self.__address

    def stop(self):
        """Sets running indicator to false which stops the socket from
        receiving anymore messages (effectively stops message processing
        thread)
        """
        self.__running.value = False
        self.__receive_messages_process.join()
        self.__process_messages_thread.join()
        self.__process_messages_thread = None
        self.__receive_messages_process = None

    def start(self, on_message_received_callback):
        """Initliaze process that waits for messages and the thread that
        processes them and starts them

        :param on_message_received_callback: Function that accepts a sender
            address and the message payload when a message is received
        :type on_message_received_callback: function (str, object) => ()
        """
        if self.__receive_messages_process is None:
            self.__running.value = True
            self.__receive_messages_process = Process(
                target=self.__wait_message
            )
            self.__process_messages_thread = threading.Thread(
                target=self.__process_messages,
                args=(on_message_received_callback,)
            )
            self.__receive_messages_process.start()
            self.__process_messages_thread.start()

    def __wait_message(self):
        """Message receiving loop"""
        context = zmq.Context()
        receive_socket = context.socket(zmq.DEALER)
        receive_socket.bind(self.__address)
        print(f'Starting socket at {self.__address}')
        while self.__running.value:
            try:
                message = receive_socket.recv_pyobj(zmq.NOBLOCK)
                self.__message_queue.put(message)
                if self.__debug:
                    print('Message received:', message)
            except zmq.Again:
                time.sleep(1e-3)
        print(f'Socket on {self.__address} is closing.')

    def __process_messages(self, on_message_received_callback):
        """Message processing loop, unwraps messages and calls the callback
        function with the unwrapped message

        :param on_message_received_callback: Function that accepts a sender
            address and the message payload when a message is received
        :type on_message_received_callback: function (str, object) => ()
        """
        while self.__running.value or not self.__message_queue.empty():
            try:
                message = self.__message_queue.get(False, 0.01)
                on_message_received_callback(
                    message.sender_addr,
                    dill.loads(message.message))
            except queue.Empty:
                time.sleep(1e-3)

    def __get_socket(self, dest_addr):
        """Helper method to avoid initializing two sockets for the same
        destination address. This is only workaround around some
        misunderstandings in ZeroMQ and this method may be removed in the
        future"""
        self.__send_sockets_lock.acquire()
        try:
            socket = self.__send_sockets.get(dest_addr)
            if socket is None:
                context = zmq.Context()
                socket = context.socket(zmq.DEALER)
                socket.connect(dest_addr)
                self.__send_sockets[dest_addr] = socket
            return socket
        finally:
            self.__send_sockets_lock.release()

    def send(self, dest_address, message):
        """Wraps a message and send it to the specified destination

        :param dest_address: An address to send the message to
        :type dest_address: str

        :param message: The message
        :type message: object
        """
        try:
            wrapped_message = MessageWrapper(
                self.__address,
                dest_address,
                dill.dumps(message)
            )

            # Bandwidth simulation
            # message_size = asizeof(wrapped_message)
            # wait_time = message_size / SIMULATED_SPEED
            # time.sleep(wait_time)

            socket = self.__get_socket(dest_address)
            socket.send_pyobj(wrapped_message, flags=zmq.NOBLOCK)
            if self.__debug:
                print('Message sent to', dest_address)
        except Exception as e:
            print('Failed to send a message')
            if self.__debug:
                print('Reason for failing to send the message:', e)
