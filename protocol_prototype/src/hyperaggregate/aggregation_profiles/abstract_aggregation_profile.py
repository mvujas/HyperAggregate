from abc import ABC, abstractmethod

class AbstractAggregationProfile(ABC):
    """Base class for secure aggregation logic and handling data sent over
    network
    """
    def __init__(self):
        pass

    @abstractmethod
    def prepare(self, data):
        """Prepares data into form ready for sending over network

        :type data: object

        :return: Data prepared for sending over network
        :rtype: object
        """
        pass

    @abstractmethod
    def create_shares_on_prepared_data(self, prepared_data, num_shares):
        """Creates shares on data already prepared for transfer over network

        :param prepared_data: Data in the form ready to be sent over network
        :type prepared_data: object

        :param num_shares: Number of shares to split data into
        :type num_shares: int

        :return: List of data shares in the form ready to be sent over network
        :rtype: list(object)
        """
        pass

    @abstractmethod
    def unprepare(self, prepared_data):
        """Transform data received over network into the form usable by
        the application

        :param prepared_data: Data in the form ready to be sent over network
        :type prepared_data: object

        :return: Data in the form which application can use
        :rtype: object
        """
        pass

    @abstractmethod
    def aggregate(self, prepared_shares):
        """Aggregates shares (in form of prepared data) into single unit
        of data

        :param prepared_shares: list of data shares in the form ready to be sent
            over network
        :type prepared_shares: list(object)

        :return: The aggregate of shares in the form ready to be sent
            over network
        :rtype: object
        """
        pass
