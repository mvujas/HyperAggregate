from zmqsockets import ZMQDirectSocket
import time

def cb(addr, msg):
    print('Message received from address:', addr)
    print('Message:', msg)

s = ZMQDirectSocket('tcp://127.0.0.1:83421', True)
s.start(cb)
for i in range(10):
    s.send('tcp://127.0.0.1:83420', i)
    time.sleep(1)
s.stop()
