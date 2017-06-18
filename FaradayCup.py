"""
The LE 12C current is read out continuously and saved into self.current.

self.ams = True:
    get current from tcp/ip connection (hve ams software)
self.ams = False:
    get current from FC -> keithley -> arduino

if no connection can be established, a sin-shaped current is simulated (for testing purposes)
"""

import serial    # for arduino communication ; default port = COM11
import socket    # for tcp/ip communication ; default port = 50001 ; ip = 192.168.0.1
import time
import threading
from math import sin    # for virtual device


# channels
NE13 = 143
NE12 = 144
HE13 = 145
HE12 = 146

SCALE_NE12 = 1e-6                                                                                   # Skalierungsfaktor abhaengig von Offsetcup Range
SCALE_NE13 = 10e-9                                                                                  # Skalierungsfaktor abhaengig von Offsetcup Range
SCALE_HE12 = 1e-6                                                                                   # Skalierungsfaktor abhaengig von Offsetcup Range
SCALE_HE13 = 10e-9                                                                                  # Skalierungsfaktor abhaengig von Offsetcup Range


class FcDevice(threading.Thread):
    ams = False
    measure = True
    refresh = True
    running = True
    current = 0.
    he12_current = 1.
    he13current = 0.
    region  = 1e-6

    def __init__(self, ams=True, ip="192.168.0.1", port=50001, buffersize=1024):
        threading.Thread.__init__(self)
        self.ams = ams
        self.buffersize = buffersize
        try:
            if ams:
                self.dev = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.dev.connect((ip, port))
            else:
                self.dev = serial.Serial(port)
        except Exception, e:
            print e
            print "Could not connect to Faraday Cup. Using Virtual Device."
            self.dev = None
            self.measure = False

    def run(self):
        while self.running:
            if (self.measure):
                if (self.refresh):
                    self.getCurrent()
                    self.refresh = False
            else:
                self.current = 6e-6 * (1. + .5 * sin(time.clock() / 3.))
                self.he12_current = 6e-6 * (1. + .5 * sin(time.clock() / 3.))
                self.he13current = 6e-9 * (1. + .5 * sin(time.clock() / 3.000001))
            time.sleep(.2)

    def getCurrent(self):
        if self.ams:
            self.dev.send("getAnalog %i\r\n" % (NE12))
            try:
                self.current = float(self.dev.recv(self.buffersize)) * SCALE_NE12
            except Exception, e:
                print e
            self.dev.send("getAnalog %i\r\n" % (HE12))
            try:
                self.he12_current = float(self.dev.recv(self.buffersize)) * SCALE_HE12
            except Exception, e:
                print e
            self.dev.send("getAnalog %i\r\n" % (HE13))
            try:
                self.he13current = float(self.dev.recv(self.buffersize)) * SCALE_HE13
            except Exception, e:
                print e
            if self.current == 0.:
                self.current = self.he12_current / 2.
        else:
            self.dev.write("1")
            time.sleep(.2)
            ans = ""
            while self.dev.in_waiting:
                ans += self.dev.read()
            try:
                self.current = self.convertCurrent(float(ans.strip()))
            except:
                pass

    def convertCurrent(self, voltage):
        answer = voltage * self.region
        return answer

    def close(self):
        self.running = False
        time.sleep(.5)
        if self.dev:
            if self.ams:
                self.dev.send("close\r\n")
            self.dev.close()

