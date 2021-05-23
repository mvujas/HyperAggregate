#!/bin/bash
gnome-terminal -t "Server" -x bash -c "python protocol-prototype/run_server.py --port 9998 --target-size 3 --group-size 3 --num-actors 2; read line"
gnome-terminal -t "Middleware server 1" -x bash -c "python protocol-prototype/middleware_server.py --port 9997 --aggregation-client-port 9001 --aggregation-server-address 127.0.0.1:9998; read line"
gnome-terminal -t "Middleware server 2" -x bash -c "python protocol-prototype/middleware_server.py --port 9996 --aggregation-client-port 9002 --aggregation-server-address 127.0.0.1:9998; read line"
gnome-terminal -t "Middleware server 3" -x bash -c "python protocol-prototype/middleware_server.py --port 9995 --aggregation-client-port 9003 --aggregation-server-address 127.0.0.1:9998; read line"

gnome-terminal -t "Middleware client 1" -x bash -c "node middleware/client/client_test.js 9997; read line"
gnome-terminal -t "Middleware client 2" -x bash -c "node middleware/client/client_test.js 9996; read line"
gnome-terminal -t "Middleware client 3" -x bash -c "node middleware/client/client_test.js 9995; read line"
