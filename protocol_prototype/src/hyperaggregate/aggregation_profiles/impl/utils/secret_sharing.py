import numpy as np

def create_int_additive_shares(number_to_split, num_shares):
    """Splits given number in specified number of additive shares

    :param number_to_split: Number to split
    :type number_to_split: np.int64

    :param num_shares: Number of shares that number_to_split should be split
        into
    :type num_shares: int

    :return: List of additive shares
    :rtype: list[np.int64]
    """
    ii64 = np.iinfo(np.int64)
    shares = []
    for i in range(num_shares):
        if i == num_shares - 1:
            share = number_to_split
        else:
            share = np.random.randint(ii64.min, ii64.max)
            number_to_split -= share
        shares.append(share)
    return shares

def rand_interval(low, high, shape, sampler_function=np.random.rand):
    """(Deprecated) Initializes array of the given shape with random values in
        interval [low, high) sampled by sampler_function

    :param low: Lower bound
    :type low: float

    :param high: Upper bound
    :type high: float

    :param shape: Shape of the output
    :type shape: list[int] or Tuple[int]

    :param sampler_function: A function that accepts shape and returns a sample
        of the given size with each value being in the range [0, 1)
    :type sampler_function: (*int) => np.array

    :return: Array of specified shape
    :rtype: np.array
    """
    return (high - low) * sampler_function(*shape) + low

def create_additive_shares(arr, num_shares):
    """Create additive int64 shares out of the passed int64 array

    :param arr: Arrray to create shares out of
    :type arr: np.array[np.int64]

    :param num_shares: Number of shares to create
    :type num_shares: int

    :return: List of shares
    :rtype: list[np.array[np.int64]]
    """
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
    """Returns sum of given additive shares

    :param shares: Shares
    :type shares: list[np.array]

    :return: Sum of shares over axis 0
    :rtype: np.array
    """
    return np.sum(shares, axis=0)
