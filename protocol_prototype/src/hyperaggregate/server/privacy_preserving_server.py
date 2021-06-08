from ..netutils.message import Message, MessageType
from .utils.aggregation_tree_generation import generate_aggregation_tree
from ..shared.responsive_message_router import ResponsiveMessageRouter
import time

class SchedulingServer(ResponsiveMessageRouter):
    def __init__(self, port, target_size, group_size,
            num_actors, aggregation_profile, debug_mode=False):
        address = f'tcp://*:{port}'
        super().__init__(address, debug_mode=debug_mode)
        self.__aggregation_queue = set()
        self.__group_size = group_size
        self.__num_actors = num_actors
        self.__target_size = target_size
        # The server supplies aggregation logic to clients
        self.__aggregation_profile = aggregation_profile
        self.__next_aggregation_id = 0

    def register_callbacks(self):
        result = super().register_callbacks()
        result.update({
            MessageType.AGGREGATION_SIGNUP:
                lambda address, payload: self.__aggregation_signup(address)
        })
        return result

    def __aggregation_signup(self, address):
        if address not in self.__aggregation_queue:
            self.__aggregation_queue.add(address)
            self.send(address, Message(MessageType.SIGNUP_CONFIRMATION))
            print(f'Signed up {address}')
            if len(self.__aggregation_queue) == self.__target_size:
                self.__create_aggregation_tree_and_send_jobs()

    def __create_aggregation_tree_and_send_jobs(self):
        num_nodes = len(self.__aggregation_queue)
        tree, aggregation_pointer_dict =    \
            generate_aggregation_tree(list(self.__aggregation_queue),
            self.__group_size,
            self.__num_actors)
        print('Tree:')
        for group in tree.groups:
            print('\t' * group.level, group)
        # time.sleep(1)
        for node_addr, node_groups in aggregation_pointer_dict.items():
            self.send(
                node_addr,
                Message(MessageType.GROUP_ASSIGNMENT, (
                    self.__next_aggregation_id,
                    num_nodes,
                    node_groups,
                    self.__aggregation_profile
                )))
        self.__next_aggregation_id += 1
        self.__aggregation_queue = set()
