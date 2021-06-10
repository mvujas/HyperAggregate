from ...aggregation_profiles.abstract_aggregation_profile import \
    AbstractAggregationProfile

from .utils.secret_sharing import create_additive_shares, create_int_additive_shares
from .utils.numberutils import convert_to_int_array, convert_to_float_array
from .utils.torchutils import convert_state_dict_to_numpy, \
    convert_numpy_state_dict_to_torch
from .utils.dictutils import map_dict

class AverageAdditiveSharingModelProfile(AbstractAggregationProfile):
    """Defines logic for averaging 'numpy state dictionaries'"""
    def __init__(self, digits_to_keep):
        self.__digits_to_keep = digits_to_keep

    def prepare(self, state_dict):
        """Creates a tuple where first element is int array model and the
        other is int representing number of clients contributed to this model
        """
        return (
            map_dict(
                lambda layer: convert_to_int_array(layer, self.__digits_to_keep),
                state_dict
            ),
            1
        )

    def create_shares_on_prepared_data(self, data, num_shares):
        """Splits model and client count into given number of shares"""
        state_dict, client_count = data
        share_state_dictionaries = [{} for _ in range(num_shares)]
        for layer_name, layer_data in state_dict.items():
            shares = create_additive_shares(layer_data, num_shares)
            for i, share_i in enumerate(shares):
                share_state_dictionaries[i][layer_name] = share_i
        client_count_shares = create_int_additive_shares(client_count, num_shares)
        return zip(share_state_dictionaries, client_count_shares)

    def aggregate(self, prepared_shares):
        """Sums model partial shares and client counts"""
        prepared_model_shares = [
            x[0]\
            for x in prepared_shares
        ]
        assert len(prepared_model_shares) != 0, 'No additive shares'
        result = {}
        layer_names = prepared_model_shares[0].keys()
        for layer_name in layer_names:
            result[layer_name] = sum(
                share[layer_name]\
                for share in prepared_model_shares
            )
        client_count_sum = sum([x[1] for x in prepared_shares])
        return (result, client_count_sum)

    def unprepare(self, prepared_data):
        """Converts model's int arrays to float arrays and divides them by the
        client count
        """
        return map_dict(
            lambda arr: convert_to_float_array(arr, self.__digits_to_keep) / prepared_data[1],
            prepared_data[0]
        )
