import torch
from .dictutils import map_dict

def convert_state_dict_to_numpy(state_dict):
    """
    Converts each tensor of the state dictionary into the equivalent
        numpy array.


    :param state_dict: collections.OrderedDict
    :type state_dict: dict(str, torch.tensor)

    :rtype: dict(string, numpy.array)
    """
    return map_dict(lambda tensor: tensor.detach().numpy(), state_dict)


def convert_numpy_state_dict_to_torch(numpy_state_dict):
    """
    The inverse function of convert_state_dict_to_numpy.
        Converts state dictionary from numpy form back to torch.tensor form.


    :param numpy_state_dict: Analogue of PyTorch state_dict but instead of
        using tensors uses numpy arrays
    :type numpy_state_dict: dict(string, numpy.array)

    :rtype: dict(str, torch.tensor)
    """
    return map_dict(lambda arr: torch.from_numpy(arr), numpy_state_dict)
