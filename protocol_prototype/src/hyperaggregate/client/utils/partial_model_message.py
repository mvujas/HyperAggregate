class PartialModelMessage:
    """Message wrapper around partial share of model for given group

    :var aggregation_id: Identifier for aggregation that this message is part of
    :var group_id: Identifier of the aggregation group inside which the message
        is sent
    :var model: Model
    """
    def __init__(self, aggregation_id, group_id, model):
        self.aggregation_id = aggregation_id
        self.group_id = group_id
        self.model = model
