from functools import reduce
import torch

TORCH_STR_TO_DTYPE = {
    'float32': torch.float32,
    'float64': torch.float64,
    'int32': torch.int32
}

TORCH_DTYPE_TO_STR = {
    v: k\
    for k, v in TORCH_STR_TO_DTYPE.items()
}


def product(list):
    """Returns the product of the elements of the given list"""
    return reduce(lambda acc, x: acc * x, list)


def deserialize_model(model_message):
    """Converts model from the format defined for intercommunication into
    PyTorch's state dictionary
    """
    state_dict = {}
    for variable in model_message:
        # Find values
        layer_name = variable['$variable']['name']
        layer_data = variable['$variable']['val']['$tensor']
        dtype = layer_data['dtype']
        shape = layer_data['shape']
        arr = layer_data['data']
        shape_flat = product(shape)
        # Create flat tensor from data
        flat_tensor = torch.tensor([
            arr[str(i)] for i in range(shape_flat)],
            dtype=TORCH_STR_TO_DTYPE[dtype])
        # Reshape tensor and add into state dictionary
        tensor = flat_tensor.reshape(shape)
        state_dict[layer_name] = tensor
    return state_dict


def serialize_tensor(tensor):
    """Converts tensor into the intercommunication format"""
    return {
        '$tensor': {
            'data': torch.flatten(tensor).tolist(),
            'shape': tensor.shape,
            'dtype': TORCH_DTYPE_TO_STR[tensor.dtype]
        }
    }

def serialize_model(state_dict):
    """Converts state dictionary into the intercommunication format"""
    return [
        {
            '$variable': {
                'name': layer_name,
                'val': serialize_tensor(tensor)
            }
        }\
        for layer_name, tensor in state_dict.items()
    ]
