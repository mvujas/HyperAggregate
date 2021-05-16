from multiprocessing import Process
from recordtype import recordtype
from server import server
from client import privacy_preserving_client
import benchmark_server

import time
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description='Benchmark test')
    parser.add_argument('--epochs', type=int, default=1, metavar='N',
                        help='number of epochs to train (default: 1)')
    parser.add_argument('--no-cuda', action='store_true', default=False,
                        help='disables CUDA training')
    parser.add_argument('--total', type=int, default=6,
                        help='Total number of peers')
    parser.add_argument('--client-start-port', default=6000, type=int,
                        help='The client starting port (default: 6000)')
    parser.add_argument('--client-port-dif', default=100, type=int,
                        help='The client port diference (default: 100)')
    parser.add_argument('--server-port', default=5555, type=int,
                        help='The server port (default: 5555)')
    parser.add_argument('--server-target-size', default=6, type=int,
                        help='Total number of clients per aggregation (default: 6)')
    parser.add_argument('--server-group-size', default=3, type=int,
                        help='Size of group (default: 3)')
    parser.add_argument('--server-num-actors', default=2, type=int,
                        help='Number of actors per group (default: 2)')
    parser.add_argument('--benchmark-server-port', default=5556, type=int,
                        help='The benchamrk server port (default: 5556)')
    parser.add_argument('--data-skip', type=int, default=25,
                        help='Indicates the program to use only every n-th data '\
                            'sample for training (default: 25)')
    parser.add_argument('--debug', default=False,
                        action='store_true',
                        help='Activate debug mode.')

    return parser.parse_args()

def main(args):
    server_args = {
        'port': args.server_port,
        'target_size': args.server_target_size,
        'group_size': args.server_group_size,
        'num_actors': args.server_num_actors
    }
    benchamrk_server_args = {
        'port': args.benchmark_server_port
    }
    client_args = {
        'batch_size': 64,
        'test_batch_size': 1000,
        'epochs': args.epochs,
        'lr': 1.0,
        'gamma': 0.7,
        'no_cuda': args.no_cuda,
        'dry_run': False,
        'seed': 1,
        'log_interval': 10,
        'save_model': False,
        'num': 0,
        'total': 1,
        'client': '',
        'server': f'127.0.0.1:{args.server_port}',
        'data_skip': args.data_skip,
        'benchmark_server': f'127.0.0.1:{args.benchmark_server_port}',
        'debug': args.debug
    }
    server_args = recordtype("ServerArgs", server_args.keys())(*server_args.values())
    benchamrk_server_args = recordtype("BenchmarkServerArgs", benchamrk_server_args.keys())(*benchamrk_server_args.values())
    client_args = recordtype("ClientArgs", client_args.keys())(*client_args.values())

    server_process = Process(target=server.main, args=(server_args,))
    server_process.start()

    benchmark_server_process = Process(target=benchmark_server.main, args=(benchamrk_server_args,))
    benchmark_server_process.start()
    time.sleep(2)

    client_processes = []
    for i in range(args.total):
        port = args.client_start_port + i * args.client_port_dif
        client_args.client = f'127.0.0.1:{port}'
        client_processes.append(
            Process(target=privacy_preserving_client.main, args=(client_args,))
        )
        client_processes[-1].start()

if __name__ == "__main__":
    main(parse_args())
