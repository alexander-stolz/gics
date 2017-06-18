import serial
import time
import struct
import signal
import sys
import threading

dev = None


class PressureDevice(threading.Thread):
    dev = None
    request = None
    answer = None
    running = True
    request_p1 = bytearray([1, 3, 0, 2, 0, 2, 101, 203])
    request_p2 = bytearray([2, 3, 0, 2, 0, 2, 101, 248])
    answer_p1 = None
    answer_p2 = None

    def __init__(self, port="COM6"):
        threading.Thread.__init__(self)
        self.dev = serial.Serial(port)
        # self.lock = threading.Lock()

    def run(self):
        while self.running:
            self.write(self.request_p1)
            time.sleep(.1)
            x = self.readallbytes()
            # self.lock.acquire()
            self.answer_p1 = x
            # self.lock.release()
            time.sleep(.05)

            self.write(self.request_p2)
            time.sleep(.1)
            x = self.readallbytes()
            # self.lock.acquire()
            self.answer_p2 = x
            # self.lock.release()
            time.sleep(.05)

            if self.request:
                self.write(self.request)
                time.sleep(.1)
                self.answer = self.readallbytes()
                self.request = None
                time.sleep(.05)
        self.close()

    def run_old(self):
        """ deprecated. getting the pressure on demand takes to long """
        while self.running:
            if self.request:
                self.write(self.request)
                time.sleep(.05)
                self.answer = self.readallbytes()
                self.request = None
            time.sleep(.01)
        self.close()

    def close(self):
        self.running = False
        time.sleep(.2)
        self.dev.close()

    def write(self, s):
        self.dev.write(s)

    def read(self):
        return self.dev.read()

    def readallbytes(self):
        answer = bytearray()
        for i in range(3):
            while self.dev.in_waiting:
                r = self.dev.read()
                answer.append(r)
                # time.sleep(.01)
            if answer:
                return answer
                break
            time.sleep(.1)
        return answer


def readall():
    answer = bytearray()
    while dev.in_waiting:
        r = dev.read()
        answer.append(r)
        # time.sleep(.01)
    return answer


def to_int(b):
    return [int(_) for _ in b]


class Keller():
    offset = None
    request_pessure = None
    request_temperature = None
    dev = None

    def setDevice(self, dev):
        self.dev = dev

    def setOffset(self, offset):
        self.offset += offset
        return self.offset

    def getPressure_old(self):
        """ deprecated. getting the pressure on demand takes to long """
        self.dev.request = self.request_pessure
        while self.dev.request:
            time.sleep(.01)
        answer = self.dev.answer
        payload = to_int(answer)[11:-2]
        data_string = "".join(chr(i) for i in payload)
        value = struct.unpack(">f", data_string)[0] * 1000. - self.offset
        return value

    def get_temperature(self):
        self.dev.request = self.request_temperature
        while self.dev.request:
            time.sleep(.01)
        answer = self.dev.answer
        payload = to_int(answer)[11:-2]
        data_string = "".join(chr(i) for i in payload)
        value = struct.unpack(">f", data_string)[0]
        return value


class P1(Keller):
    offset = 0.
    request_pessure = bytearray([1, 3, 0, 2, 0, 2, 101, 203])
    request_temperature = bytearray([1, 3, 0, 8, 0, 2, 69, 201])

    def __init__(self, dev=None):
        if dev:
            self.dev = dev
            self.pressure_answer = dev.answer_p1

    def get_pressure(self):
        answer = self.dev.answer_p1
        for i in range(3):
            try:
                payload = to_int(answer)[11:-2]
                data_string = "".join(chr(i) for i in payload)
                value = struct.unpack(">f", data_string)[0] * 1000. - self.offset
                return value
                break
            except Exception, e:
                value = 0.
                print "P1: ", e
        return value


class P2(Keller):
    offset = 0.
    request_pessure = bytearray([2, 3, 0, 2, 0, 2, 101, 248])
    request_temperature = bytearray([2, 3, 0, 8, 0, 2, 69, 250])

    def __init__(self, dev=None):
        if dev:
            self.dev = dev

    def get_pressure(self):
        answer = self.dev.answer_p2
        for i in range(3):
            try:
                payload = to_int(answer)[11:-2]
                data_string = "".join(chr(i) for i in payload)
                value = struct.unpack(">f", data_string)[0] * 1000. - self.offset
                return value
                break
            except Exception, e:
                value = 0.
                print "P2: ", e
        return value


def mainloop():
    p1_obj = P1()
    p2_obj = P2()

    while True:
        try:
            # pressure P1
            print "\r", format(p1_obj.get_pressure(), ".2f") + " mbar",
            # temperature P1
            print "(%s)" % (format(p1_obj.get_temperature(), ".2f") + " celsius"),

            print " --- ",

            # pressure P2
            print format(p2_obj.get_pressure(), ".2f") + " mbar",
            # temperature P2
            print "(%s)" % (format(p2_obj.get_temperature(), ".2f") + " celsius"),

        except Exception, e:
            print e


def disconnectGracefully(signal, frame):
    print "closing.."
    dev.close()
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, disconnectGracefully)
    connect()
    mainloop()
