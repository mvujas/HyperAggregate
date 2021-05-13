from abc import ABC, abstractmethod

class AbstractAggregationProfile(ABC):
    """Base class for secure aggregation logic and handling data sent over
    network
    """
    def __init__(self):
        pass

    @abstractmethod
    def prepare(self, data):
        """Prepares data into form ready for sending over network"""
        pass

    @abstractmethod
    def create_shares_on_prepared_data(self, prepared_data, num_shares):
        """Creates shares on data already prepared for transfer over network"""
        pass

    @abstractmethod
    def unprepare(self, prepared_data):
        """Transform data received over network into the form usable by
        the application
        """
        pass

    @abstractmethod
    def aggregate(self, prepared_shares):
        """Aggregates shares (in form of prepared data) into single unit
        of data
        """
        pass
