import numpy as np


def convert_to_int_array(arr, decimals_included):
    """
    Converts a numpy array of type float into an array of type int while
        preserving information about decimals_included decimals. It is not
        recommended to use array in this form for mathematical operations.

    :param arr: Array to be converted
    :type arr: np.array[float]

    :param decimals_included: Number of decimals to be preserved
    :type decimals_included: int

    :rtype: np.array[int]
    """
    base = 10 ** decimals_included
    return (arr * base).astype(np.int64)

def convert_to_float_array(arr, decimals_included):
    """
    The inverse function of convert_to_int_array function.
        Converts a numpy array of type int into an array of type float under
        assumption that last decimals_included digits of each int number are
        their decimal digits in float representation.

    :param arr: Array to be converted
    :type arr: np.array[int]

    :param decimals_included: Number of decimals included in int representation
        of array
    :type decimals_included: int

    :rtype: np.array[float]
    """
    base = 10 ** decimals_included
    return (arr / base).astype(np.float32)
