from queue import Queue, Empty
from threading import Lock

class AggregationModelQueue:
    """Stores models for participants and implements logic for easy handling
    of these models
    """
    def __init__(self, participants):
        """
        :param participants: identifiers of participants (presumably addresses)
        :type participants: list[str]
        """
        self.__participant_models = {
            participant: None\
            for participant in participants
        }
        self.__remaining_models = len(participants)
        self.__model_queue = Queue()
        self.__lock = Lock()

    def add(self, participant, model):
        """Adds model for given participant. If it already has model for this
        participant or if participant is not in the list of participants
        for this model queue then exception ValueError is risen

        :param participant: Identifier of the participant (presumably address)
        :type participant: str

        :param model: Model to store for the given participant
        :type model: object

        :raises ValueError: Participant is not in the specified list in the
            constructor or there is already a model set for the given participant
        """
        with self.__lock:
            if participant not in self.__participant_models:
                raise ValueError('Participant not in group')
            if self.__participant_models[participant] is not None:
                raise ValueError('Already received model')
            self.__remaining_models -= 1
            self.__participant_models[participant] = model
            self.__model_queue.put(model)

    def is_empty(self):
        """Returns true if models from all participants are received and there
        is no model in queue to be retrieved. False is returned otherwise.

        :rtype: bool
        """
        return self.__remaining_models == 0 and self.__model_queue.empty()

    def get(self):
        """Get's a model from queue

        :raises queue.Empty: no model is available and no model
            can be received anymore

        :return: Next model from the queue
        :rtype: object
        """
        if self.is_empty():
            raise Empty('No more models to receive')
        return self.__model_queue.get()
