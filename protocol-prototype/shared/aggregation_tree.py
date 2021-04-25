class AggregationGroup:
    def __init__(self, level, is_root_level=False):
        self.level = level
        self.is_root_level = is_root_level
        self.aggregation_actors = []
        self.participating_nodes = []

    def __str__(self):
        return f'Group(level={self.level}; actors={self.aggregation_actors}; '\
            f'participants={self.participating_nodes})'

    def __repr__(self):
        return self.__str__()



class AggregationTree:
    def __init__(self):
        self.groups = []

    def __str__(self):
        return f'Tree(groups={self.groups})'

    def __repr__(self):
        return self.__str__()
