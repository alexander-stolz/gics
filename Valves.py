# --- Imports ---
from dln_generic import *
from dln_results import *
import signal
import sys
import time

serverHost = "localhost"
serverPort = DLN_DEFAULT_SERVER_PORT
handle = None

valves = {
    "V0": 16,  # 1: Syringe Valve to AMS
    "syringe": 16,
    "V1": 17,  # Pump
    "pump": 17,
    "V2": 18,
    "V3": 19,  # 1/0: change selector valve
    "V4": 20,
    "V5": 21,
    "V6": 22,  # He
    "he": 22,
    "ams": 23,
    "V8": 24,
    "V9": 25,  # ox
    "ox": 25,
    "V10": 26,  # blank
    "blank": 26,
    "V11": 27,
    "move": 28,
    "open": 29,
    "crack": 30,
    "he-vac": 31,  # 1: he
}

selectorValve = {
    "1": 8,
    "2": 9,
    "T": 10,
    "trap": 10,
    "C": 11,
    "cracker": 11,
    "3": 12,
    "blank": 12,
    "4": 13,
    "ox": 13,
}

switch = 3

log = lambda msg: open("log.txt", "a").write(str(msg) + "\n")


class ValvesDevice():
    handle = None
    serverHost = "localhost"
    serverPort = DLN_DEFAULT_SERVER_PORT
    pinrange = range(16, 32)

    def __init__(self):
        res = DlnConnect(self.serverHost, self.serverPort)
        if DLN_SUCCEEDED(res):
            res, self.handle = DlnOpenDevice(0)
            if DLN_SUCCEEDED(res):
                self.setPinDirection(self.pinrange, 1)
                self.setPinEnabled(self.pinrange)
                # self.setPinDirection(switch, 0)
            else:
                raise Exception("DlnOpenDevice failed.")
        else:
            raise Exception("DlnConnect failed.")

    def close(self):
        DlnCloseHandle(self.handle)
        DlnDisconnect(self.serverHost, self.serverPort)
        # log("diolan disconnected.")
        return 0

    def setPinEnabled(self, pins):
        try:
            for pin in pins:
                DlnGpioPinEnable(self.handle, pin)
        except:
                DlnGpioPinEnable(self.handle, pins)
        return 0

    def setPinDisabled(self, pins):
        try:
            for pin in pins:
                DlnGpioPinDisable(self.handle, pin)
        except:
                DlnGpioPinDisable(self.handle, pins)
        return 0

    def setPinDirection(self, pins, direction):
        try:
            for pin in pins:
                DlnGpioPinSetDirection(self.handle, pin, direction)
        except:
            DlnGpioPinSetDirection(self.handle, pins, direction)
        return 0

    def set_pin_value(self, pin, value, wait=.2):
        # self.setPinDirection(pin, 1)
        DlnGpioPinSetOutVal(self.handle, pin, value)
        if wait:
            time.sleep(wait)
        return 0

    def get_pin_value(self, pin):
        # self.setPinDirection(pin, 0)
        return DlnGpioPinGetVal(self.handle, pin).value


def mainloop():
    res = DlnConnect(serverHost, serverPort)
    if DLN_SUCCEEDED(res):
        print "Device connected."
        # open first available device (deviceNumber 0)
        res, handle = DlnOpenDevice(0)
        if DLN_SUCCEEDED(res):
            print "Device opened."

            while True:
                try:
                    pin = valves[raw_input("Valve = ")]
                    value = input("value? ")
                    res = DlnGpioPinSetDirection(handle, pin, 1)
                    res = DlnGpioPinEnable(handle, pin)
                    res = DlnGpioPinSetOutVal(handle, pin, value)
                except:
                    disconnect(0, 0)

                if DLN_SUCCEEDED(res):
                    pass
                else:
                    print "Error code " + hex(res)
        else:
            print "Failed to open device"
    else:
        print "Failed to connect to local DLN server"


def disconnect(signal, frame):
    print "closing.."
    DlnCloseHandle(handle)
    print ("Device disconnected." if not DlnDisconnect(serverHost, serverPort) else "Error while trying to disconnect.")
    time.sleep(1)
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, disconnect)
    mainloop()
