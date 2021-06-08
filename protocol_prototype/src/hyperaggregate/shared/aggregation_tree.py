class AggregationGroup:
    """Class representing aggregation group

    :var id: The identifier of the group (Assumed this value is generated to be
        unique in a single aggregation tree)
    :var level: The level of the aggregation tree at which the group appears
    :var is_root_level: Whether the group returns at the highest level of the
        agregation tree
    :var aggregation_actors: A list of peers appearing in the group under role
        aggregation actor
    :var participating_nodes: A list of peers appearing in the group under role
        aggregation participants
    """
    def __init__(self, id, level, is_root_level=False):
        self.id = id
        self.level = level
        self.is_root_level = is_root_level
        self.aggregation_actors = []
        self.participating_nodes = []

    def __str__(self):
        return f'Group(id={self.id}; level={self.level}; '\
            f'actors={self.aggregation_actors}; participants={self.participating_nodes})'

    def __repr__(self):
        return self.__str__()



class AggregationTree:
    """Class representing aggregation tree

    :var groups: A list of aggregation groups in the tree in no specific order by
        default
    """
    def __init__(self):
        self.groups = []

    def __str__(self):
        return f'Tree(groups={self.groups})'

    def __repr__(self):
        return self.__str__()
