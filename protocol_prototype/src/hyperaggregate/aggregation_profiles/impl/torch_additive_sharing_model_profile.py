from ...aggregation_profiles.abstract_aggregation_profile import \
    AbstractAggregationProfile

from .additive_sharing_model_profile import AverageAdditiveSharingModelProfile

from .utils.secret_sharing import create_additive_shares
from .utils.numberutils import convert_to_int_array, convert_to_float_array
from .utils.torchutils import convert_state_dict_to_numpy, \
    convert_numpy_state_dict_to_torch
from .utils.dictutils import map_dict

class AverageTorchAdditiveSharingModelProfile(AverageAdditiveSharingModelProfile):
    """Defines logic for averaging PyTorch state dictionaries"""
    def __init__(self, digits_to_keep):
        super().__init__(digits_to_keep)

    def prepare(self, state_dict):
        """Transforms PyTorch state dictionary into dictionary of int numpy
        arrays and calls the parent method to create tuple of numpy array and
        client count
        """
        numpy_state_dict = convert_state_dict_to_numpy(state_dict)
        return super().prepare(numpy_state_dict)

    def unprepare(self, prepared_data):
        """Converts model's int arrays to float arrays and divides then by the
        client count, afterwards converts numpy state dictionary to PyTorch
        state dictionary
        """
        return convert_numpy_state_dict_to_torch(
            super().unprepare(prepared_data)
        )
