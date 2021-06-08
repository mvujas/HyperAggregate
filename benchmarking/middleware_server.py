import json
import asyncio
from middleware.interoperability_utils import deserialize_model, serialize_model
from client import privacy_preserving_client

import argparse

def parse_args():
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

args = parse_args()

aggregator = privacy_preserving_client.PrivacyPreservingAggregator(
    f'tcp://127.0.0.1:{args.aggregation_client_port}', f'tcp://{args.aggregation_server_address}', False)
aggregator.start()

class EchoServerClientProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        print('Connection from {}'.format(peername))
        self.transport = transport

    def data_received(self, data):
        print('Received aggregation request')
        message = data.decode()
        obj = json.loads(message)
        model = deserialize_model(obj)

        aggregated_model = aggregator.aggregate(model)
        print('Returning model update')
        # print(aggregated_model)
        # print(json.dumps(serialize_model(aggregated_model)))

        self.transport.write(json.dumps(serialize_model(aggregated_model)).encode())

        # self.transport.write(data)
        # self.transport.close()


class IntecommunicationServer:
    """Server side of middleware. Created with only 1 client in mind, so it
    doesn't work with multiple client
    """
    def __init__(self, port):
        self.loop = asyncio.get_event_loop()
        self.coro = self.loop.create_server(
            EchoServerClientProtocol, '127.0.0.1', port)
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
    IntecommunicationServer(args.port).run()
