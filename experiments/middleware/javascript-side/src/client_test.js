const { Client } = require('./IntecommunicationClient');
const { serializeWeights, assignWeightsToModel, sleep } = require('./helpers');

const tf = require('@tensorflow/tfjs');

// Optional Load the binding:
// Use '@tensorflow/tfjs-node-gpu' if running with GPU.
require('@tensorflow/tfjs-node');

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
        'modelReceived': modelMessage => {
          console.log('Got model for epoch: ' + (counter.modelCounter + 1));
          // Load the aggregated model into local model
          assignWeightsToModel(modelMessage, model);
          // Evaluate metrics on the training dataset
          model.evaluate(x, y).print();
          // Notify outside world that the aggregated model is received
          counter.modelCounter++;
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
}

train(model, xs, ys, 10);
