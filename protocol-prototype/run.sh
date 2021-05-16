#!/bin/bash
#
# SERVER_PORT=5554
# BASE_CLIENT_PORT=10600
# NUM_CLIENTS=6
# NUM_EPOCHS=3
# DEBUG=1
# SUFFIX=""
# #_old
#
# # Start server
# gnome-terminal -t "Server" -x bash -c "python server/server$SUFFIX.py --port $SERVER_PORT; read line"
#
# # Wait a little bit to make sure the server is ready and running
# sleep 1
#
# SERVER_ADDRESS=127.0.0.1:$SERVER_PORT
# # Start NUM_CLIENTS peers
# for i in `seq 0 $(($NUM_CLIENTS-1))`
# do
#   # Clients take port sequentially starting from BASE_CLIENT_PORT
#   CLIENT_PORT=$(($BASE_CLIENT_PORT+100*$i))
#   CLIENT_ADDRESS=127.0.0.1:$CLIENT_PORT
#   case "$DEBUG" in
#    0) DEBUG_SEQ="" ;;
#    *) DEBUG_SEQ="--debug" ;;
#   esac
#   gnome-terminal -t "Client $i" -x bash -c \
#     "python client/privacy_preserving_client$SUFFIX.py --server $SERVER_ADDRESS \
#       --client $CLIENT_ADDRESS --num $i --total $NUM_CLIENTS \
#       --epochs $NUM_EPOCHS $DEBUG_SEQ; read line"
# done

python runtest.py --debug --server-port 9002 --client-start-port 3000 --data-skip 200 --server-target-size 4 --total 4
