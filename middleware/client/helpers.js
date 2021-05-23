// Taken from: https://github.com/epfml/DeAI/blob/master/experiments/peerjs/helpers.js
const tf = require('@tensorflow/tfjs');

async function serializeTensor(tensor) {
    return {
        "$tensor": {
            "data": await tensor.data(), // doesn't copy (maybe depending on runtime)!
            "shape": tensor.shape,
            "dtype": tensor.dtype
        }
    }
}
function deserializeTensor(dict) {
    const {data, shape, dtype} = dict["$tensor"];
    return tf.tensor(data, shape, dtype); // doesn't copy (maybe depending on runtime)!
}
async function serializeVariable(variable) {
    return {
        "$variable": {
            "name": variable.name,
            "val": await serializeTensor(variable.val),
        }
    }
}

async function serializeWeights(model) {
    return await Promise.all(model.weights.map(serializeVariable));
}

function assignWeightsToModel(serializedWeights, model) {
    // This assumes the weights are in the right order
    model.weights.forEach((weight, idx) => {
        const serializedWeight = serializedWeights[idx]["$variable"];
        const tensor = deserializeTensor(serializedWeight.val);
        weight.val.assign(tensor);
        tensor.dispose();
    });
}

function averageWeightsIntoModel(serializedWeights, model) {
    model.weights.forEach((weight, idx) => {
        const serializedWeight = serializedWeights[idx]["$variable"];

        const tensor = deserializeTensor(serializedWeight.val);
        weight.val.assign(tensor.add(weight.val).div(2)); //average
        tensor.dispose();
    });
}

//////////// TESTING functions - generate random data and labels
function* dataGenerator() {
    for (let i = 0; i < 100; i++) {
        // Generate one sample at a time.
        yield tf.randomNormal([784]);
    }
}

function* labelGenerator() {
    for (let i = 0; i < 100; i++) {
        // Generate one sample at a time.
        yield tf.randomUniform([10]);
    }
}
///////////////////////////////////////////////

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}


/**
 * Wait to receive data by checking if recv_buffer.key is defined
 * @param {Object} recv_buffer
 * @param {*} key
 */
function data_received(recv_buffer, key) {
    return new Promise( (resolve) => {
        (function wait_data(){
            if (recv_buffer[key]) {
                return resolve();
            }
            setTimeout(wait_data, 100);
        })();
    });
}

/**
 * Same as data_received, but break after max_tries
 * @param {Object} recv_buffer
 * @param {*} key
 * @param {int} max_tries
 */
function data_received_break(recv_buffer, key, max_tries) {
    return new Promise( (resolve) => {
        (function wait_data(n){
            if (recv_buffer[key] || n >= max_tries - 1) {
                return resolve();
            }
            setTimeout(() => wait_data(n+1), 100);
        })(0);
    });
}


/**
 * Waits until an array reaches a given length. Used to make
 * sure that all weights from peers are received.
 * @param {Array} arr
 * @param {int} len
 */
function check_array_len(arr, len) {
    return new Promise( (resolve) => {
        (function wait_data(){
            if (arr.length >= len) {
                return resolve();
            }
            setTimeout(wait_data, 100);
        })();
    });
}

// generates a random string
function makeid(length) {
    var result           = '';
    var characters       = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    var charactersLength = characters.length;
    for ( var i = 0; i < length; i++ ) {
       result += characters.charAt(Math.floor(Math.random() * charactersLength));
    }
    return result;
 }

