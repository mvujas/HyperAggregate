#!/bin/bash

SERVER_PORT=5554
BASE_CLIENT_PORT=10600
NUM_CLIENTS=4
NUM_EPOCHS=1

# Start server
gnome-terminal -t "Server" -x bash -c "python server/server.py --port $SERVER_PORT; read line"

# Wait a little bit to make sure the server is ready and running
sleep 1

SERVER_ADDRESS=127.0.0.1:$SERVER_PORT
# Start NUM_CLIENTS peers
for i in `seq 0 $(($NUM_CLIENTS-1))`
do
  # Clients take port sequentially starting from BASE_CLIENT_PORT
  CLIENT_PORT=$(($BASE_CLIENT_PORT+$i))
  CLIENT_ADDRESS=127.0.0.1:$CLIENT_PORT
  gnome-terminal -t "Client $i" -x bash -c \
    "python client/privacy_preserving_client.py --server $SERVER_ADDRESS \
      --client $CLIENT_ADDRESS --num $i --total $NUM_CLIENTS \
      --epochs $NUM_EPOCHS; read line"
done
