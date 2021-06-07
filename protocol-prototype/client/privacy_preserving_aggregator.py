from netutils.message import Message, MessageType
from shared.responsive_message_router import ResponsiveMessageRouter
from threading import Lock, Condition

from .utils.aggregation_model_queue import AggregationModelQueue
from .utils.partial_model_message import PartialModelMessage

import random
import gc

import timeit

from enum import Enum

from queue import Empty


class ClientState(Enum):
    """Possible states client can be in"""
    NO_JOB, \
    WAITING_SIGNUP_CONFIRMATION, \
    WAITING_JOB, \
    DOING_JOB = range(4)


class PrivacyPreservingAggregator(ResponsiveMessageRouter):
    """A class representing aggregation client logic"""
    def __init__(self, address, server_address, debug_mode=False):
        super().__init__(address, debug_mode=debug_mode)
        self.__server_address = server_address
        self.__state = ClientState.NO_JOB
        self.__state_lock = Lock()
        self.__aggregation_model_queues = None
        self.__resulting_model = None
        self.__previous_aggregation_ids = set()
        self.__resulting_model_lock = Lock()
        self.__aggregation_model_queues_lock = Lock()
        self.__wait_aggregation = Condition()
        self.__wait_model = Condition()
        self.__aggregation_group_list = None
        self.__num_nodes = None
        self.__aggregation_profile = None
        self.__time_elapsed = None

        self.__active_aggregation_id = None
        # Actors that should send ME model
        self.__actors_to_send_list = None
        # Participants I am responsible for to send model
        self.__participants_to_receive_list = None
        # Participants that I am responsible for, but notified ME that they
        #   received the model
        self.__participants_that_dont_need_model_lock = Lock()
        self.__participants_that_dont_need_model = None

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
            MessageType.MODEL_UPDATE: self.__handle_model_update,
            MessageType.NO_MODEL_NEEDED: self.__handle_no_model_needed
        })
        return result

    @property
    def time_elapsed(self):
        """Getter that returns the amount of time the last aggregation has taken

        :return: A number of seconds that the last aggregation has taken between
            being assigned aggregation and finishing the aggregation. If no
            aggregation has taken place yet, None will be returned
        :rtype: float or None
        """
        return self.__time_elapsed

    def __send_to_server(self, message):
        """Helper function to simplify code that sends a message to the server

        :param message: A message to be sent to the server
        :type message: object
        """
        self.send(self.__server_address, message)

    def aggregate(self, model):
        """Signs up for aggregation and wait for it to start

        :param model: Model to aggregate
        :type model: object

        :return: Aggregated model
        :rtype: object
        """
        with self.__state_lock:
            with self.__resulting_model_lock:
                if self.__state != ClientState.NO_JOB:
                    raise ValueError('The client is already taking part in aggregation')
                self.__state = ClientState.WAITING_SIGNUP_CONFIRMATION
                self.__active_aggregation_id = None
                print(f'\t[{self.address}]: Active aggregation id set to {self.__active_aggregation_id}')
                self.__resulting_model = None
                self.__participants_that_dont_need_model = set()
                self.__actors_to_send_list = []
                self.__participants_to_receive_list = []
                self.__send_to_server(Message(MessageType.AGGREGATION_SIGNUP))
        with self.__wait_aggregation:
            self.__wait_aggregation.wait()

        start_time = timeit.default_timer()
        aggregated_model = self.__do_aggregation(self.__aggregation_group_list, model)
        end_time = timeit.default_timer()
        self.__time_elapsed = end_time - start_time
        return aggregated_model

    def __handle_signup_confirmation(self, payload):
        """Sets proper state on signup confirmation

        :param payload: Payload (curently not in use as signup confirmation
            doesn't have any additional data. However, this might not be the
            case in the future)
        :type payload: object or None
        """
        with self.__state_lock:
            if self.__state == ClientState.WAITING_SIGNUP_CONFIRMATION:
                if self.debug:
                    print('Received sign up confimation')
                self.__state = ClientState.WAITING_JOB
            elif self.debug:
                print('Received sign up confirmation, but not waiting for one')

    def __handle_group_assignment(self, payload):
        """Prepare for aggregation and wake up aggregate function
        to start aggregation

        :param payload: Payload of the message (expected to contain aggregation
            identifier, number of nodes in aggregation, list of groups the
            node participates in and the aggregation profile for aggregation)
        :type payload: tuple[int, int,
            list[shared.aggregation_tree.AggregationGroup],
            aggregation_profiles.abstract_aggregation_profile.AbstractAggregationProfile]
        """
        with self.__state_lock:
            procceed_to_aggregation = False
            if self.__state == ClientState.WAITING_JOB:
                if self.debug:
                    print('Received assigned aggregation tree jobs')
                self.__active_aggregation_id, self.__num_nodes, \
                    group_list, self.__aggregation_profile = payload

                print(f'\t[{self.address}]: Active aggregation id set to {self.__active_aggregation_id}')
                self.__aggregation_group_list = sorted(
                    group_list, key=lambda group: group.level)
                self.__create_aggregation_model_queues(
                    self.__aggregation_group_list)
                self.__state = ClientState.DOING_JOB
                procceed_to_aggregation = True
            elif self.debug:
                print('Received aggregation tree, but not waiting for one')

        # Needs polishing, so far we assume it will always procceed to aggregation
        if procceed_to_aggregation:
            with self.__wait_aggregation:
                self.__wait_aggregation.notifyAll()

    def __is_actor(self, group):
        """Checks whether this node is an actor in the given group

        :param group: An aggregation group
        :type group: shared.aggregation_tree.AggregationGroup

        :return: True is this node is an aggregation actor in the given group
        :rtype: bool
        """
        return self.address in group.aggregation_actors

    def __is_participant(self, group):
        """Checks whether this node is a participant in the given group

        :param group: An aggregation group
        :type group: shared.aggregation_tree.AggregationGroup

        :return: True is this node is an aggregation participant in the given group
        :rtype: bool
        """
        return self.address in group.participating_nodes

    def __send_model_to_actors(self, group, model):
        """Splits model in shares and send them to corresponding actors
        of the given group

        :param group: Group to whose aggregation actors the shares of the model
            should be sent to
        :type group: shared.aggregation_tree.AggregationGroup

        :param model: A model to be split into shares
        :type model: object
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
            del model_share
        del model_shares
        # In future ideally program would be forced to free memory of the share

    def __organize_groups_by_level_jobs(self, group_list):
        """Organize group list for easy access with elements on each index
        corresponding to aggregation levels ascedingly. 0th element correspond to
        level 0 of aggregation tree, 1st element to level 1 and so on. Each
        element is a 2 element tuple where first element is the group the node
        participates in at the given level, while the other is the group
        that the node is actor in. If node is not an actor on the given
        level second element is None.

        :param group_list: A list of groups that the nodes is in either as an
            aggregation actor or participant
        :type group_list: list[shared.aggregation_tree.AggregationGroup]

        :raises ValueError: Node is either participant of 2 groups at the same
            level or aggregation actor of 2 groups at the same level

        :rtype: list[tuple[
            shared.aggregation_tree.AggregationGroup or None,
            shared.aggregation_tree.AggregationGroup or None]]
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
                        raise ValueError(
                            'Cannot be actor in two grups at the same level')
                    actor_group = group
                if self.__is_participant(group):
                    if participant_group is not None:
                        raise ValueError(
                            'Cannot be participant in two groups at the same level')
                    participant_group = group
                current_group_index += 1
            level_jobs.append([participant_group, actor_group])
            current_level += 1
        return level_jobs

    def __aggregate_shares_received_for_group(self, group_id):
        """Collects partial shares received for the given group and
        aggregates them into a single model

        :param group_id: Identifier of the group that aggregation should be
            done for
        :type group_id: int

        :return: Aggregation of partial model shares for the given group
        :rtype: object
        """
        aggregation_model_queue = self.__aggregation_model_queues[group_id]
        received_partial_shares = []
        try:
            while True:
                share = aggregation_model_queue.get()
                received_partial_shares.append(share)
                del share
        except Empty:
            pass
        model = self.__aggregation_profile.aggregate(received_partial_shares)
        return model

    def __do_aggregation(self, group_list, model):
        """Perform secure aggregation with other nodes signed up for it
        over network

        :param group_list: A list of groups that the nodes is in either as an
            aggregation actor or participant
        :type group_list: list[shared.aggregation_tree.AggregationGroup]

        :param model: A model to be aggregated with other models in the
            aggregation
        :type model: object

        :return: The aggregated model
        :rtype: object
        """
        try:
            assert self.__resulting_model is None, 'Model set before training'
            assert self.__active_aggregation_id is not None, 'Active aggregation id is None'
            groups_to_update = []
            current_model = self.__aggregation_profile.prepare(model)
            last_actor_group = None

            level_jobs = self.__organize_groups_by_level_jobs(group_list)
            for participant_group, actor_group in level_jobs:
                # print(actor_group)

                # Actors on top of tree are likely to send ME the model first,
                #   so I should notify them as soon as possible
                self.__actors_to_send_list = participant_group.aggregation_actors +\
                    self.__actors_to_send_list

                assert participant_group is not None, 'Node must be participant at each level it is on'
                self.__send_model_to_actors(participant_group, current_model)

                if actor_group is not None:
                    self.__participants_to_receive_list += actor_group.participating_nodes
                    groups_to_update.insert(0, actor_group)
                    last_actor_group = actor_group
                    current_model = self.__aggregate_shares_received_for_group(actor_group.id)

                gc.collect()


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

                    averaged_model = {
                        k: arr // self.__num_nodes \
                        for k, arr in final_model_sum.items()
                    }

                    self.__set_model(averaged_model)


                    gc.collect()
            else:
                with self.__wait_model:
                    self.__wait_model.wait()


            for group in groups_to_update:
                # Order list so don't all actors start on same node in the group
                my_index = group.aggregation_actors.index(self.address)
                group_actors_num = len(group.aggregation_actors)
                participants = list(set(group.participating_nodes).difference(group.aggregation_actors))
                group_participants_num = len(participants)
                split_index = my_index * (group_participants_num // group_actors_num)
                ordered_participant_list = participants[split_index:] +\
                    participants[:split_index]

                # Send model to participants that haven't already received it
                for participant in ordered_participant_list:
                    if participant != self.address and \
                            participant not in self.__participants_that_dont_need_model:
                        # print(f'\t\t[{self.address}]: Model sent to {participant}')
                        self.send(participant, Message(
                            MessageType.MODEL_UPDATE, (self.__active_aggregation_id, self.__resulting_model)))
                    # else:
                    #     print(f'\t\t[{self.address}]: Trying to send model to {participant}, but they already got it or it\'s me')
            self.__resulting_model = self.__aggregation_profile.unprepare(
                self.__resulting_model
            )
            try:
                return self.__resulting_model
            finally:
                with self.__state_lock:
                    with self.__resulting_model_lock:
                        with self.__participants_that_dont_need_model_lock:
                            self.__previous_aggregation_ids.add(self.__active_aggregation_id)
                            self.__participants_that_dont_need_model = set()
                        self.__num_nodes = None
                        self.__resulting_model = None
                        self.__active_aggregation_id = None
                        print(f'\t[{self.address}]: Active aggregation id set to {self.__active_aggregation_id}')
                        self.__state = ClientState.NO_JOB
        except Exception as e:
            print(e)

    def __create_aggregation_model_queues(self, group_list):
        """Prepares model queues for models to go into them when received

        :param group_list: A list of groups that the nodes is in either as an
            aggregation actor or participant
        :type group_list: list[shared.aggregation_tree.AggregationGroup]
        """
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

        :param address: The address of the peer that sent the model
        :type address: str

        :param partial_model: An object containing a partial share of the model
            of the given peer and the identifier of the group that this share
            should take part in
        :type partial_model: utils.PartialModelMessage
        """
        # print(f'Received model {partial_model.model} for group {partial_model.group_id} from {address}')
        assert partial_model.group_id != 'final', 'Invalid way to send final partial share'
        self.__aggregation_model_queues[partial_model.group_id].add(
            address,
            partial_model.model)

    def __handle_final_shares(self, address, partial_model):
        """Puts submodel of final group it receives into corresponding
        aggregation model queue

        :param address: The address of the peer that sent the model
        :type address: str

        :param partial_model: A partial share of the modle of the given peer
            and the identifier of the group that this share should take part in
            (the identifier is ignored in this case and only the share is
            considered)
        :type partial_model: utils.PartialModelMessage
        """
        # print(f'Received final share {partial_model.model} from {address}')
        self.__aggregation_model_queues['final'].add(
            address,
            partial_model.model)

    def __handle_no_model_needed(self, address, payload):
        """Puts given address in list of addresses that doesn't need the
        aggregated model

        :param address: The address of a peer that doesn't need the aggregated
            model
        :type address: str

        :param payload: The identifier of the aggregation for which the model
            is not needed
        :type payload: int
        """
        aggregation_id = payload
        with self.__participants_that_dont_need_model_lock:
            if aggregation_id not in self.__previous_aggregation_ids:
                self.__participants_that_dont_need_model.add(address)

    def __set_model(self, model):
        """Updates model and wakes up threads waiting for it

        :type model: object
        """
        self.__resulting_model = model
        for actor in self.__actors_to_send_list:
            self.send(actor, Message(MessageType.NO_MODEL_NEEDED, self.__active_aggregation_id))
        with self.__wait_model:
            self.__wait_model.notifyAll()

    def __handle_model_update(self, address, message):
        """Handles receipt of model

        :param address: The address of a peer that sent the model
        :type address: str

        :param message: A tuple containing the id of the aggregation that
            produced the model and the model itself
        :type message: tuple[int, object]
        """
        model = message[1]
        active_id = message[0]
        print(f'\t[{self.address}]: Trying to acquire model lock')
        with self.__resulting_model_lock:
            if active_id == self.__active_aggregation_id and \
                    self.__resulting_model is None:
                self.__set_model(model)
            #     print(f'\t[{self.address}]: Got a model from {address} and accepted')
            # else:
            #     print(f'\t[{self.address}]: Got a model from {address} but rejected it, since I have one already', active_id == self.__active_aggregation_id, active_id, self.__active_aggregation_id, self.__resulting_model is None)
