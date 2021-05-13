import torch
from .dictutils import map_dict

def convert_state_dict_to_numpy(state_dict):
    """Converts each tensor of the state dictionary into the equivalent
        numpy array.

    Parameters
    ----------
    state_dict: collections.OrderedDict
        Dictionary of string -> torch.tensor pairs.
    """
    return map_dict(lambda tensor: tensor.detach().numpy(), state_dict)


def convert_numpy_state_dict_to_torch(numpy_state_dict):
    """The inverse function of convert_state_dict_to_numpy.
        Converts state dictionary from numpy form back to torch.tensor form.

    Parameters
    ----------
    numpy_state_dict : type
        Dictionary of string -> numpy.array pairs.
    """
    return map_dict(lambda arr: torch.from_numpy(arr), numpy_state_dict)
