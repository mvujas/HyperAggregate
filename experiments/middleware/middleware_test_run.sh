#!/bin/bash
# This script requires gnome-terminal installed (available only on Linux)
# Another option to run the required commands is opening multiple command lines/terminals
#   and entering corresponding command in each (for each gnome-terminal command
#   there should be open a respective terminal)

ADDITIONAL_JAVASCRIPT_ARGUMENTS = ""

# Start aggregation server
gnome-terminal -t "Server" -x bash -c "python ../benchmarking/server/run_server.py --port 9998 --target-size 3 --group-size 3 --num-actors 2; read line"

# Create middleware server and client for each aggregation client. Aggregation
#   client code is run on middleware server
gnome-terminal -t "Middleware server 1" -x bash -c "python python-side/middleware_server.py --port 9997 --aggregation-client-port 9001 --aggregation-server-address 127.0.0.1:9998; read line"
gnome-terminal -t "Middleware client 1" -x bash -c "cd javascript-side/src; node client_test.js 9997 $ADDITIONAL_JAVASCRIPT_ARGUMENTS; read line"

gnome-terminal -t "Middleware server 2" -x bash -c "python python-side/middleware_server.py --port 9996 --aggregation-client-port 9002 --aggregation-server-address 127.0.0.1:9998; read line"
gnome-terminal -t "Middleware client 2" -x bash -c "cd javascript-side/src; node client_test.js 9996 $ADDITIONAL_JAVASCRIPT_ARGUMENTS; read line"

gnome-terminal -t "Middleware server 3" -x bash -c "python python-side/middleware_server.py --port 9995 --aggregation-client-port 9003 --aggregation-server-address 127.0.0.1:9998; read line"
gnome-terminal -t "Middleware client 3" -x bash -c "cd javascript-side/src; node client_test.js 9995 $ADDITIONAL_JAVASCRIPT_ARGUMENTS; read line"
