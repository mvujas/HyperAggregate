from zmqsockets import ZMQDirectSocket
import time

def cb(addr, msg):
    print('Message received from address:', addr)
    print('Message:', msg)

def f(x):
    return x // 2

s = ZMQDirectSocket('tcp://127.0.0.1:83421', True)
s.start(cb)
time.sleep(2)
s.send('tcp://127.0.0.1:83420', {
    'pera': 1,
    'mara': 2
})
s.stop()
