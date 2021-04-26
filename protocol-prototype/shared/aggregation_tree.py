class AggregationGroup:
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
    def __init__(self):
        self.groups = []

    def __str__(self):
        return f'Tree(groups={self.groups})'

    def __repr__(self):
        return self.__str__()
