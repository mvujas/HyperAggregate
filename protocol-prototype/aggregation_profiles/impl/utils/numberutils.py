import numpy as np

# doesn't work properly for high decimals included (something like 8 or 9),
# because before dividing an array numpy first converts it to float/double which
# have they own inprecision which comes into play in this case
#
# Code sample:
# a = np.array([
#     [0.512321312, 1.123213213],
#     [16.123123, 18.3]
# ])
#
# x = convert_to_int_array(a, 12)
# print('As int: ', x)
#
# print('Back to float: ', convert_to_float_array(x, 12))

def convert_to_int_array(arr, decimals_included):
    """Converts a numpy array of type float into an array of type int while
        preserving information about decimals_included decimals. It is not
        recommended to use array in this form for mathematical operations.

    Parameters
    ----------
    arr: np.array[float]
        Array to be converted
    decimals_included: int
        Number of decimals to be preserved
    """
    base = 10 ** decimals_included
    return (arr * base).astype(np.int64)

def convert_to_float_array(arr, decimals_included):
    """The inverse function of convert_to_int_array function.
        Converts a numpy array of type int into an array of type float under
        assumption that last decimals_included digits of each int number are
        their decimal digits in float representation.

    Parameters
    ----------
    arr: np.array[int]
        Array to be converted
    decimals_included: int
        Number of decimals included in int representation of array
    """
    base = 10 ** decimals_included
    return arr / base
