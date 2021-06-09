"""
Starts aggregation server
"""
import argparse
from hyperaggregate.server.privacy_preserving_server import SchedulingServer
from hyperaggregate.aggregation_profiles.impl.additive_sharing_model_profile import \
    AdditiveSharingModelProfile

def parse_args():
    """Get command line arguments"""
    parser = argparse.ArgumentParser(description='DeAI privacy preserving server')
    parser.add_argument('--port', default='5555', metavar='N',
                        help='input server port number (default: 5555)')
    parser.add_argument('--target-size', default=6, type=int,
                        help='Total number of clients per aggregation (default: 6)')
    parser.add_argument('--group-size', default=3, type=int,
                        help='Size of group (default: 3)')
    parser.add_argument('--num-actors', default=2, type=int,
                        help='Number of actors per group (default: 2)')
    args = parser.parse_args()
    return args


def main(args):
    # Creates aggregation logic server by the server to client
    DIGITS_TO_KEEP = 6
    agg_profile = AdditiveSharingModelProfile(DIGITS_TO_KEEP)
    # Creates and start the server
    server = SchedulingServer(
        args.port, target_size=args.target_size, group_size=args.group_size,
        num_actors=args.num_actors, aggregation_profile=agg_profile,
        debug_mode=False)
    server.start()


if __name__ == "__main__":
    main(parse_args())
