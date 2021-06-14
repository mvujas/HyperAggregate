# HyperAggregate: A sublinear aggregation algorithm implementation

Implementation of in-house secure aggregation protocol.

The documentation can be accessed by opening `protocol_prototype/docs/_build/html/index.html` in browser.

## Installation

The package is available in directory protocol_prototype. It requires Python version `>= 3.6`. It can be installed by running the following in the root of the project:
```bash
pip install protocol_prototype
```
This command will install the package and all required dependencies.

The package is only the secure aggregation algorithm and provides no out of the box way to run the actual system: it is expected that the user will use the package to implement the system according to their own needs. We provide examples how this is expected to be done for [client](experiments/benchmarking/client/run_client.py) and [server](experiments/benchmarking/client/run_server.py) side respectively.

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
