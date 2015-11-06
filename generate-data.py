#!/usr/bin/env python

import random
from nott_params import *

num_samples = int(gridDim[0] * gridDim[1] * 10)

def generate_data(numx, numy):
    ldata = ['0' for i in range(numx * numy)]
    rdata = ['0' for i in range(numx * numy)]
    stimulus = (random.randint(0, numx - 1), random.randint(0, numy - 1))
    ldata[stimulus[1] * numx + stimulus[0]] = '1'
    rdata[stimulus[1] * numx + stimulus[0]] = '1'
    return ldata, rdata, stimulus

def print_header():
    print("{0} {1} {2}".format(num_samples, num_inputs, num_outputs))

def print_input(left, right):
    data = left + right
    print(' '.join(data))

if __name__ == '__main__':
    random.seed()
    print_header()
    for i in range(num_samples):
        ldata, rdata, stimulus = generate_data(gridDim[0], gridDim[1])
        print_input(ldata, rdata)
        scaled_x = 2 * float(stimulus[0]) / gridDim[0] - 1
        scaled_y = 2 * float(stimulus[1]) / gridDim[1] - 1
        print("{0} {1} {2} {3}".format(scaled_x, scaled_y,
                                       scaled_x, scaled_y))