// train on Mnist
 async function train_common(model, model_compile_data, model_train_data, onEpochBegin, onEpochEnd) {
    const mnist = new MnistData()
    await mnist.load()
    const [x_train_2d, y_train_2d] = mnist.getTrainData()
    const x_train_1d_ord = tf.reshape(x_train_2d, [x_train_2d.shape[0], -1])
    const y_train_1d_ord = tf.reshape(y_train_2d, [y_train_2d.shape[0], -1])

    // shuffle to avoid having the same thing on all peers
    var indices = tf.linspace(0, x_train_1d_ord.shape[0]).cast('int32')
    tf.util.shuffle(indices)
    const x_train_1d = x_train_1d_ord.gather(indices)
    const y_train_1d = y_train_1d_ord.gather(indices)


    model.compile(model_compile_data)
    console.log("Training started")
    await model.fit(x_train_1d, y_train_1d, {
      epochs : model_train_data.epochs,
      batchSize: 50,
      callbacks : {onEpochBegin, onEpochEnd}
    }).then( (info) => console.log("Training finished", info.history) )
  }

/**
 * Sends weights to all peers, waits to receive weights from all peers
 * and then averages peers' weights into the model.
*/
async function onEpochEnd_Sync(model, epoch, receivers, recv_buffer) {
    const serialized_weights = await serializeWeights(model)
    const epoch_weights = {epoch : epoch, weights : serialized_weights}

    for (var i in receivers) {
      console.log("Sending weights to: ", receivers[i])
      await send_data(epoch_weights, CMD_CODES.AVG_WEIGHTS, peerjs, receivers[i])
    }

    if (recv_buffer.avg_weights === undefined) {
      console.log("Waiting to receive weights...")
      await data_received(recv_buffer, "avg_weights")
    }
    if (recv_buffer.avg_weights[epoch] === undefined) {
      console.log("Waiting to receive weights for this epoch...")
      await data_received(recv_buffer.avg_weights, epoch.toString())
    }
    console.log("Waiting to receive all weights for this epoch...")
    await check_array_len(recv_buffer.avg_weights[epoch], receivers.length)
      .then(() => {
        console.log("Averaging weights")
        for(i in recv_buffer.avg_weights[epoch]) {
          averageWeightsIntoModel(recv_buffer.avg_weights[epoch][i], model)
        }
        // might want to delete weights after using them to avoiding hogging memory
        // delete recv_buffer.avg_weights[epoch]
      })
  }

/**
 * Request weights from peers, carry on if the number of received weights is
 * greater than the provided threshold
*/
async function onEpochEnd_common(model, epoch, receivers, recv_buffer, username, threshold) {

    const serialized_weights = await serializeWeights(model)
    const epoch_weights = {epoch : epoch, weights : serialized_weights}

    // request weights and send to all who requested
    for (var i in receivers) {
        await send_data({name : username}, CMD_CODES.WEIGHT_REQUEST, peerjs, receivers[i])

        if (recv_buffer.weight_requests !== undefined && recv_buffer.weight_requests.has(receivers[i])) {
            console.log("Sending weights to: ", receivers[i])
            await send_data(epoch_weights, CMD_CODES.AVG_WEIGHTS, peerjs, receivers[i])
        }
    }
    if (recv_buffer.weight_requests !== undefined) {
        recv_buffer.weight_requests.clear()
    }

    if (recv_buffer.avg_weights === undefined) {
      console.log("Waiting to receive weights...")
      await data_received_break(recv_buffer, "avg_weights", 100) // timeout to avoid deadlock (10s)
    }

    if (recv_buffer.avg_weights !== undefined) { // check if any weights were received
        console.log("Waiting to receive enough weights...")
        await check_array_len(Object.values(recv_buffer.avg_weights).flat(1), threshold)
        .then(() => {
            console.log("Averaging weights")
            Object.values(recv_buffer.avg_weights).flat(1).forEach(
                (w) => { averageWeightsIntoModel(w, model) }
            )
            delete recv_buffer.avg_weights // NOTE: this might delete useful weights...
        })
    }


    // change data handler for future requests if this is the last epoch
    if (epoch == recv_buffer.train_info.epochs) {
        end_buffer = epoch_weights
        end_buffer.peerjs = peerjs
        peerjs.set_data_handler(handle_data_end, end_buffer)
    }
  }

module.exports = {
  serializeWeights: serializeWeights,
  assignWeightsToModel: assignWeightsToModel,
  sleep: sleep
}
