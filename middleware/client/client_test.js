const { Client } = require('./IntecommunicationClient');
const { serializeWeights, assignWeightsToModel, sleep } = require('./helpers');


const tf = require('@tensorflow/tfjs');

// Optional Load the binding:
// Use '@tensorflow/tfjs-node-gpu' if running with GPU.
require('@tensorflow/tfjs-node');



// Train a simple model:
const model = tf.sequential();
model.add(tf.layers.dense({units: 100, activation: 'relu', inputShape: [2]}));
model.add(tf.layers.dense({units: 1, activation: 'linear'}));
model.compile({optimizer: 'sgd', loss: 'meanSquaredError'});

// const xs = tf.randomNormal([100, 10]);
// const ys = tf.randomNormal([100, 1]);
const xs = tf.tensor([
  [1, 2],
  [3, 4]
])
const ys = tf.tensor([1, 2])


async function train(model, x, y, epochs) {
  const client = new Client(
    process.argv[2],
    {
        'modelReceived': modelMessage => {
          console.log('Got model');
          assignWeightsToModel(modelMessage, model);
          model.evaluate(x, y).print();
          // for (let i = 0; i < model.getWeights().length; i++) {
          //   console.log(model.getWeights()[i].dataSync());
          // }

          // model.predict(x).print()
        }
    }
  );
  for(let i = 0; i < epochs; i++) {
    await model.fit(x, y);

    await client.averageModel(model);

    await sleep(1000)
  }
}

train(model, xs, ys, 10);
