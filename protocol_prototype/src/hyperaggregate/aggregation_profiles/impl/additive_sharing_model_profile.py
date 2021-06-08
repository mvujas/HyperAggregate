from ...aggregation_profiles.abstract_aggregation_profile import \
    AbstractAggregationProfile

from .utils.secret_sharing import create_additive_shares
from .utils.numberutils import convert_to_int_array, convert_to_float_array
from .utils.torchutils import convert_state_dict_to_numpy, \
    convert_numpy_state_dict_to_torch
from .utils.dictutils import map_dict

class AdditiveSharingModelProfile(AbstractAggregationProfile):
    def __init__(self, digits_to_keep):
        self.__digits_to_keep = digits_to_keep

    def prepare(self, state_dict):
        """Transforms PyTorch state dictionary into dictionary of int numpy
        arrays
        """
        numpy_state_dict = convert_state_dict_to_numpy(state_dict)
        return map_dict(
            lambda layer: convert_to_int_array(layer, self.__digits_to_keep),
            numpy_state_dict
        )

    def create_shares_on_prepared_data(self, state_dict, num_shares):
        share_state_dictionaries = [{} for _ in range(num_shares)]
        for layer_name, layer_data in state_dict.items():
            shares = create_additive_shares(layer_data, num_shares)
            for i, share_i in enumerate(shares):
                share_state_dictionaries[i][layer_name] = share_i
        return share_state_dictionaries

    def aggregate(self, prepared_shares):
        assert len(prepared_shares) != 0, 'No additive shares'
        result = {}
        layer_names = prepared_shares[0].keys()
        for layer_name in layer_names:
            result[layer_name] = sum(
                share[layer_name]\
                for share in prepared_shares
            )
        return result

    def unprepare(self, prepared_data):
        return convert_numpy_state_dict_to_torch(
            map_dict(
                lambda arr: convert_to_float_array(arr, self.__digits_to_keep),
                prepared_data
            )
        )
