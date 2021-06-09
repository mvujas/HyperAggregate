import torch.nn.functional as F
import torch


def train_epoch(args, model, device, train_loader, optimizer, epoch):
    """Trains the model for a single epoch

    :param args: Configuration arguments
    :param model: Model to train
    :param device: Device on which the model should be trained
    :param train_loader: Data loader for training data
    :param optimizer: Optimizer to use for training
    :param epoch: The number of the current epoch (used only for logging
        purposes)
    """
    model.train()
    for batch_idx, (data, target) in enumerate(train_loader):
        data, target = data.to(device), target.to(device)
        optimizer.zero_grad()
        output = model(data)
        loss = F.nll_loss(output, target)
        loss.backward()
        optimizer.step()
        if batch_idx % args.log_interval == 0:
            print('Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}'.format(
                epoch, batch_idx * len(data), len(train_loader.dataset),
                100. * batch_idx / len(train_loader), loss.item()))
            if args.dry_run:
                break


def test(model, device, test_loader):
    """Evaluates the loss and accuracy of the model

    :param model: Model to test
    :param device: Device on which the evaluation should be done
    :param test_loader: Data loader for test data

    :return: The loss and accuracy of the model on the given data
    :rtype: tuple[float, float]
    """
    model.eval()
    test_loss = 0
    correct = 0
    with torch.no_grad():
        for data, target in test_loader:
            data, target = data.to(device), target.to(device)
            output = model(data)
            # sum up batch loss
            test_loss += F.nll_loss(output, target, reduction='sum').item()
            # get the index of the max log-probability
            pred = output.argmax(dim=1, keepdim=True)
            correct += pred.eq(target.view_as(pred)).sum().item()

    test_loss /= len(test_loader.dataset)
    accuracy = 100. * correct / len(test_loader.dataset)
    print('Test set: Average loss: {:.4f}, Accuracy: {}/{} ({:.0f}%)\n'.format(
        test_loss, correct, len(test_loader.dataset),
        accuracy))

    return test_loss, accuracy
