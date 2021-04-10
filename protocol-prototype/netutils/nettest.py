from zmqsockets import ZMQDirectSocket
import time

class Object1:
    def __init__(self, x):
        self.a = x

    def __str__(self):
        return str(self.a)

    def __repr__(self):
        return self.__str__()

s1 = ZMQDirectSocket('tcp://127.0.0.1:83412', debug_mode=True)
s1.start(None)

time.sleep(1)
print(1)

s2 = ZMQDirectSocket('tcp://127.0.0.1:83414', debug_mode=True)
s2.send('tcp://127.0.0.1:83412', Object1(123))
