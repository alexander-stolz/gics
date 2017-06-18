import socket
import time

IP = "192.168.0.1"
PORT = 50001
BUFFER_SIZE = 1024

# GET Channels
LEOFC1 = LE13 = 143                                                                                 # getAnalog
LEOFC2 = LE12 = 144                                                                                 # getAnalog
HEOFC1 = HE13 = 145                                                                                 # getAnalog
HEOFC2 = HE12 = 146                                                                                 # getAnalog
GETDATA_TARGET_VOLTAGE = 15 * 8 + 2 + 128                                                                        # getData ; _ / 342.5
GETDATA_EXTRACTION_VOLTAGE = 15 * 8 + 0 + 128
GETDATA_CS_RESERVOIR = 16 * 8 + 0 + 128                                                                              #

# SET Channels
SET_TARGET_VOLTAGE = 11                                                                             # setAnalog <kV>
SET_EXTRACTION_VOLTAGE = 14                                                                         # setAnalog <kV>
SET_CS_RESERVOIR = 13                                                                               # setAnalog <Celsius>


class AmsDevice():
    """ TCP/IP Client for AMS Communication """
    dev = None
    buffer_size = None
    factors_target = 1. / 342.5, 0.
    factors_extraction = None, None

    def __init__(self, ip=IP, port=PORT, buffer_size=BUFFER_SIZE):
        # print ip, port, buffer_size
        self.dev = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # print "connecting",
        self.dev.connect((ip, port))
        # print "\rconnected."
        self.buffer_size = buffer_size
        self.calibrate_target_voltage()
        self.calibrate_extraction_voltage()

    def send(self, message):
        self.dev.send(message + "\r\n")

    def receive(self):
        ans = self.dev.recv(self.buffer_size)
        return ans

    def request(self, *args):
        request = " ".join(map(str, args))
        # print "request: ", request
        self.send(request)
        return self.receive()

    def close(self):
        self.send("close")
        self.dev.close()

    def getChannel(self, channel):
        return self.request("getAnalog", channel)

    def setChannel(self, channel, value):
        self.request("setAnalog %i %f" % (channel, value))

    def add(self, a, b):
        print self.request("add", a, b)

    def load_target(self, pos):
        print "load target"
        print self.request("src2LoadSample", int(pos))

    def set_cs_temperature(self, temp):
        self.setChannel(SET_CS_RESERVOIR, temp)

    def set_target_voltage(self, voltage):
        self.setChannel(SET_TARGET_VOLTAGE, voltage)

    def set_extraction_voltage(self, voltage):
        self.setChannel(SET_EXTRACTION_VOLTAGE, voltage)

    def get_extraction_voltage(self):
        for i in range(3):
            try:
                ans = self.request("getData", GETDATA_EXTRACTION_VOLTAGE)
                return float(ans) * self.factors_extraction[0] + self.factors_extraction[1]
                break
            except Exception, e:
                print e
        return -1

    def get_target_voltage(self):
        for i in range(3):
            try:
                ans = self.request("getData", GETDATA_TARGET_VOLTAGE)
                return float(ans) * self.factors_target[0] + self.factors_target[1]
                break
            except Exception, e:
                print e
        return -1

    def getLeOffsetcup1(self):                                                                      # muss noch skaliert werden (FaradayCup.py)
        return self.getChannel(LEOFC1)

    def getLeOffsetcup2(self):                                                                      # muss noch skaliert werden (FaradayCup.py)
        return self.getChannel(LEOFC2)

    def getHeOffsetcup1(self):                                                                      # muss noch skaliert werden (FaradayCup.py)
        return self.getChannel(HEOFC1)

    def getHeOffsetcup2(self):                                                                      # muss noch skaliert werden (FaradayCup.py)
        return self.getChannel(HEOFC2)

    def get_cs_temperature(self):
        for i in range(3):
            try:
                ans = self.request("getData", GETDATA_CS_RESERVOIR)
                return float(ans) / 505. * 123.
                break
            except Exception, e:
                print e
        return -1

    def calibrate_target_voltage(self, y1=0., y2=5.):
        self.set_target_voltage(y1)
        time.sleep(2)
        x1 = float(self.request("getData", GETDATA_TARGET_VOLTAGE))
        self.set_target_voltage(y2)
        time.sleep(2)
        x2 = float(self.request("getData", GETDATA_TARGET_VOLTAGE))
        self.set_target_voltage(5.)
        a = (y2 - y1) / (x2 - x1)
        b = y1 - a * x1
        self.factors_target = a, b
        # print self.factors_target

    def calibrate_extraction_voltage(self, y1=0., y2=30.):
        self.set_extraction_voltage(y1)
        time.sleep(2)
        x1 = float(self.request("getData", GETDATA_EXTRACTION_VOLTAGE))
        self.set_extraction_voltage(y2)
        time.sleep(2)
        x2 = float(self.request("getData", GETDATA_EXTRACTION_VOLTAGE))
        self.set_extraction_voltage(29.)
        a = (y2 - y1) / (x2 - x1)
        b = y1 - a * x1
        self.factors_extraction = a, b
        # print self.factors_extraction
