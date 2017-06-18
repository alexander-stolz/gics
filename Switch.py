"""
Read switch for manual cracker control
"""


import serial
import time
import threading


class SwitchDevice(threading.Thread):
    switch = 0
    button = 0
    running = True
    sleeptime = .05

    def __init__(self, port="COM11"):
        threading.Thread.__init__(self)
        self.dev = serial.Serial(port)

    def run(self):
        while self.running:
            self.dev.write("1")
            time.sleep(self.sleeptime)
            try:
                ans = ""
                while self.dev.in_waiting:
                    ans += self.dev.read()
                self.switch = int(ans)
            except Exception, e:
                pass
            time.sleep(self.sleeptime)
            self.dev.write("2")
            time.sleep(self.sleeptime)
            try:
                ans = ""
                while self.dev.in_waiting:
                    ans += self.dev.read()
                self.button = int(ans)
            except Exception, e:
                pass
            time.sleep(self.sleeptime)
        self.close()

    def close(self):
        self.running = False
        time.sleep(.5)
        self.dev.close()
