import os,sys,inspect
current_dir = os.path.dirname(
    os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
from netutils.message import Message, MessageType
from shared.responsive_message_router import ResponsiveMessageRouter
from threading import Lock, Condition

from utils.aggregation_profile import AggregationProfile
from utils.partial_model_message import PartialModelMessage


from utils.secret_sharing import create_additive_shares
from utils.numberutils import convert_to_int_array, convert_to_float_array
from utils.torchutils import convert_state_dict_to_numpy, \
    convert_numpy_state_dict_to_torch
from utils.dictutils import map_dict

import random

from enum import Enum

from queue import Empty


DIGITS_TO_KEEP = 6


class ClientState(Enum):
    NO_JOB, \
    WAITING_SIGNUP_CONFIRMATION, \
    WAITING_JOB, \
    DOING_JOB = range(4)


def prepare_state_dict(state_dict):
    numpy_state_dict = convert_state_dict_to_numpy(state_dict)

def prepare_state_dict_and_create_shares(state_dict, num_shares):
    numpy_state_dict = convert_state_dict_to_numpy(state_dict)
    share_state_dictionaries = [{} for _ in range(num_shares)]
    for layer_name, layer_data in numpy_state_dict.items():
        shares = create_additive_shares(layer_data, num_shares)
        for i, share_i in enumerate(shares):
            share_i_int = convert_to_int_array(share_i, DIGITS_TO_KEEP)
            share_state_dictionaries[i][layer_name] = share_i_int
    return share_state_dictionaries


def aggregate_shares(shares):
    assert len(shares) != 0, 'No additive shares'
    result = {}
    layer_names = shares[0].keys()
    for layer_name in layer_names:
        result[layer_name] = sum(share[layer_name] for share in shares)
    return result


def get_state_dict_from_prepared_form(prepared_form):
    return convert_numpy_state_dict_to_torch(
        map_dict(
            lambda arr: convert_to_float_array(arr, DIGITS_TO_KEEP),
            prepared_form
        )
    )


class PrivacyPreservingAggregator(ResponsiveMessageRouter):
    def __init__(self, address, server_address, debug_mode=False):
        super().__init__(address, debug_mode=debug_mode)
        self.__server_address = server_address
        self.__state = ClientState.NO_JOB
        self.__state_lock = Lock()
        self.__aggregation_profiles = None
        self.__resulting_model = None
        self.__resulting_model_lock = Lock()
        self.__aggregation_profiles_lock = Lock()
        self.__wait_aggregation = Condition()
        self.__wait_model = Condition()
        self.__aggregation_group_list = None
        self.__num_nodes = None

    def register_callbacks(self):
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
        self.send(self.__server_address, message)

    def aggregate(self, model):
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
        with self.__state_lock:
            if self.__state == ClientState.WAITING_SIGNUP_CONFIRMATION:
                if self.debug:
                    print('Received sign up confimation')
                self.__state = ClientState.WAITING_JOB
            elif self.debug:
                print('Received sign up confirmation, but not waiting for one')

    def __handle_group_assignment(self, message):
        with self.__state_lock:
            procceed_to_aggregation = False
            if self.__state == ClientState.WAITING_JOB:
                if self.debug:
                    print('Received assigned aggregation tree jobs')
                self.__num_nodes, group_list = message
                self.__aggregation_group_list = sorted(
                    group_list, key=lambda group: group.level)
                self.__create_aggregation_profiles(self.__aggregation_group_list)
                self.__state = ClientState.DOING_JOB
                procceed_to_aggregation = True
            elif self.debug:
                print('Received aggregation tree, but not waiting for one')

        # Needs polishing, so far we assume it will always procceed to aggregation
        if procceed_to_aggregation:
            with self.__wait_aggregation:
                self.__wait_aggregation.notifyAll()

    def __is_actor(self, group):
        return self.address in group.aggregation_actors

    def __is_participant(self, group):
        return self.address in group.participating_nodes

    def __do_aggregation(self, group_list, model):
        groups_to_update = []
        current_level = 0
        current_group_index = 0
        current_model = model
        last_actor_group = None
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

            print(actor_group)

            assert participant_group is not None, 'Node must be participant at each level it is on'
            model_shares = prepare_state_dict_and_create_shares(current_model, len(participant_group.aggregation_actors))
            group_id = participant_group.id
            for actor_node, model_share in zip(participant_group.aggregation_actors, model_shares):
                if actor_node != self.address:
                    self.send(actor_node, Message(MessageType.PARTIAL_MODEL_SHARE, PartialModelMessage(
                        group_id, model_share
                    )))
                else:
                    self.__aggregation_profiles[group_id].add(self.address, model_share)


            if actor_group is not None:
                groups_to_update.insert(0, actor_group)
                last_actor_group = actor_group
                group_id = actor_group.id
                aggregation_profile = self.__aggregation_profiles[group_id]
                received_partial_shares = []
                try:
                    while True:
                        received_partial_shares.append(aggregation_profile.get())
                except Empty:
                    pass
                current_model = get_state_dict_from_prepared_form(aggregate_shares(received_partial_shares))
                # print(f'Have all models for {actor_group.id}, result {current_model} with {len(received_partial_shares)} models')
            current_level += 1

        if last_actor_group is not None and last_actor_group.is_root_level:
            with self.__resulting_model_lock:
                final_partial_shares = []
                root_group = last_actor_group
                group_id = root_group.id
                current_model = prepare_state_dict_and_create_shares(current_model, 1)[0]
                # print(current_model)
                for actor in root_group.aggregation_actors:
                    if actor != self.address:
                        self.send(actor, Message(MessageType.FINAL_PARTIAL_SHARES, PartialModelMessage(
                            group_id, current_model
                        )))
                    else:
                        self.__aggregation_profiles['final'].add(self.address, current_model)

                aggregation_profile = self.__aggregation_profiles['final']
                try:
                    while True:
                        final_partial_shares.append(aggregation_profile.get())
                except Empty:
                    pass
                # print(final_partial_shares)
                self.__resulting_model = aggregate_shares(final_partial_shares)

                self.__resulting_model = map_dict(
                    lambda arr: arr // self.__num_nodes,
                    self.__resulting_model
                )
                # print(f'Model {self.__resulting_model}')
        else:
            with self.__wait_model:
                self.__wait_model.wait()


        for group in groups_to_update:
            for participant in group.participating_nodes:
                if participant != self.address:
                    self.send(participant, Message(
                        MessageType.MODEL_UPDATE, self.__resulting_model))

        self.__resulting_model = get_state_dict_from_prepared_form(self.__resulting_model)
        try:
            return self.__resulting_model
        finally:
            self.__num_nodes = None
            self.__resulting_model = None
            with self.__state_lock:
                self.__state = ClientState.NO_JOB

    def __create_aggregation_profiles(self, group_list):
        with self.__aggregation_profiles_lock:
            actor_groups = list(filter(self.__is_actor, group_list))
            self.__aggregation_profiles = {
                group.id: AggregationProfile(group.participating_nodes)\
                for group in actor_groups
            }
            root_group = list(filter(lambda group: group.is_root_level, actor_groups))
            if root_group:
                self.__aggregation_profiles['final'] = AggregationProfile(root_group[0].aggregation_actors)
            # print(self.__aggregation_profiles)

    def __handle_partial_model(self, address, partial_model):
        # print(f'Received model {partial_model.model} for group {partial_model.group_id} from {address}')
        assert partial_model.group_id != 'final', 'Invalid way to send final partial share'
        self.__aggregation_profiles[partial_model.group_id].add(address, partial_model.model)

    def __handle_final_shares(self, address, partial_model):
        # print(f'Received final share {partial_model.model} from {address}')
        self.__aggregation_profiles['final'].add(address, partial_model.model)

    def __handle_model_update(self, address, model):
        with self.__resulting_model_lock:
            if self.__resulting_model is None:
                self.__resulting_model = model
                with self.__wait_model:
                    self.__wait_model.notifyAll()
