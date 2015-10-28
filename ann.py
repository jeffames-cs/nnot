#!/usr/bin/python

from pyfann import libfann

connection_rate = 1
learning_rate = 0.7
num_input = 200
num_hidden = 4
num_output = 4

desired_error = 0.0001
max_iterations = 100000
iterations_between_reports = 1000

# one test input value
input = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         1, 0, 0, 0, 0, 0, 0, 0, 0, 0,

         0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         0.1, 0, 0, 0, 0, 0, 0, 0, 0, 0]

def trainNet():
    ann = libfann.neural_net()
    ann.create_sparse_array(connection_rate, (num_input, num_hidden, num_output))
    ann.set_learning_rate(learning_rate)
    ann.set_activation_function_output(libfann.SIGMOID_SYMMETRIC_STEPWISE)
    ann.train_on_file("objtrack.data", max_iterations, iterations_between_reports, desired_error)
    ann.save("objtrack.net")

def testValue(inputs):
    ann = libfann.neural_net()
    ann.create_from_file("objtrack.net")
    return ann.run(inputs)

if __name__ == "__main__":
    trainNet()
    print(testValue(input))
