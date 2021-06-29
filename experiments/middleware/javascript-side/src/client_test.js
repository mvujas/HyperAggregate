const { Client } = require('./IntecommunicationClient');
const { serializeWeights, assignWeightsToModel, sleep } = require('./helpers');

const tf = require('@tensorflow/tfjs');

// Optional Load the binding:
// Use '@tensorflow/tfjs-node-gpu' if running with GPU.
require('@tensorflow/tfjs-node');

// Helper functions
  // Return the last element of an array
Array.prototype.last = function() {
  return this[this.length - 1];
};
  // Return the mean of an array
Array.prototype.mean = function() {
  return this.reduce((a, b) => a + b, 0) / this.length;
}

// Get command line arguments
const args = process.argv.slice(2);



// Create a model and prepare it for training
const model = tf.sequential();
model.add(tf.layers.dense({units: 100, activation: 'relu', inputShape: [2]}));
model.add(tf.layers.dense({units: 1, activation: 'linear'}));
model.compile({optimizer: 'sgd', loss: 'meanSquaredError'});

// Create data used for both training and evaluation
const USE_RANDOM_DATA = args.includes('--random-data');
const xs = USE_RANDOM_DATA ? tf.randomNormal([100, 2]) : tf.tensor([
                                                              [1, 2],
                                                              [3, 4]
                                                            ]);
const ys = USE_RANDOM_DATA ? tf.randomNormal([100, 1]) : tf.tensor([1, 2]);

const times = {
  'aggregation_times': [],
  'sign_up_to_aggregation_end_times': [],
  'full_times': [],
  'message_to_server_times': [],
  'message_from_server_times': []
};

async function train(model, x, y, epochs) {
  // counter works as a mutable integer, so that it can be passed in lambda
  //  and changes are visible outside
  const counter = {
    modelCounter: -1
  };
  // Create client
  const client = new Client(
    args[0],
    {
        'modelReceived': message => {
          console.log('Got model for epoch: ' + (counter.modelCounter + 1));
          const modelMessage = message['model'];
          // Load the aggregated model into local model
          assignWeightsToModel(modelMessage, model);
          // Evaluate metrics on the training dataset
          model.evaluate(x, y).print();
          // Notify outside world that the aggregated model is received
          counter.modelCounter++;

          // Time statistics
          const now = +new Date;
          times['aggregation_times'].push(message['aggregation_time']);
          times['sign_up_to_aggregation_end_times'].push(
            message['sign_up_to_aggregation_end_time'] / 1000);
          times['full_times'].push((now - message['callTime']) / 1000);
          times['message_to_server_times'].push(
            message['time_until_receive'] / 1000);
          times['message_from_server_times'].push(
            (now - message['time_of_sending_back']) / 1000);
          console.log(`\
Time statistics
===============
Aggregation time: ${times['aggregation_times'].last()}
Sign up to aggregation end time: ${times['sign_up_to_aggregation_end_times'].last()}
Full time of call: ${times['full_times'].last()}
Message to server time: ${times['message_to_server_times'].last()}
Message from server time: ${times['message_from_server_times'].last()}
===============`);
        }
    }
  );
  // Train for specified number of epochs
  for(let i = 0; i < epochs; i++) {
    // Train by going once over the training set
    await model.fit(x, y);

    // Send aggregation request with the model
    await client.averageModel(model);

    // Workaround to wait for receiving the aggregated model
    while(counter.modelCounter < i) {
      await sleep(5);
    }
  }
  await sleep(1000);

  console.log(`
Mean time statistics
===============
Aggregation time: ${times['aggregation_times'].mean()}
Sign up to aggregation end time: ${times['sign_up_to_aggregation_end_times'].mean()}
Full time of call: ${times['full_times'].mean()}
Message to server time: ${times['message_to_server_times'].mean()}
Message from server time: ${times['message_from_server_times'].mean()}
===============`);
}

train(model, xs, ys, 10);
