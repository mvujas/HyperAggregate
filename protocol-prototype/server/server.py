import argparse
from privacy_preserving_server import SchedulingServer
from aggregation_profiles.impl.additive_sharing_model_profile import \
    AdditiveSharingModelProfile

def parse_args():
    parser = argparse.ArgumentParser(description='DeAI privacy preserving server')
    parser.add_argument('--port', default='5555', metavar='N',
                        help='input server port number (default: 5555)')
    args = parser.parse_args()
    return args


def main(args):
    DIGITS_TO_KEEP = 6
    agg_profile = AdditiveSharingModelProfile(DIGITS_TO_KEEP)
    server = SchedulingServer(
        args.port, group_size=3, num_actors=2,
        aggregation_profile=agg_profile, debug_mode=True)
    server.start()


if __name__ == "__main__":
    main(parse_args())
