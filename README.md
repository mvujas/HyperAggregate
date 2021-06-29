# HyperAggregate: A sublinear aggregation algorithm implementation

Implementation of in-house secure aggregation protocol for decentralized collaborative machine learning.

The documentation can be accessed by opening `protocol_prototype/docs/_build/html/index.html` in browser.

The protocol is based on the work thoroughly described in [this report](https://infoscience.epfl.ch/record/286909).

The implementation works in the setting with multiple peers and a single helper server used for peer discovery, as well as an aggregation waiting queue. The server doesn't actively play a role in aggregation, but plays a significant role in the steps that lead up to it. The current iteration of the protocol doesn't support peers dropping out during aggregation.

## Installation

The package is available in directory protocol_prototype. It requires Python version `>= 3.6`. It can be installed by running the following in the root of the project:
```bash
pip install protocol_prototype
```
This command will install the package and all required dependencies.

The package is only the secure aggregation algorithm and provides no way out of the box way to run the actual system: it is expected that the user will use the package to implement the system according to their own needs. We provide examples how this is expected to be done for [client](benchmarking/client/run_client.py) and [server](benchmarking/client/run_server.py) side respectively.

To see our implementation in action you can run the following command in directory `benchmarking` (supported for Linux):
```bash
sh run.sh
```

Another option is to run:
```
python runtest.py
	[--epochs [number of epochs to train (default: 1)]]
	[--no-cuda]
	[--total [Total number of peers]]
	[--client-start-port [The client starting port (default: 6000)]]
	[--client-port-dif [Difference between ports of clients - they are allocated sequentally with the difference (default: 100)]]
	[--server-port [The server port (default: 5555)]]
	[--server-target-size [Total number of clients per aggregation (default: 6)]]
	[--server-group-size [Size of an aggregation group (default: 3)]]
	[--server-num-actors [Number of aggregation actors per aggregation group (default: 2)]]
	[--benchmark-server-port [The benchamrk server port (default: 5556)]]
	[--data-skip [Indicates the program to use only every n-th data sample for training (default: 25)]]
	[--debug]
```

Before running either of the commands you have to have package `recordtype` installed which can be done using the following command:
```bash
pip install recordtype
```

## Getting started

This implementation of the protocol aims at providing modular and easy to use interface for performing secure aggregation.
The first step is to create a helper server that peers would contact when they want to perform aggregation.
The class used for this is `hyperaggregate.server.privacy_preserving_server.SchedulingServer` and it accepts several parameters, such as port, an aggregation profile, the target number of peers in aggregation, as well as several parameters that parameterize how aggregation trees are generated (aggregation trees are an important concept for understanding how the protocol works, and you are therefore encouraged to take a look at [the report](https://infoscience.epfl.ch/record/286909) in order to better understand them).
Aggregation profiles are classes that define underlying aggregation specifics, e.g. how secrets are created and merged, how the data is transfered over network etc.
If you ware interested in creating your own aggregation profile check out the provided documentation.
We provide an already made implementation for aggregation profile used for averagging PyTorch state dictionaries.
It is available in class `hyperaggregate.aggregation_profiles.impl.torch_additive_sharing_model_profile.AverageTorchAdditiveSharingModelProfile`.
The aggregation starts only when the number of peers that have signed up for aggregation is equal to `target_size` parameter passed in the constructor.

Creating a server side code from here is simple:

```python
from hyperaggregate.server.privacy_preserving_server import SchedulingServer
from hyperaggregate.aggregation_profiles.impl.torch_additive_sharing_model_profile import \
    AverageTorchAdditiveSharingModelProfile

# Specifies logic for averaging PyTorch state dictionaries
agg_profile = AverageTorchAdditiveSharingModelProfile(DIGITS_TO_KEEP)
PORT = 6055
# Create server instance
server = SchedulingServer(
    PORT, target_size=6, group_size=3,
    num_actors=2, aggregation_profile=agg_profile)
#Start the server
server.start()
```

This will start helper server at the home address on port `6055`.


The code of peers is even simpler when we have the server ready and running, all it takes is to create an instance of class `hyperaggregate.client.privacy_preserving_aggregator.PrivacyPreservingAggregator`.
As parameters it accepts the address that the peer is running on and the address of the helper server.
Before calling a method `aggregate` that does aggregation in the synchronous way, we have to call method `start` which starts all the required receiver sockets essential for communication.

From here, the peer's code is as simple as:

```python
from hyperaggregate.client.privacy_preserving_aggregator import PrivacyPreservingAggregator

# Specify that peer runs at home address on port 8001
peer_address = 'tcp://127.0.0.1:8001'
# The previous code snippet start the server on port 6055 at home address
server_address = 'tcp://127.0.0.1:6055'
# Create peer side instance
aggregator = PrivacyPreservingAggregator(peer_address, args.sserver_addresserver)
# Start peer side receive sockets
aggregator.start()

# Initialize and train PyTorch model
pytorch_model = ...
...


# Does aggregation
# state dictionary passed to method aggregate must be on CPU
new_state_dict = aggregator.aggregate(pytorch_model.state_dict())
pytorch_model.load_state_dict(new_state_dict)

...
```

As we have passed `target_size` to be 6 on the server side, the aggregation while start only when 6 peers sign up for one.
