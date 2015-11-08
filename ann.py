#!/usr/bin/env python

from pyfann import libfann
from nott_params import *

connection_rate = 1
learning_rate   = 0.7
num_hidden      = max(5, min(100, (gridDim[0] + gridDim[1]) / 2))

desired_error              = 0.0005
max_iterations             = 100000
iterations_between_reports = 200

nn_file    = "objtrack.net"
train_file = "training.data"
test_file  = "testing.data"

def trainNet():
    ann = libfann.neural_net()
    ann.create_sparse_array(connection_rate, (num_inputs, num_hidden, num_outputs))
    ann.set_learning_rate(learning_rate)
    ann.set_activation_function_output(libfann.SIGMOID_SYMMETRIC)
    ann.train_on_file(train_file, max_iterations, iterations_between_reports, desired_error)
    ann.save(nn_file)

def testValue(inputs):
    ann = libfann.neural_net()
    ann.create_from_file(nn_file)
    return ann.run(inputs)

def testNet():
    data = libfann.training_data()
    data.read_train_from_file(test_file);

    ann = libfann.neural_net()
    ann.create_from_file(nn_file)

    ann.reset_MSE()
    ann.test_data(data)
    print("Mean square error: {0}".format(ann.get_MSE()));

if __name__ == "__main__":
    trainNet()
    testNet()
