import argparse
from privacy_preserving_server import SchedulingServer

def parse_args():
    parser = argparse.ArgumentParser(description='DeAI prvacy preserving server')
    parser.add_argument('--port', default='5555', metavar='N',
                        help='input server port number (default: 5555)')
    args = parser.parse_args()
    return args


def main(args):
    server = SchedulingServer(args.port, debug_mode=True)
    server.start()


if __name__ == "__main__":
    main(parse_args())
