#!/usr/bin/env python

import math
import random
from nott_params import *

num_samples = int(gridDim[0] * gridDim[1] * 10)
if num_samples < 10:
    num_samples = 10

def generateStimulus():
    stimulus = (random.randint(0, gridDim[0] - 1), random.randint(0, gridDim[1] - 1))
    return stimulus

def generateEyePositions():
    leye = (random.randint(0, gridDim[0] - 1), random.randint(0, gridDim[1] - 1))
    reye = (random.randint(0, gridDim[0] - 1), random.randint(0, gridDim[1] - 1))
    return (leye, reye)

def print_header():
    print("{0} {1} {2}".format(num_samples, num_inputs, num_outputs))

def print_input(left, right):
    data = left + right
    print(' '.join(data))

def scale(x, oldmin, oldmax, newmin, newmax):
    percent = float(x - oldmin) / float(oldmax - oldmin)
    return percent * (newmax - newmin) + newmin

def unitVec(v):
    length = math.sqrt(v[0] * v[0] + v[1] * v[1])
    return (v[0] / length, v[1] / length)

def calcDirection(source, target):
    return (target[0] - source[0], target[1] - source[1])

def print_sample():
    stimulus = generateStimulus()
    (leye, reye) = generateEyePositions()
    ldir = calcDirection(leye, stimulus)
    rdir = calcDirection(reye, stimulus)
    if ldir != (0, 0): ldir = unitVec(ldir)
    if rdir != (0, 0): rdir = unitVec(rdir)

    input = stimulus + leye + reye
    output = ldir + rdir

    print('%d %d %g %g %g %g' % input)
    print('%g %g %g %g' % output)

if __name__ == '__main__':
    random.seed()
    print_header()
    for i in range(num_samples):
        print_sample()
