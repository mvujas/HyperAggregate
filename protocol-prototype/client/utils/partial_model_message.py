class PartialModelMessage:
    """Message wrapper around partial share of model for given group"""
    def __init__(self, group_id, model):
        self.group_id = group_id
        self.model = model
