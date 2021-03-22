from utils.secret_sharing import *
from utils.numberutils import *
from network_model import Net
from collections import OrderedDict
import numpy as np
import torch

from utils.secret_sharing import create_additive_shares
from utils.numberutils import convert_to_int_array, convert_to_float_array
from utils.torchutils import convert_state_dict_to_numpy, \
    convert_numpy_state_dict_to_torch
from utils.dictutils import map_dict

# a = np.array([
#     [0.512321312, 1.123213213],
#     [16.123123, 18.3]
# ])
#
# decimals = 12
# x = convert_to_int_array(a, decimals)
# print('As int: ', x)
#
# print('Back to float: ', convert_to_float_array(x, decimals))

#
# model = Net()
# model_state = model.state_dict()
#
# print(type(model_state))
#
# def convert_state_dict_to_numpy(state_dict):
#     return {
#         layer_name: tensor.detach().numpy()\
#         for layer_name, tensor in state_dict.items()
#     }
#
# def convert_numpy_state_dict_to_torch(numpy_state_dict):
#     return {
#         layer_name: torch.from_numpy(arr)\
#         for layer_name, arr in numpy_state_dict.items()
#     }
#
# a = convert_state_dict_to_numpy(model_state)
# print(a)
# x = convert_numpy_state_dict_to_torch(a)
# print(x)
# in_image = torch.ones([1, 1, 28, 28])
#
# res1 = model.forward(in_image)
# model.load_state_dict(x)
# res2 = model.forward(in_image)
# print(res1)
# print(res2)

def aggregate_shares(shares):
    assert len(shares) != 0, 'No additive shares'
    result = {}
    layer_names = shares[0].keys()
    for layer_name in layer_names:
        result[layer_name] = sum(share[layer_name] for share in shares)
    return result

a = {
    'a': np.array([1, 2]),
    'b': np.array([0, 0, 3]),
    'c': np.array([[0, 1], [2, 2]])
}

b = {
    'a': np.array([10, 8]),
    'b': np.array([-1, 1, 4]),
    'c': np.array([[12, 3], [4, 4]])
}

c = {
    'a': np.array([0, 5]),
    'b': np.array([8, 0, 3-12]),
    'c': np.array([[0, -1], [8, 7]])
}

def prepare_state_dict_and_create_shares(state_dict, num_shares):
    numpy_state_dict = state_dict#convert_state_dict_to_numpy(state_dict)
    share_state_dictionaries = [{} for _ in range(num_shares)]
    for layer_name, layer_data in numpy_state_dict.items():
        shares = create_additive_shares(layer_data, num_shares)
        for i, share_i in enumerate(shares):
            # share_i_int = convert_to_int_array(share_i, DIGITS_TO_KEEP)
            share_state_dictionaries[i][layer_name] = share_i
    return share_state_dictionaries

print(aggregate_shares([a, b, c]))

print(prepare_state_dict_and_create_shares(a, 3))

print(aggregate_shares(prepare_state_dict_and_create_shares(a, 3)))
print(aggregate_shares(prepare_state_dict_and_create_shares(b, 3)))
print(aggregate_shares(prepare_state_dict_and_create_shares(c, 3)))
