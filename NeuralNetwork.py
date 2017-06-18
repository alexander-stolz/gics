import numpy as np
from pylab import plot, grid, show, legend


class NN():
    def __init__(self, dimX, dimY, nodes=4):
        np.random.seed(1)

        # randomly initialize our weights with mean 0
        self.synapse_0 = 2. * np.random.random((dimX, nodes)) - 1.
        self.synapse_1 = 2. * np.random.random((nodes, dimY)) - 1.

    # compute sigmoid nonlinearity
    def sigmoid(self, x):
        output = 1. / (1. + np.exp(-x))
        return output

    # convert output of sigmoid function to its derivative
    def sigmoid_output_to_derivative(self, output):
        return output * (1. - output)

    def forward(self, x):
        layer_0 = x
        layer_1 = self.sigmoid(np.dot(layer_0, self.synapse_0))
        layer_2 = self.sigmoid(np.dot(layer_1, self.synapse_1))
        return layer_1, layer_2

    def scaleDown(self, X, Y, maxX=None, maxY=None):
        if not maxX:
            maxX = max(X)
        if not maxY:
            maxY = max(Y)
        self.scaleX, self.scaleY = 1. / maxX, 1. / maxY
        return X * self.scaleX, Y * self.scaleY

    def scaleDownX(self, X):
        return X * self.scaleX

    def scaleUp(self, x, y):
        return x / self.scaleX, y / self.scaleY

    def scaleUpY(self, y):
        return y / self.scaleY

    def guess(self, X):
        x = self.scaleDownX(X)
        y_hidden, y = self.forward(x)
        Y = self.scaleUpY(y)
        return Y

    def train(self, X, Y, n=1000, alpha=1., maxX=None, maxY=None, plot_errors=False):
        x, y = self.scaleDown(X, Y, maxX, maxY)

        for j in xrange(n):
            # Feed forward through layers 0, 1, and 2
            layer_1, layer_2 = self.forward(x)

            # how much did we miss the target value?
            layer_2_error = layer_2 - y

            # in what direction is the target value?
            # were we really sure? if so, don't change too much.
            layer_2_delta = layer_2_error * self.sigmoid_output_to_derivative(layer_2)

            # how much did each l1 value contribute to the l2 error (according to the weights)?
            layer_1_error = layer_2_delta.dot(self.synapse_1.T)

            # in what direction is the target l1?
            # were we really sure? if so, don't change too much.
            layer_1_delta = layer_1_error * self.sigmoid_output_to_derivative(layer_1)

            self.synapse_1 -= alpha * (layer_1.T.dot(layer_2_delta))
            self.synapse_0 -= alpha * (x.T.dot(layer_1_delta))
        print "Error: ", sum(abs(layer_2_error)) / self.scaleY / len(layer_2_error)

import random

X = np.array([[random.random(), random.random()] for x in range(1000)])
Y = np.array([[_[0] ** 2 + _[1] ** 2 for _ in X]]).T

N = NN(dimX=2, dimY=1, nodes=4)
N.train(X, Y, n=50000, alpha=.001, maxX=1., maxY=2.)
print N.guess(np.array([[.5, .5]]))
