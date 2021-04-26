from queue import Queue, Empty
from threading import Lock

class AggregationProfile:
    def __init__(self, participants):
        self.__participant_models = {
            participant: None\
            for participant in participants
        }
        self.__remaining_models = len(participants)
        self.__model_queue = Queue()
        self.__lock = Lock()

    def add(self, participant, model):
        with self.__lock:
            if participant not in self.__participant_models:
                raise ValueError('Participant not in group')
            if self.__participant_models[participant] is not None:
                raise ValueError('Already received model')
            self.__remaining_models -= 1
            self.__participant_models[participant] = model
            self.__model_queue.put(model)

    def is_empty(self):
        return self.__remaining_models == 0 and self.__model_queue.empty()

    def get(self):
        if self.is_empty():
            raise Empty('No more models to receive')
        return self.__model_queue.get()
