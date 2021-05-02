import argparse
from netutils.zmqsockets import ZMQDirectSocket

def parse_args():
    parser = argparse.ArgumentParser(description='Benchmark server')
    parser.add_argument('--port', default='83420', metavar='N',
                        help='input server port number (default: 83420)')
    args = parser.parse_args()
    return args

def avg(arr):
    return sum(arr) / len(arr)

def main(args):
    time_arr = []
    def callback(address, message, arr):
        arr.append(message)
        print(f'Running average after {len(arr)} times: {avg(arr)}')
    address = f'tcp://*:{args.port}'
    socket = ZMQDirectSocket(address, False)
    socket.start(lambda addr, msg: callback(addr, msg, time_arr))

if __name__ == "__main__":
    main(parse_args())
