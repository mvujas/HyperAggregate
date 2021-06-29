import json
import time
import asyncio
from utils.interoperability_utils import deserialize_model, serialize_model
from hyperaggregate.client.privacy_preserving_aggregator import \
    PrivacyPreservingAggregator

import argparse

def parse_args():
    """Get command line arguments"""
    parser = argparse.ArgumentParser(description='DeAI secure aggregation middleware')
    parser.add_argument('--port', default=5555, type=int, required=True,
                        help='input server port number (default: 5555)')
    parser.add_argument('--aggregation-client-port', default=5556, type=int,
                        required=True,
                        help='input server port number (default: 5556)')
    parser.add_argument('--aggregation-server-address', type=str, required=True,
                        help='address of aggregation server')
    args = parser.parse_args()
    return args


class IntercommunicatorServerProtocol(asyncio.Protocol):
    """Does event/message handling for middleware server"""
    def __init__(self, args):
        self.aggregator = PrivacyPreservingAggregator(
            f'tcp://127.0.0.1:{args.aggregation_client_port}',
            f'tcp://{args.aggregation_server_address}',
            False
        )
        self.aggregator.start()

    def connection_made(self, transport):
        """Callback called on client connection"""
        peername = transport.get_extra_info('peername')
        print('Connection from {}'.format(peername))
        self.transport = transport

    def data_received(self, data):
        """Callback called on message received"""
        print('Received aggregation request')
        time_of_receive = int(time.time() * 1000)

        # Reconstruct the model
        message = data.decode()
        obj = json.loads(message)
        model = deserialize_model(obj['model'])

        time_of_aggregation_start = int(time.time() * 1000)

        # Aggregate model with other peers
        aggregated_model = self.aggregator.aggregate(model)

        time_of_aggregation_ending = int(time.time() * 1000)

        response = {
            'model': serialize_model(aggregated_model),
            'sign_up_to_aggregation_end_time': time_of_aggregation_ending - \
                time_of_aggregation_start,
            'aggregation_time': self.aggregator.time_elapsed,
            'callTime': obj['callTime'],
            'time_until_receive': time_of_receive - obj['callTime'],
            'time_of_sending_back': int(time.time() * 1000)
        }

        # Return the aggregated model to javascript
        print('Returning model update')
        self.transport.write(json.dumps(response).encode())


class MiddlewareServer:
    """Server side of middleware. Created with only 1 client in mind, so it
    doesn't work with multiple client
    """
    def __init__(self, args):
        self.loop = asyncio.get_event_loop()
        self.coro = self.loop.create_server(
            lambda: IntercommunicatorServerProtocol(args),
            '127.0.0.1',
            args.port)
        self.server = None

    def run(self):
        self.__start()
        try:
            self.loop.run_forever()
        except KeyboardInterrupt:
            pass
        self.__close()

    def __start(self):
        self.server = self.loop.run_until_complete(self.coro)
        print('Serving on {}'.format(self.server.sockets[0].getsockname()))

    def __close(self):
        self.server.close()
        self.loop.run_until_complete(self.server.wait_closed())
        self.loop.close()


if __name__ == "__main__":
    args = parse_args()
    MiddlewareServer(args).run()
