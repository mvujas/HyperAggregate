import random
from ...shared.aggregation_tree import AggregationGroup, AggregationTree

def partition_sizes(set_size, subset_size, min_subset_size = 3):
    """Returns the size of each part for the set of size set_size

    :param set_size: Size of the set
    :type set_size: int

    :param subset_size: Preferable size of a part
    :type subset_size: int

    :param min_subset_size: Minimum size of a part
    :type min_subset_size: int

    :return: Size of each part
    :rtype: list[int]
    """
    # print(subset_size, min_subset_size)
    assert subset_size >= min_subset_size, 'Set size must be bigger than minimum subset size'
    result = [subset_size] * (set_size // subset_size)
    last_subset_size = set_size % subset_size
    if last_subset_size < min_subset_size:
        assert len(result) > 0, 'Can\'t generate partition with given parameters'
        result[-1] += last_subset_size
    else:
        result.append(last_subset_size)
    return result


def generate_aggregation_tree(participants, size, num_actors):
    """Generates aggregation tree for a set of participants and the given
    parameters

    :param participants: A set of indentifiers for the participants of
        aggregation
    :type participants: set[string]

    :param size: Size of aggregation groups in the tree
    :type size: int

    :param num_actors: Number of actors in each group of the tree
    :type num_actors: int

    :return: A tuple where the first element is the aggregation tree, while
        the other is a dictionary for each particiapnts of the
        groups it is in
    :rtype: tuple[AggregationTree, dict[string, list[AggregationGroup]]]
    """
    current_level_participants = participants
    aggregation_tree = AggregationTree()
    next_id = 0
    level = 0
    more_levels = True
    participation_group_dict = {
        node: []\
        for node in participants
    }
    while more_levels:
        random.shuffle(current_level_participants)
        actors_set = set(current_level_participants)
        next_level_participants = []

        min_index = 0
        partitions = partition_sizes(len(current_level_participants), size)
        # print('Partitions:', partitions)
        for group_size in partitions:
            # Choose participants and aggregation actors
            group_participants =    \
                current_level_participants[min_index:min_index + group_size]
            min_index += group_size
            # print(actors_set, len(actors_set), num_actors)
            group_actors = random.sample(actors_set, num_actors)
            actors_set.difference_update(group_actors)
            # Actors take part in next level aggregation
            next_level_participants.extend(group_actors)
            # Create group
            is_root = len(partitions) == 1
            aggregation_group = AggregationGroup(next_id, level, is_root)
            next_id += 1
            aggregation_group.aggregation_actors = group_actors
            aggregation_group.participating_nodes = group_participants
            aggregation_tree.groups.append(aggregation_group)
            # Add pointers for each node to find group easier
            for group_member in set(group_participants + group_actors):
                participation_group_dict[group_member].append(aggregation_group)
        # If there is only a single member in partition it means we are at root
        if len(partitions) == 1:
            more_levels = False
        level += 1
        current_level_participants = next_level_participants
    return aggregation_tree, participation_group_dict
