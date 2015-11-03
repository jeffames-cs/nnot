#!/usr/bin/env python

from pyfann import libfann

connection_rate = 1
learning_rate = 0.7
num_input = 200
num_hidden = 4
num_output = 4

desired_error = 0.0001
max_iterations = 100000
iterations_between_reports = 1000

nn_file = "objtrack.net"

def trainNet():
    ann = libfann.neural_net()
    ann.create_sparse_array(connection_rate, (num_input, num_hidden, num_output))
    ann.set_learning_rate(learning_rate)
    ann.set_activation_function_output(libfann.SIGMOID_SYMMETRIC_STEPWISE)
    ann.train_on_file("training.data", max_iterations, iterations_between_reports, desired_error)
    ann.save(nn_file)

def testValue(inputs):
    ann = libfann.neural_net()
    ann.create_from_file(nn_file)
    return ann.run(inputs)

def testNet():
    data = libfann.training_data()
    data.read_train_from_file("testing.data");

    ann = libfann.neural_net()
    ann.create_from_file(nn_file)

    ann.reset_MSE()
    ann.test_data(data)
    print("Mean Square Error: {0}".format(ann.get_MSE()));

if __name__ == "__main__":
    trainNet()
    testNet()
