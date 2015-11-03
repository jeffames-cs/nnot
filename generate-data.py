#!/usr/bin/env python

import random

input_x = 10
input_y = 10
num_samples = int(input_x * input_y * 0.1)
num_inputs = input_x + input_y
num_outputs = 4

def generate_data(numx, numy, args):
    data = []
    stimulus = (random.randint(0, numx), random.randint(0, numy))

    for i in range(numx):
        data.append([])
        for j in range(numy):
            if (i, j) == stimulus:
                data[i].append(1)
            else:
                data[i].append(0)

    return data, stimulus

def print_header():
    print("{0} {1} {2}".format(num_samples, num_inputs, num_outputs))

def print_input(left, right):
    data = left + right
    strData = []
    for row in data:
        rowStr = [str(elt) for elt in row]
        strData.append(' '.join(rowStr))
    print(' '.join(strData))

if __name__ == '__main__':
    import sys
    random.seed()
    print_header()
    for i in range(num_samples):
        data, stimulus = generate_data(input_x, input_y, sys.argv)
        print_input(data, data) # duplicate for two eyes
        scaled_x = 2 * float(stimulus[0]) / input_x - 1
        scaled_y = 2 * float(stimulus[1]) / input_y - 1
        print("{0} {1}".format(scaled_x, scaled_y))
        # TODO: map to [-1, 1]
