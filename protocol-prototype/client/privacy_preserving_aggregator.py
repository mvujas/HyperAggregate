import os,sys,inspect
current_dir = os.path.dirname(
    os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
from netutils.message import Message, MessageType
from shared.responsive_message_router import ResponsiveMessageRouter
from threading import Lock, Condition

from utils.aggregation_model_queue import AggregationModelQueue
from utils.partial_model_message import PartialModelMessage

import random

from enum import Enum

from queue import Empty


DIGITS_TO_KEEP = 6


class ClientState(Enum):
    NO_JOB, \
    WAITING_SIGNUP_CONFIRMATION, \
    WAITING_JOB, \
    DOING_JOB = range(4)


class PrivacyPreservingAggregator(ResponsiveMessageRouter):
    def __init__(self, address, server_address, debug_mode=False):
        super().__init__(address, debug_mode=debug_mode)
        self.__server_address = server_address
        self.__state = ClientState.NO_JOB
        self.__state_lock = Lock()
        self.__aggregation_model_queues = None
        self.__resulting_model = None
        self.__resulting_model_lock = Lock()
        self.__aggregation_model_queues_lock = Lock()
        self.__wait_aggregation = Condition()
        self.__wait_model = Condition()
        self.__aggregation_group_list = None
        self.__num_nodes = None
        self.__aggregation_profile = None

    def register_callbacks(self):
        """Assigns proper callbacks to corresponding messages"""
        result = super().register_callbacks()
        result.update({
            MessageType.SIGNUP_CONFIRMATION:
                lambda address, payload: self.__handle_signup_confirmation(payload),
            MessageType.GROUP_ASSIGNMENT:
                lambda address, payload: self.__handle_group_assignment(payload),
            MessageType.PARTIAL_MODEL_SHARE: self.__handle_partial_model,
            MessageType.FINAL_PARTIAL_SHARES: self.__handle_final_shares,
            MessageType.MODEL_UPDATE: self.__handle_model_update
        })
        return result

    def __send_to_server(self, message):
        """Helper function to simplify code that sends a message to the server"""
        self.send(self.__server_address, message)

    def aggregate(self, model):
        """Signs up for aggregation and wait for it to start"""
        with self.__state_lock:
            if self.__state != ClientState.NO_JOB:
                raise ValueError('The client is already taking part in aggregation')
            self.__state = ClientState.WAITING_SIGNUP_CONFIRMATION
            self.__resulting_model = None
            self.__send_to_server(Message(MessageType.AGGREGATION_SIGNUP))
        with self.__wait_aggregation:
            self.__wait_aggregation.wait()

        return self.__do_aggregation(self.__aggregation_group_list, model)

    def __handle_signup_confirmation(self, message):
        """Sets proper state on signup confirmation"""
        with self.__state_lock:
            if self.__state == ClientState.WAITING_SIGNUP_CONFIRMATION:
                if self.debug:
                    print('Received sign up confimation')
                self.__state = ClientState.WAITING_JOB
            elif self.debug:
                print('Received sign up confirmation, but not waiting for one')

    def __handle_group_assignment(self, message):
        """Prepare for aggregation and wake up aggregate function
        to start aggregation
        """
        with self.__state_lock:
            procceed_to_aggregation = False
            if self.__state == ClientState.WAITING_JOB:
                if self.debug:
                    print('Received assigned aggregation tree jobs')
                self.__num_nodes, group_list, self.__aggregation_profile = message
                self.__aggregation_group_list = sorted(
                    group_list, key=lambda group: group.level)
                self.__create_aggregation_model_queues(self.__aggregation_group_list)
                self.__state = ClientState.DOING_JOB
                procceed_to_aggregation = True
            elif self.debug:
                print('Received aggregation tree, but not waiting for one')

        # Needs polishing, so far we assume it will always procceed to aggregation
        if procceed_to_aggregation:
            with self.__wait_aggregation:
                self.__wait_aggregation.notifyAll()

    def __is_actor(self, group):
        """Helper function that returns whether this node is an actor in the
        given group
        """
        return self.address in group.aggregation_actors

    def __is_participant(self, group):
        """Helper function that returns whether this node is a participant in
        the given group
        """
        return self.address in group.participating_nodes

    def __send_model_to_actors(self, group, model):
        """Splits model in shares and send them to corresponding actors
        of the given group
        """
        model_shares = self.__aggregation_profile.create_shares_on_prepared_data(
            model, len(group.aggregation_actors))
        group_id = group.id
        for actor_node, model_share in zip(group.aggregation_actors, model_shares):
            if actor_node != self.address:
                self.send(actor_node, Message(MessageType.PARTIAL_MODEL_SHARE, PartialModelMessage(
                    group_id, model_share
                )))
            else:
                self.__aggregation_model_queues[group_id].add(self.address, model_share)

    def __organize_groups_by_level_jobs(self, group_list):
        """Organize group list for easy access with elements on each index
        corresponding to aggregation levels ascedingly. 0th element correspond to
        level 0 of aggregation tree, 1st element to level 1 and so on. Each
        element is a 2 element array where first element is the group the node
        participates in at the given level, while the other is the group
        that the node is actor in. If node is not an actor on the given
        level second element is None.
        """
        level_jobs = []
        current_level = 0
        current_group_index = 0
        while current_group_index < len(group_list):
            actor_group = None
            participant_group = None
            while current_group_index < len(group_list) and \
                    group_list[current_group_index].level <= current_level:
                group = group_list[current_group_index]
                if self.__is_actor(group):
                    if actor_group is not None:
                        raise ValueError('Cannot be actor in two gorups at the same level')
                    actor_group = group
                if self.__is_participant(group):
                    if participant_group is not None:
                        raise ValueError('Cannot be participant in two groups at the same level')
                    participant_group = group
                current_group_index += 1
            level_jobs.append([participant_group, actor_group])
            current_level += 1
        return level_jobs

    def __aggregate_shares_received_for_group(self, group_id):
        """Collects partial shares received for the given group and
        aggregates them into a single model
        """
        aggregation_model_queue = self.__aggregation_model_queues[group_id]
        received_partial_shares = []
        try:
            while True:
                received_partial_shares.append(aggregation_model_queue.get())
        except Empty:
            pass
        model = self.__aggregation_profile.aggregate(received_partial_shares)
        return model

    def __do_aggregation(self, group_list, model):
        """Perform secure aggregation with other nodes signed up for it
        over network
        """
        groups_to_update = []
        current_model = self.__aggregation_profile.prepare(model)
        last_actor_group = None

        level_jobs = self.__organize_groups_by_level_jobs(group_list)
        for participant_group, actor_group in level_jobs:
            print(actor_group)

            assert participant_group is not None, 'Node must be participant at each level it is on'
            self.__send_model_to_actors(participant_group, current_model)

            if actor_group is not None:
                groups_to_update.insert(0, actor_group)
                last_actor_group = actor_group
                current_model = self.__aggregate_shares_received_for_group(actor_group.id)


        if last_actor_group is not None and last_actor_group.is_root_level:
            with self.__resulting_model_lock:
                final_partial_shares = []
                root_group = last_actor_group
                group_id = root_group.id

                for actor in root_group.aggregation_actors:
                    if actor != self.address:
                        self.send(actor, Message(MessageType.FINAL_PARTIAL_SHARES, PartialModelMessage(
                            group_id, current_model
                        )))
                    else:
                        self.__aggregation_model_queues['final'].add(self.address, current_model)


                final_model_sum = self.__aggregate_shares_received_for_group(
                    'final'
                )

                self.__resulting_model = {
                    k: arr // self.__num_nodes \
                    for k, arr in final_model_sum.items()
                }
        else:
            with self.__wait_model:
                self.__wait_model.wait()


        for group in groups_to_update:
            for participant in group.participating_nodes:
                if participant != self.address:
                    self.send(participant, Message(
                        MessageType.MODEL_UPDATE, self.__resulting_model))

        self.__resulting_model = self.__aggregation_profile.unprepare(
            self.__resulting_model
        )
        try:
            return self.__resulting_model
        finally:
            self.__num_nodes = None
            self.__resulting_model = None
            with self.__state_lock:
                self.__state = ClientState.NO_JOB

    def __create_aggregation_model_queues(self, group_list):
        """Prepares model queues for models to go into them when received"""
        with self.__aggregation_model_queues_lock:
            actor_groups = list(filter(self.__is_actor, group_list))
            self.__aggregation_model_queues = {
                group.id: AggregationModelQueue(group.participating_nodes)\
                for group in actor_groups
            }
            root_groups = list(
                filter(lambda group: group.is_root_level, actor_groups))
            if root_groups:
                self.__aggregation_model_queues['final'] = \
                    AggregationModelQueue(root_groups[0].aggregation_actors)

    def __handle_partial_model(self, address, partial_model):
        """Puts partial share it receives into corresponding aggregation
        model queue
        """
        # print(f'Received model {partial_model.model} for group {partial_model.group_id} from {address}')
        assert partial_model.group_id != 'final', 'Invalid way to send final partial share'
        self.__aggregation_model_queues[partial_model.group_id].add(
            address,
            partial_model.model)

    def __handle_final_shares(self, address, partial_model):
        """Puts submodel of final group it receives into corresponding
        aggregation model queue
        """
        # print(f'Received final share {partial_model.model} from {address}')
        self.__aggregation_model_queues['final'].add(
            address,
            partial_model.model)

    def __handle_model_update(self, address, model):
        """Updates model and wakes up threads waiting for it"""
        with self.__resulting_model_lock:
            if self.__resulting_model is None:
                self.__resulting_model = model
                with self.__wait_model:
                    self.__wait_model.notifyAll()
