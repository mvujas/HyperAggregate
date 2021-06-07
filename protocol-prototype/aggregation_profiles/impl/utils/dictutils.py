def map_dict(map_function, dictionary):
    """
    Maps a dictionary to another by preserving keys and applying the given map
        function to values keys point to

    :param map_function: Function from V to A where V are values of dictionary
        and A is any type
    :type map_function: V => A

    :param dictionary: Dictionary of keys of type K pointing to values of type V
    :type dictionary: dict(K, V)

    :return: Dictionary with keys same as the input dictionary, while each
        value is obtained by applying the given function to the value under
        particular key
    :rtype: dict(K, A)
    """
    return {
        k: map_function(v) \
        for k, v in dictionary.items()
    }
