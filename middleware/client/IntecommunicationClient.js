const net = require('net');
const { serializeWeights } = require('./helpers')

/**
 *  Provides communication interface for client side of middleware.
 *  The idea is to use this class to make requests to the server on the other
 *    side of the midleware. The server would run secure aggregation algorithm
 *    over network with other peers and relay requests of this client.
 *  Both server and client should run on the same machine.
 */
class IntercommunicationClient {
  constructor(serverPort, callbacks = {}) {
    this.socket = net.Socket();
    this.connected = false;
    this.callbacks = callbacks;
    this.socket.connect(
      serverPort,
      '127.0.0.1',
      this.handleConnectionSuccess.bind(this)
    );
    this.socket.on('error', error => {
      console.log('Error : ' + error);
    });
    this.socket.on('data', this.handleReceivedModel.bind(this));
  }

  close() {
    this.socket.destroy();
  }

  handleConnectionSuccess() {
    this.connected = true;
  }

  async averageModel(model) {
    if(this.connected) {
      console.log('Sending request');
      const serializedModel = JSON.stringify(await serializeWeights(model));
      this.socket.write(serializedModel);
    }
    else {
      console.log('Must be connected to average model');
    }
  }

  handleReceivedModel(modelMessage) {
    const modelMessageObject = JSON.parse(modelMessage);
    const callbackName = 'modelReceived';
    if(callbackName in this.callbacks) {
      this.callbacks[callbackName](modelMessageObject);
    }
  }
}

module.exports = {
  Client: IntercommunicationClient
}
