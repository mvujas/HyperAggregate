import numpy as np

def rand_interval(low, high, shape, sampler_function=np.random.rand):
    """ Initialize array of the given shape with random values in interval
        [low, high) sampled by sampler_function.

    Parameters
    ----------
    low: float
        Lower bound
    high: float
        Upper bound
    shape: list[int] or Tuple[int]
        Shape of the output
    sampler_function:
        A function that accepts shape and returns a sample of the given size
        with each value being in the range [0, 1)
    """
    return (high - low) * sampler_function(*shape) + low

def create_additive_shares(arr, num_shares):
    """Create additive shares out of the passed int64 array"""
    remaining_arr = arr
    # iinfo returns bounds for the given type
    # TODO: Create config files and put int format there and retrieve it
    #   when needed
    ii64 = np.iinfo(np.int64)
    shares = []
    for i in range(num_shares):
        if i == num_shares - 1:
            share = remaining_arr
        else:
            share = np.random.randint(
                ii64.min,
                ii64.max,
                size=arr.shape,
                dtype=np.int64)
        remaining_arr = remaining_arr - share
        shares.append(share)
    return shares

def reconstruct_additive_secretsharing_result(shares):
    return np.sum(shares, axis=0)
