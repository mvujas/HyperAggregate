import torch
from torchvision import datasets, transforms

import os

def load_data(num, total):
    """Loads a fraction of dataset for the given peer

    :param num: The index of the peer
    :type num: int

    :param total: Total number of peers
    :type total: int

    :return: Training and test data loader
    :rtype: tuple[torch.utils.data.DataLoader, torch.utils.data.DataLoader]
    """
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])

    print(os.path.abspath('./data'))
    train_set = datasets.MNIST('./data', train=True, download=True,
                               transform=transform)
    test_set = datasets.MNIST('./data', train=False,
                              transform=transform)

    # Use a subset of the whole training set
    indices = range(len(train_set) // total * num,
                    len(train_set) // total * (num + 1))
    train_set = torch.utils.data.Subset(train_set, indices)

    return train_set, test_set
