class PartialModelMessage:
    """Message wrapper around partial share of model for given group

    :var group_id: Identifier of the aggregation group inside which the message
        is sent
    :var model: Model
    """
    def __init__(self, group_id, model):
        self.group_id = group_id
        self.model = model
