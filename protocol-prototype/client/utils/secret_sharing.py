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
    max_val = max(abs(arr.min()), abs(arr.max()))
    interval_bound = (1 + np.random.rand()) * (max_val + np.random.rand())
    # generate all shares but last
    shares = [rand_interval(-interval_bound, interval_bound, arr.shape)
        for _ in range(num_shares - 1)]
    # calculate last share as sum of generated shares subtracted from the
    #   original array
    last_share = arr - np.sum(shares, axis=0)
    shares.append(last_share)
    return shares

def reconstruct_additive_secretsharing_result(shares):
    return np.sum(shares, axis=0)
