import data
import network_model

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
from queue import Queue

from utils.mlutils import train_epoch, test
from utils.secret_sharing import create_additive_shares
from utils.numberutils import convert_to_int_array, convert_to_float_array
from utils.torchutils import convert_state_dict_to_numpy, \
    convert_numpy_state_dict_to_torch
from utils.dictutils import map_dict

from privacy_preserving_aggregator import PrivacyPreservingAggregator

import os,sys,inspect
current_dir = os.path.dirname(
    os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from netutils.zmqsockets import ZMQDirectSocket
from netutils.message import *

DIGITS_TO_KEEP = 6


def prepare_state_dict_and_create_shares(state_dict, num_shares):
    numpy_state_dict = convert_state_dict_to_numpy(state_dict)
    share_state_dictionaries = [{} for _ in range(num_shares)]
    for layer_name, layer_data in numpy_state_dict.items():
        shares = create_additive_shares(layer_data, num_shares)
        for i, share_i in enumerate(shares):
            share_i_int = convert_to_int_array(share_i, DIGITS_TO_KEEP)
            share_state_dictionaries[i][layer_name] = share_i_int
    return share_state_dictionaries


def aggregate_shares(shares):
    assert len(shares) != 0, 'No additive shares'
    result = {}
    layer_names = shares[0].keys()
    for layer_name in layer_names:
        result[layer_name] = sum(share[layer_name] for share in shares)
    return result


def train_and_send(args, model, device, train_loader, test_loader, optimizer, addr_message, server_address):
    aggregator = PrivacyPreservingAggregator(addr_message, server_address, False)
    aggregator.start()
    # new_model_dict = aggregator.aggregate(model.state_dict())
    # model.load_state_dict(new_model_dict)
    # print('New model loaded')


    for epoch in range(1, args.epochs + 1):
        print("----------- Epoch", epoch, "starts ----------- ")
        train_epoch(args, model, device, train_loader, optimizer, epoch)
        print("\nTest result before averaging:")
        test(model, device, test_loader)
        print("----------- Epoch", epoch, "finished ----------- ")

        new_state_dict = aggregator.aggregate(model.state_dict())
        model.load_state_dict(new_state_dict)
        print('Loading the averaged model')

        print("\nTest result after averaging:")
        test(model, device, test_loader)


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
    parser.add_argument('--debug', default=False,
                        action='store_true',
                        help='Activate debug mode.')
    return parser.parse_args()


def main(args):
    # Step 1:
    # Prepare configuration
    use_cuda = not args.no_cuda and torch.cuda.is_available()
    torch.manual_seed(args.seed)
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
    model = network_model.Net().to(device)
    optimizer = optim.Adadelta(model.parameters(), lr=args.lr)

    train_set, test_set = data.load_data(args.num, args.total)
    train_idx = list(range(0, len(train_set), 5))
    trainset = torch.utils.data.Subset(train_set, train_idx)
    train_loader = torch.utils.data.DataLoader(trainset, **train_kwargs)
    test_loader = torch.utils.data.DataLoader(test_set, **test_kwargs)

    server_address = 'tcp://' + args.server

    train_and_send(args, model, device, train_loader, test_loader,
            optimizer, addr_message, server_address)


if __name__ == '__main__':
    main(parse_args())
