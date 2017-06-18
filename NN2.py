from pybrain.tools.shortcuts import buildNetwork
from pybrain.datasets import SupervisedDataSet
from pybrain.supervised.trainers import BackpropTrainer
from pybrain.tools.customxml.networkwriter import NetworkWriter
from pybrain.tools.customxml.networkreader import NetworkReader
import random
import pickle
from numpy import array
import threading
import re
import time


class NN(threading.Thread):
    stop = True
    skipped = False
    skiplen = 5000

    def __init__(self, dimX=None, nodes=3, filename=None):
        threading.Thread.__init__(self)

        self.nodes = nodes
        self.dimX = dimX

        if not dimX:
            self.dimX = 2
            # mischung, gasfluss
            self.setXRanges(xRanges=[.2, 5.])
        self.setYRange(yRange=.2)

        self.filename = filename

        if filename:
            print "try loading neural net",
            try:
                self.load(filename)
                print "\r%s loaded. dimX = %i" % (filename, self.dimX)
            except:
                print "net not found. creating new one."
                self.createNewNet()
        else:
            try:
                self.load(load_trainingdata=True)
            except:
                print "create new net..",
                self.createNewNet()
                print "\rnew net created."

    def createNewNet(self):
        self.net = buildNetwork(self.dimX, self.nodes, 1)
        self.ds = SupervisedDataSet(self.dimX, 1)
        self.trainer = BackpropTrainer(self.net, self.ds)

    def setXRanges(self, xRanges):
        self.xRanges = array(xRanges)

    def setYRange(self, yRange):
        self.yRange = yRange

    def scaleDownX(self, x):
        return array(x) / self.xRanges

    def scaleDownY(self, y):
        return array(y) / self.yRange

    def scaleUpY(self, y):
        return y * self.yRange

    def addSample(self, x, y):
        self.ds.addSample(self.scaleDownX(x), self.scaleDownY(y))

    def guess(self, x):
        x = self.scaleDownX(x)
        return self.scaleUpY(self.net.activate(x))[0]

    def train(self, n=100000, maxtime=240):
        print "training network. n = %i ; maxtime = %i s" % (n, maxtime)
        self.stop = False
        t0 = time.clock()
        for i in xrange(n):
            if (self.stop) or (time.clock() - t0 > maxtime):
                break
            e = self.trainer.train()
        print "training paused. current error: %f ; %i cycles ; %i datapoints" % (e, i, len(self.ds))
        return e

    def load(self, filename="brain.xml", load_trainingdata=False):
        self.net = NetworkReader.readFrom(filename)
        if load_trainingdata:
            ds = pickle.load(open("trainingdata", "rb"))
            datalen = len(ds)
            if datalen > self.skiplen:
                self.dataset = ds
                self.skipped = True
                self.ds = SupervisedDataSet(self.dimX, 1)
                for i in xrange(self.skiplen):
                    index = random.randrange(datalen)
                    self.ds.addSample(ds["input"][index], ds["target"][index])
            else:
                self.ds = ds

        else:
            self.ds = SupervisedDataSet(self.dimX, 1)
        self.trainer = BackpropTrainer(self.net, self.ds)

    def save(self):
        if not self.filename:
            filename = "brain.xml"
        NetworkWriter.writeToFile(self.net, filename)
        if not self.skipped:
            pickle.dump(self.ds, open("trainingdata", "wb"))
        else:
            ds = SupervisedDataSet(self.dimX, 1)
            for inp, tar in self.dataset:
                ds.addSample(inp, tar)
            for i, (inp, tar) in enumerate(self.ds):
                if i > self.skiplen:
                    ds.append(inp, tar)
            pickle.dump(ds, open("trainingdata", "wb"))

    def addMeasurementFile(self, filename):
        try:
            data = open(filename, "r").read()
            pattern = "^\[mix\](.*)\n"
            mixture = float(re.search(pattern, data).groups()[0])
            pattern = "\[c flow vs efficiency\]\n(.*)\n(.*)"
            flow = map(float, re.search(pattern, data).groups()[0].split())   # FEHLER: GASFLUSS!!
            efficiency = map(float, re.search(pattern, data).groups()[1].split())
            for f, e in zip(flow, efficiency):
                print "adding: (%f, %f) -> (%f)" % (mixture, f, e / 100.)
                self.addSample((mixture, f), (e / 100.,))
        except Exception, e:
            print e


def test():
    nn = NN()
    import random
    nn.setXRanges([1., 1.])
    nn.setYRange(1.)
    for i in xrange(1000):
        a = random.random()
        b = random.random()
        c = a + b
        nn.addSample([a, b], [c])
    for i in range(50):
        print "\r", i, nn.train(n=1),
        print nn.guess([.2, .6]), nn.guess([.3, .2]),
    nn.save()


def test2():
    nn = NN()
    nn.addMeasurementFile("measurements/20161216_269.txt")
    print nn.train()
