import argparse
from privacy_preserving_server import SchedulingServer

def parse_args():
    parser = argparse.ArgumentParser(description='DeAI privacy preserving server')
    parser.add_argument('--port', default='5555', metavar='N',
                        help='input server port number (default: 5555)')
    args = parser.parse_args()
    return args


def main(args):
    server = SchedulingServer(args.port, group_size=3, num_actors=2, debug_mode=True)
    server.start()


if __name__ == "__main__":
    main(parse_args())
