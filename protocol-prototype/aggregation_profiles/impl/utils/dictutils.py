def map_dict(map_function, dictionary):
    """Maps a dictionary to another by preserving keys and applying the
        given map function to values keys point to

    Parameters
    ----------
    map_function
        Function from V to A where V are values of dictionary and A is any type
    dictionary : dict
        Dictionary of keys of type K pointing to values of type V.
    """
    return {
        k: map_function(v) \
        for k, v in dictionary.items()
    }
