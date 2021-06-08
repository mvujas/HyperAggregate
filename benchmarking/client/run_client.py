from .data import load_data
from .network_model import Net
from .mlutils import train_epoch, test

import argparse
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torchvision import datasets, transforms
from torch.optim.lr_scheduler import StepLR
import queue
import json
import pickle
import zmq
import time
import random
import timeit
from queue import Queue


from hyperaggregate.client.privacy_preserving_aggregator import PrivacyPreservingAggregator

# BENCHMARK_SERVER_ADDRESS = 'tcp://127.0.0.1:83420'
# ACCURACY_THRESHOLD = 90

def train_and_send(args, model, device, train_loader, test_loader, optimizer, addr_message):
    """Trains the model locally and does aggregation with other clients after
    each epoch

    :param
    """
    # reached_milestone = False

    aggregator = PrivacyPreservingAggregator(addr_message, args.server, False)
    aggregator.start()
    # start_time = timeit.default_timer()
    accuracies_to_achieve = [0.6, .7, .8, .9, .95, .97]
    achieved = [
        False
        for acc in accuracies_to_achieve
    ]
    for epoch in range(1, args.epochs + 1):
        print("----------- Epoch", epoch, "starts ----------- ")
        train_epoch(args, model, device, train_loader, optimizer, epoch)
        # print("\nTest result before averaging:")
        # test(model, device, test_loader)
        print("----------- Epoch", epoch, "finished ----------- ")


        new_state_dict = aggregator.aggregate(model.state_dict())
        time_elapsed = aggregator.time_elapsed

        model.load_state_dict(new_state_dict)
        print(f'Loading the averaged model, time elapsed: {time_elapsed}')

        print("\nTest result after averaging:")
        loss, accuracy = test(model, device, test_loader)

        if args.benchmark_server is not None:
            aggregator.send(args.benchmark_server, ('time-only', time_elapsed))

            # print('Accuracy')
            for i, acc in enumerate(accuracies_to_achieve):
                # print(f'Checking {acc}')
                if not achieved[i] and accuracy / 100 >= acc:
                    achieved[i] = True
                    # print(f'Accuracy {acc} achieved')
                    aggregator.send(args.benchmark_server, (f'achieved-{acc}', epoch))



        # if not reached_milestone and accuracy >= ACCURACY_THRESHOLD:
        #     end_time = timeit.default_timer()
        #     time_elapsed = end_time - start_time
        #     if args.benchmark_server is not None:
        #         aggregator.send(args.benchmark_server, time_elapsed)
        #     reached_milestone = True
    print('Training over', args.epochs)
    # Prematurely closing it may cause some clients not to recieve the model
    time.sleep(5)
    aggregator.stop()


def parse_args():
    # Step 1:
    # Parse command line arguments about server address, local port number, peer number, etc.
    parser = argparse.ArgumentParser(description='DeAI privacy preserving peer client')
    parser.add_argument('--batch-size', type=int, default=64, metavar='N',
                        help='input batch size for training (default: 64)')
    parser.add_argument('--test-batch-size', type=int, default=1000, metavar='N',
                        help='input batch size for testing (default: 1000)')
    parser.add_argument('--epochs', type=int, default=14, metavar='N',
                        help='number of epochs to train (default: 14)')
    parser.add_argument('--lr', type=float, default=1.0, metavar='LR',
                        help='learning rate (default: 1.0)')
    parser.add_argument('--gamma', type=float, default=0.7, metavar='M',
                        help='Learning rate step gamma (default: 0.7)')
    parser.add_argument('--no-cuda', action='store_true', default=False,
                        help='disables CUDA training')
    parser.add_argument('--dry-run', action='store_true', default=False,
                        help='quickly check a single pass')
    parser.add_argument('--seed', type=int, default=1, metavar='S',
                        help='random seed (default: 1)')
    parser.add_argument('--log-interval', type=int, default=10, metavar='N',
                        help='how many batches to wait before logging training status')
    parser.add_argument('--save-model', action='store_true', default=False,
                        help='For Saving the current Model')
    # The number is used to decide which part of the original dataset is trained on this peer.
    parser.add_argument('--num', type=int, default=0, metavar='N',
                        help='Number of this peer')
    parser.add_argument('--total', type=int, default=1, metavar='N',
                        help='Total number of peers')
    parser.add_argument('--client', default='127.0.0.1:6000', metavar='N',
                        help='The client address (default: 127.0.0.1:6000)')
    parser.add_argument('--server', default='127.0.0.1:5555', metavar='N',
                        help='The server address (default: 127.0.0.1:5555)')
    parser.add_argument('--benchmark-server', default=None, type=int,
                        help='The benchmark server address')
    parser.add_argument('--data-skip', type=int, default=25,
                        help='Indicates the program to use only every n-th data '\
                            'sample for training (default: 25)')
    parser.add_argument('--debug', default=False,
                        action='store_true',
                        help='Activate debug mode.')
    return parser.parse_args()


def main(args):
    # Step 1:
    # Prepare configuration
    use_cuda = not args.no_cuda and torch.cuda.is_available()
    torch.manual_seed(args.seed)
    random.seed(args.seed)
    device = torch.device("cuda" if use_cuda else "cpu")
    train_kwargs = {'batch_size': args.batch_size}
    test_kwargs = {'batch_size': args.test_batch_size}
    if use_cuda:
        cuda_kwargs = {'num_workers': 1,
                       'pin_memory': True,
                       'shuffle': True}
        train_kwargs.update(cuda_kwargs)
        test_kwargs.update(cuda_kwargs)
    addr_message = 'tcp://' + args.client
    port = args.client.split(':')[-1]
    print("Starting the program on", addr_message)

    # Step 2:
    # Initialize the network model and dataset.
    print("Initializing the network model and dataset...")
    try:
        model = Net().to(device)
        optimizer = optim.Adadelta(model.parameters(), lr=args.lr)

        train_set, test_set = load_data(args.num, args.total)
        train_idx = list(range(0, len(train_set), args.data_skip))
        trainset = torch.utils.data.Subset(train_set, train_idx)
        train_loader = torch.utils.data.DataLoader(trainset, **train_kwargs)
        test_loader = torch.utils.data.DataLoader(test_set, **test_kwargs)

        args.server = f'tcp://{args.server}'
        if args.benchmark_server is not None:
            args.benchmark_server = f'tcp://{args.benchmark_server}'

        train_and_send(args, model, device, train_loader, test_loader,
                optimizer, addr_message)
    except Exception as e:
        print('Exception while running a client:', e)

if __name__ == '__main__':
    main(parse_args())
