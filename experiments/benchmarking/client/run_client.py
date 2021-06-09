"""
Starts a client node and setups up everything for decentralized MNIST training.
"""
from .data import load_data
from .network_model import MNISTNet
from .mlutils import train_epoch, test

import argparse
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torchvision import datasets, transforms
from torch.optim.lr_scheduler import StepLR
import time
import random
import traceback

from hyperaggregate.client.privacy_preserving_aggregator import PrivacyPreservingAggregator


def train_and_send(args, model, device, train_loader, test_loader, optimizer, addr_message):
    """Trains the model locally and does aggregation with other clients after
    each epoch

    :param args: Command line arguments
    :param model: Neural network to train
    :param device: Device on which to train the model
    :param train_loader: Data loader for training data
    :param test_loader: Data loader for test data
    :param optimizer: Optimizer used for training
    :param addr_message: The address on which the client should run
    """
    # Initialize aggregation client
    aggregator = PrivacyPreservingAggregator(addr_message, args.server, False)
    aggregator.start()
    # Prepare structure to track if milestones are reached
    accuracies_to_achieve = args.milestones
    achieved = [
        False
        for acc in accuracies_to_achieve
    ]
    for epoch in range(1, args.epochs + 1):
        # Do training and evaluation before aggregation
        print("----------- Epoch", epoch, "starts ----------- ")
        if not args.aggregation_only:
            train_epoch(args, model, device, train_loader, optimizer, epoch)
            if args.pre_aggregation_evaluation:
                print("\nTest result before averaging:")
                test(model, device, test_loader)
            print("----------- Epoch", epoch, "finished ----------- ")

        # Do aggregation and load the aggregated model
        state_dictionary = model.state_dict()
        for k in state_dictionary:
            state_dictionary[k] = state_dictionary[k].cpu()

        new_state_dict = aggregator.aggregate(state_dictionary)
        time_elapsed = aggregator.time_elapsed

        for k in new_state_dict:
            new_state_dict[k] = new_state_dict[k].to(device)

        model.load_state_dict(new_state_dict)
        print(f'Loading the averaged model, time elapsed: {time_elapsed}')

        # Post-aggregation evaluation
        if not args.aggregation_only:
            print("\nTest result after averaging:")
            loss, accuracy = test(model, device, test_loader)

        # Sending important information to the benchmark server
        if args.benchmark_server is not None:
            # Always send the time it took for aggregation
            aggregator.send(args.benchmark_server, ('time-only', time_elapsed))
            for i, acc in enumerate(accuracies_to_achieve):
                # Send the number of iteratios it took to achieve a milestone
                #   only the first time it is exceeded
                if not achieved[i] and accuracy / 100 >= acc:
                    achieved[i] = True
                    aggregator.send(args.benchmark_server,
                        (f'achieved-{acc}', epoch))
    # Prematurely closing it may cause some clients not to recieve the model
    #   Seems not to be the issue in the later iterations of the software,
    #   but it's still left there to avoid any unexpected behaviour
    time.sleep(5)
    aggregator.stop()


def parse_args():
    """Get command line arguments"""
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
    parser.add_argument('--num', type=int, default=0, metavar='N',
                        help='Number of this peer (used to decide which part of'\
                            'the original dataset is trained on this peer)')
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
    parser.add_argument('--aggregation-only', default=False,
                        action='store_true',
                        help='Skip training and evaluation phase, but do '\
                            'aggregation only')
    parser.add_argument('--milestones', type=str, default='',
                        help='List of milestone accuracies that the client '\
                            'should notify the benchmark server when achieved '\
                            'for the first time (example: 0.7,0.8,0.9)')
    parser.add_argument('--pre-aggregation-evaluation', default=False,
                        action='store_true',
                        help='Evaluate model before aggregation, not only after')
    parser.add_argument('--debug', default=False,
                        action='store_true',
                        help='Activate debug mode.')
    return parser.parse_args()


def main(args):
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
    # Convert milestones string into list of floats
    milestones_float = []
    for milestone in args.milestones.split(','):
        try:
            milestone_acc = float(milestone.strip())
            milestones_float.append(milestone_acc)
        except:
            pass
    args.milestones = milestones_float
    # Puts the address of the peer in the proper format
    addr_message = 'tcp://' + args.client
    port = args.client.split(':')[-1]
    print("Starting the program on", addr_message)

    try:
        print("Initializing the network model and dataset...")
        # Initializing model and optimizer
        model = MNISTNet().to(device)
        optimizer = optim.Adadelta(model.parameters(), lr=args.lr)

        # Loading datasets
        train_set, test_set = load_data(args.num, args.total)
        train_idx = list(range(0, len(train_set), args.data_skip))
        trainset = torch.utils.data.Subset(train_set, train_idx)
        train_loader = torch.utils.data.DataLoader(trainset, **train_kwargs)
        test_loader = torch.utils.data.DataLoader(test_set, **test_kwargs)

        # Putting aggregation and benchmark server endpoints in
        #   the proper format
        args.server = f'tcp://{args.server}'
        if args.benchmark_server is not None:
            args.benchmark_server = f'tcp://{args.benchmark_server}'

        # Aggregation training
        train_and_send(args, model, device, train_loader, test_loader,
                optimizer, addr_message)
    except Exception as exc:
        print('Exception while running a client:', exc)
        traceback.print_tb(exc.__traceback__)


if __name__ == '__main__':
    main(parse_args())
