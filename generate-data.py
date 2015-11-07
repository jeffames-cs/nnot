#!/usr/bin/env python

import random
from nott_params import *

num_samples = int(gridDim[0] * gridDim[1] * 0.2)
if num_samples < 10:
    num_samples = 10

def generateStimulus(maxx, maxy):
    stimulus = (random.randint(0, maxx - 1), random.randint(0, maxy - 1))
    return stimulus

def print_header():
    print("{0} {1} {2}".format(num_samples, num_inputs, num_outputs))

def print_input(left, right):
    data = left + right
    print(' '.join(data))

def scale(x, oldmin, oldmax, newmin, newmax):
    percent = float(x - oldmin) / float(oldmax - oldmin)
    return percent * (newmax - newmin) + newmin

def print_sample():
    input = generateStimulus(gridDim[0], gridDim[1])
    output = (scale(input[0], 0, gridDim[0], -1, 1),
              scale(input[1], 0, gridDim[1], -1, 1),
              scale(input[0], 0, gridDim[0], -1, 1),
              scale(input[1], 0, gridDim[1], -1, 1))
    print('%d %d' % input)
    print('%g %g %g %g' % output)

if __name__ == '__main__':
    random.seed()
    print_header()
    for i in range(num_samples):
        print_sample()
