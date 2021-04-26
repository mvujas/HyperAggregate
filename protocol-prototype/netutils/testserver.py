from zmqsockets import ZMQDirectSocket
import time

def cb(addr, msg):
    print('Message received from address:', addr)
    print('Message:', msg)
    # print(msg(5))

s = ZMQDirectSocket('tcp://127.0.0.1:83420', True)
s.start(cb)
time.sleep(10)
s.stop()
