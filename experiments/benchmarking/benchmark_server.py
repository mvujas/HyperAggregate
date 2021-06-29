import argparse
from hyperaggregate.netutils.zmqsockets import ZMQDirectSocket
import time

def parse_args():
    parser = argparse.ArgumentParser(description='Benchmark server')
    parser.add_argument('--port', default='83420', metavar='N',
                        help='input server port number (default: 83420)')
    parser.add_argument('--log-file', type=str, default='log.txt',
                        help='Path to the log file (default: log.txt)')
    args = parser.parse_args()
    return args

def avg(arr):
    return sum(arr) / len(arr)

def main(args):
    time_arrs = dict()
    def callback(address, message, arrs):
        msg_type, payload = message
        if msg_type not in time_arrs:
            arrs[msg_type] = []
        arrs[msg_type].append(payload)
        arr = arrs[msg_type]
        txt = f'Running average for \'{msg_type}\' after {len(arr)} times: {avg(arr)}'
        print(txt)
        with open(args.log_file, 'a') as f:
            print(txt, file=f)
    address = f'tcp://*:{args.port}'
    socket = ZMQDirectSocket(address, False)
    socket.start(lambda addr, msg: callback(addr, msg, time_arrs))
    try:
        while(True):
            time.sleep(1)
    except KeyboardInterrupt:
        with open('benchmark-log_30_05_2021.txt', 'a') as f:
            print('All times:', time_arrs, file=f)

if __name__ == "__main__":
    main(parse_args())
