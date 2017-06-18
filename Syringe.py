import crc16
import serial
import time

# Modbus Function Codes
# X, Y, D : Corresponding Memory Locations
F_READ_OUTPUT_SIGNAL = 0x01    # Y
F_READ_INPUT_SIGNAL = 0x02    # X
F_READ_DATA = 0x03    # D ; cannot read output/input signals
F_FORCED_SIGNAL_OUTPUT = 0x05    # write one Y
F_ECHO_BACK = 0x08
F_OUTPUT_SIGNAL_BATCH_WRITE = 0x0f    # write all Y
F_WRITE_DATA = 0x10    # D, X

# Memory Locations ; Each Location Contains 2 Bytes
M_STEP_DATA_NO = range(0x0400, 0x043f, 0x010)    # D
M_ALARM_DATA_GROUP = range(0x0380, 0x03bf, 0x4)    # D ; Each Group contains 8 Alarms (Each Alarm 1 Byte)
M_STATE_DATA_CURRENT_POSITION = 0x9000    # 4 Bytes ; 0.01 mm
M_STATE_DATA_SPEED = 0x9002    # 2 Bytes ; 1 mm / s
M_STATE_DATA_THRUST = 0x9003    # 2 Bytes ; 1 %
M_STATE_DATA_TARGET_POSITION = 0x9004    # 4 Bytes ; 0.01 mm
M_STATE_DATA_DRIVING_DATA_NO = 0x9006    # 2 Bytes ; Last/Current Process(ed/ing) Data Number
M_STATE_DATA_EQUIPMENT_NAME = 0xe    # 16 Bytes ; ASCII

# Relative Step Data Memory Locations (added to M_STEP_DATA_NO)
M_STEP_DATA_MODE = 0x0    # 2 Bytes ; 1: Absolute ; 2 : Relative Movement
M_STEP_DATA_SPEED = 0x1    # 2 Bytes ; 1 mm / s ; Speed to Target Position
M_STEP_DATA_POSITION = 0x2    # 4 Bytes ; 0.01 mm
M_STEP_DATA_ACCELERATION = 0x4    # 2 Bytes ; 1 mm / s**2
M_STEP_DATA_DECELLERATION = 0x5    # 2 Bytes ; 1 mm / s**2
M_STEP_DATA_PUSHING_FORCE = 0x6    # 2 Bytes ; 0 : Positioning Operation ; 1..100 : Pushing Torque in %
M_STEP_DATA_TRIGGER_LV = 0x7    # 2 Bytes ;
M_STEP_DATA_PUSHING_SPEED = 0x8    # 2 Bytes ; 1 mm / s ; Speed while Pushing from Target Position
M_STEP_DATA_MOVING_FORCE = 0x9    # 2 Bytes ; 1 % ; Maximum Force when Positioning
M_STEP_DATA_AREA_OUTPUT_END1 = 0xa    # 4 Bytes
M_STEP_DATA_AREA_OUTPUT_END2 = 0xc    # 4 Bytes
M_STEP_DATA_IN_POSITION = 0xe    # 4 Bytes ; 0.01 mm ; Positioning/Pushing Width

# Relative Step Data Memory Locations for SPECIFIED DATA
M_SPECIFIED_START_FLAG = 0x9100    # 1 Byte ; 1: Start Operation ; Returns 0 after completion
M_SPECIFIED_DATA_MODE = 0x9102    # 2 Bytes ; 1: Absolute ; 2 : Relative Movement
M_SPECIFIED_DATA_SPEED = 0x9103    # 2 Bytes ; 1 mm / s ; Speed to Target Position
M_SPECIFIED_DATA_POSITION = 0x9104    # 4 Bytes ; 0.01 mm
M_SPECIFIED_DATA_ACCELERATION = 0x9106    # 2 Bytes ; 1 mm / s**2
M_SPECIFIED_DATA_DECELERATION = 0x9107    # 2 Bytes ; 1 mm / s**2
M_SPECIFIED_DATA_PUSHING_FORCE = 0x9108    # 2 Bytes ; 0 : Positioning Operation ; 1..100 : Pushing Torque in %
M_SPECIFIED_DATA_TRIGGER_LV = 0x9109    # 2 Bytes ;
M_SPECIFIED_DATA_PUSHING_SPEED = 0x910a    # 2 Bytes ; 1 mm / s ; Speed while Pushing from Target Position
M_SPECIFIED_DATA_MOVING_FORCE = 0x9910b    # 2 Bytes ; 1 % ; Maximum Force when Positioning
M_SPECIFIED_DATA_AREA_OUTPUT_END1 = 0x910c    # 4 Bytes
M_SPECIFIED_DATA_AREA_OUTPUT_END2 = 0x910e    # 4 Bytes
M_SPECIFIED_DATA_IN_POSITION = 0x9110    # 4 Bytes ; 0.01 mm ; Positioning/Pushing Width

# Internal Status Flags ; read-only
X_BUSY = 0x48
X_SVRE = 0x49
X_SETON = 0x4a
X_INP = 0x4b
X_AREA = 0x4c
X_WAREA = 0x4d
X_ESTOP = 0x4e
X_ALARM = 0x4f

# Internal State Change Flags ; read / write
Y_HOLD = 0x18
Y_SVON = 0x19
Y_DRIVE = 0x1a
Y_RESET = 0x1b
Y_SETUP = 0x1c
Y_JOG_minus = 0x1d
Y_JOG_plus = 0x1e
Y_SERIAL_MODE = 0x30

# FLAGS
FLAG_ON = [0xFF, 0x00]
FLAG_OFF = [0x00, 0x00]
X_FLAGS = [
    "OUT0",
    "OUT1",
    "OUT2",
    "OUT3",
    "OUT4",
    "OUT5",
    "Not In Use",
    "Not In Use",
    "BUSY",
    "SVRE",
    "SETON",
    "INP",
    "AREA",
    "WAREA",
    "ESTOP",
    "ALARM"]
Y_FLAGS = [
    "IN0",
    "IN1",
    "IN2",
    "IN3",
    "IN4",
    "IN5",
    "Not In Use",
    "Not In Use",
    "HOLD",
    "SVON",
    "DRIVE",
    "RESET",
    "SETUP",
    "JOG-",
    "JOG+",
    "SERIAL MODE"]

# Controller Defaults
CONTROLLER_ID = 0x01
BAUDRATE = 38400


def to_hex_H_L(h, bytes=2):
    h = format(h, "0%ix" % (bytes * 2))
    return [int(float.fromhex(h[2 * i:2 * i + 2])) for i in xrange(bytes)]


def readallbytes():
    answer = bytearray()
    while dev.in_waiting:
        r = dev.read()
        answer.append(r)
        time.sleep(.01)
    return answer


def to_int(b):
    return [int(_) for _ in b]


def to_hex(b):
    return [hex(_)[2:] for _ in b]


class SyringeDevice():
    dev = None
    T1 = .1

    def __init__(self, port="COM8"):
        """ open connection """
        self.dev = serial.Serial(port, BAUDRATE)
        while (not self.initialize()):
            print "Error(s) occured. Resetting and reinitializing syringe."
            time.sleep(1)

    def initialize(self):
        print "Serial Mode On"
        success = True
        self.setSerialFlag(1)
        time.sleep(.1)
        print "Reset"
        self.setResetFlag(1)
        time.sleep(.1)
        self.setResetFlag(0)
        print "Servo On"
        self.setSvonFlag(0)
        time.sleep(.1)
        self.setSvonFlag(1)
        time.sleep(.2)
        if (self.readXFlags()[9] == 0):
            print "Error: SVRE flag is 0"
            success = False
        print "Goto Reference Position"
        self.setSetupFlag(1)
        time.sleep(2)
        ans = self.readXFlags()
        if (ans[10] == 0):
            print "Error: SETON flag is 0"
            success = False
        if (ans[11] == 0):
            print "ERROR: INP flag is 0"
            success = False
        self.setSetupFlag(0)
        print "Set Positioning Mode: Absolute"
        self.setPositioningMode(1)
        print "Set speed to 10 mm / s."
        self.set_speed(10)
        print "Syringe Initialization Done."
        return success

    def close(self):
        """ close the device """
        self.dev.close()

    ##### READING AND WRITING TO MEMORY #####
    def readData(self, location, words):
        """ returns memory content as bytearray """
        r = [CONTROLLER_ID] + [F_READ_DATA] + to_hex_H_L(location) + to_hex_H_L(words)
        ans = self.request(r)[3:-2]
        return ans

    def writeData(self, location, data):
        """ writes to memory """
        words = len(data) / 2
        r = [CONTROLLER_ID] + [F_WRITE_DATA] + to_hex_H_L(location) + to_hex_H_L(words) + [len(data)] + data
        ans = self.request(r)[3:-2]
        return ans

    def readXFlags(self):
        r = [CONTROLLER_ID] + [F_READ_INPUT_SIGNAL] + to_hex_H_L(0x40) + to_hex_H_L(0x10)
        ans = map(float.fromhex, self.request_hex(r)[3:5])
        flag_X47_to_X40 = format(int(ans[0]), "08b")
        flag_X4f_to_X48 = format(int(ans[1]), "08b")
        flags = [int(_) for _ in flag_X4f_to_X48 + flag_X47_to_X40]
        flags.reverse()
        for i, flag in enumerate(flags):
            print flag, X_FLAGS[i]
        return flags

    def getXFlag(self, flag):
        r = [CONTROLLER_ID] + [F_READ_INPUT_SIGNAL] + to_hex_H_L(0x40) + to_hex_H_L(0x10)
        ans = map(float.fromhex, self.request_hex(r)[3:5])
        flag_X47_to_X40 = format(int(ans[0]), "08b")
        flag_X4f_to_X48 = format(int(ans[1]), "08b")
        flags = [int(_) for _ in flag_X4f_to_X48 + flag_X47_to_X40]
        flags.reverse()
        return flags[flag]

    def getYFlag(self, flag):
        r = [CONTROLLER_ID] + [F_READ_OUTPUT_SIGNAL] + to_hex_H_L(0x10) + to_hex_H_L(0x10)
        ans = map(float.fromhex, self.request_hex(r)[3:5])
        flag_Y17_to_Y10 = format(int(ans[0]), "08b")
        flag_Y1f_to_Y18 = format(int(ans[1]), "08b")
        flags = [_ for _ in flag_Y1f_to_Y18 + flag_Y17_to_Y10]
        flags.reverse()
        return flags[flag]

    def readYFlags(self):
        r = [CONTROLLER_ID] + [F_READ_OUTPUT_SIGNAL] + to_hex_H_L(0x10) + to_hex_H_L(0x10)
        ans = map(float.fromhex, self.request_hex(r)[3:5])
        flag_Y17_to_Y10 = format(int(ans[0]), "08b")
        flag_Y1f_to_Y18 = format(int(ans[1]), "08b")
        flags = [_ for _ in flag_Y1f_to_Y18 + flag_Y17_to_Y10]
        flags.reverse()
        for i, flag in enumerate(flags):
            print flag, Y_FLAGS[i]
        return flags

    def setStateChangeFlag(self, flag, value):
        r = [CONTROLLER_ID] + [F_FORCED_SIGNAL_OUTPUT] + to_hex_H_L(flag) + value
        ans = self.request(r)
        return ans

    def readData_all(self, location, words):
        """ returns full answer as bytearray """
        r = [CONTROLLER_ID] + [F_READ_DATA] + to_hex_H_L(location) + to_hex_H_L(words)
        ans = self.request(r)
        return ans

    def request_hex(self, data):
        """ adds crc16 checksum and returns answer as hex string array """
        crcL, crcH = crc16.getCRC16(data)
        data.append(crcL)
        data.append(crcH)
        self.dev.write(bytearray(data))
        time.sleep(self.T1)
        answer = self.readallbytes()
        return to_hex(answer)

    def request(self, data):
        """ adds crc16 checksum and returns answer as bytearray """
        crcL, crcH = crc16.getCRC16(data)
        data.append(crcL)
        data.append(crcH)
        self.dev.write(bytearray(data))
        time.sleep(self.T1)
        answer = self.readallbytes()
        return answer

    def readallbytes(self):
        """ reads all available bytes and returns bytearray """
        answer = bytearray()
        while self.dev.in_waiting:
            r = self.dev.read()
            answer.append(r)
            # time.sleep(.01)
        # print "answer: ", to_hex(answer)
        return answer

    ##### SET FLAGS #####
    def setDriveFlag(self, value=1):
        if value == 1:
            self.setStateChangeFlag(Y_DRIVE, FLAG_ON)
        else:
            self.setStateChangeFlag(Y_DRIVE, FLAG_OFF)

    def setResetFlag(self, value=1):
        if value == 1:
            self.setStateChangeFlag(Y_RESET, FLAG_ON)
        else:
            self.setStateChangeFlag(Y_RESET, FLAG_OFF)

    def setSerialFlag(self, value=1):
        """ 1: serial ; 2: parallel """
        if value == 1:
            self.setStateChangeFlag(Y_SERIAL_MODE, FLAG_ON)
        else:
            self.setStateChangeFlag(Y_SERIAL_MODE, FLAG_OFF)

    def setSvonFlag(self, value=1):
        if value == 1:
            self.setStateChangeFlag(Y_SVON, FLAG_ON)
        else:
            self.setStateChangeFlag(Y_SVON, FLAG_OFF)

    def setSetupFlag(self, value=1):
        if value == 1:
            self.setStateChangeFlag(Y_SETUP, FLAG_ON)
        else:
            self.setStateChangeFlag(Y_SETUP, FLAG_OFF)

    def setJogPlusFlag(self, value):
        if value == 1:
            self.setStateChangeFlag(Y_JOG_plus, FLAG_ON)
        else:
            self.setStateChangeFlag(Y_JOG_plus, FLAG_OFF)

    def setJogMinusFlag(self, value):
        if value == 1:
            self.setStateChangeFlag(Y_JOG_minus, FLAG_ON)
        else:
            self.setStateChangeFlag(Y_JOG_minus, FLAG_OFF)


    def getBusyFlag(self):
        return self.getXFlag(8)

    def getInpFlag(self):
        return self.getXFlag(11)

    ##### SET NEW STATE #####
    def startOperation(self):
        # return self.writeData(M_SPECIFIED_START_FLAG, [0x01, 0x00])
        return self.setDriveFlag()

    def setPositioningMode(self, mode):
        """ 1: absolute ; 2: relative """
        return self.writeData(M_STEP_DATA_NO[0] + M_STEP_DATA_MODE, to_hex_H_L(mode))

    def set_speed(self, speed):
        """ mm / s """
        return self.writeData(M_STEP_DATA_NO[0] + M_STATE_DATA_SPEED, to_hex_H_L(int(speed)))

    def setTargetPosition(self, pos):
        """ set target position in mm """
        pos = int(pos * 100)
        ans = self.writeData(M_STEP_DATA_NO[0] + M_STEP_DATA_POSITION, to_hex_H_L(pos, 4))
        # print currentPos, "-->", targetPos

    def goto(self, pos):
        self.setTargetPosition(pos)
        self.setDriveFlag()
        # print "\rSyringe BUSY going to %.1f mm" % (pos),
        while (self.getBusyFlag() == 1):
            time.sleep(1)
        # print "\rNot Yet INP",
        while (self.getInpFlag() == 0):
            time.sleep(1)
        self.setDriveFlag(0)
        # print "\r",


    def setAcceleration(self, acceleration):
        """ mm / s**2 """
        return self.writeData(M_SPECIFIED_DATA_ACCELERATION, to_hex_H_L(acceleration))

    def setDeceleration(self, deceleration):
        """ mm / s**2 """
        return self.writeData(M_SPECIFIED_DATA_DECELERATION, to_hex_H_L(deceleration))

    def setPushingForce(self, percentage):
        """ 0: positioning operation """
        return self.writeData(M_SPECIFIED_DATA_PUSHING_FORCE, to_hex_H_L(percentage))

    def setTriggerLevel(self, percentage):
        return self.writeData(M_SPECIFIED_DATA_TRIGGER_LV, to_hex_H_L(percentage))

    def setPushingSpeed(self, speed):
        """ m / s """
        return self.writeData(M_SPECIFIED_DATA_PUSHING_SPEED, to_hex_H_L(speed))

    def setMovingForce(self, percentage):
        return self.writeData(M_SPECIFIED_DATA_MOVING_FORCE, to_hex_H_L(percentage))

    ##### GET CURRENT STATE #####
    def getCurrentPosition(self):
        """ returns current position in mm """
        ans = self.readData(M_STATE_DATA_CURRENT_POSITION, 2)
        ans = float.fromhex("".join(to_hex(ans))) / 100.
        # print ans, "mm"
        return ans

    def getTargetPosition(self):
        """ returns target position in mm """
        ans = self.readData(M_STATE_DATA_TARGET_POSITION, 2)
        ans = float.fromhex("".join(to_hex(ans))) / 100.
        print ans, "mm"
        return ans

    def getCurrentSpeed(self):
        """ returns current speed in mm / s """
        ans = self.readData(M_STATE_DATA_SPEED, 1)
        ans = float.fromhex("".join(to_hex(ans)))
        print ans, "mm / s"
        return ans

    def getCurrentThrust(self):
        """ returns current thrust in % """
        ans = self.readData(M_STATE_DATA_THRUST, 1)
        ans = float.fromhex("".join(to_hex(ans)))
        print ans, "%"
        return ans

    def getDrivingDataNumber(self):
        """ returns current/processed driving data number """
        ans = self.readData(M_STATE_DATA_DRIVING_DATA_NO, 1)
        ans = float.fromhex("".join(to_hex(ans))) * 100.
        print int(ans)
        return ans

    def getEquipmentNumber(self):
        """ returns equipment number as string """
        ans = self.readData(M_STATE_DATA_EQUIPMENT_NAME, 8)
        ans_string = "".join([chr(i) for i in ans])
        print ans_string
        return ans_string


if __name__ == "__main__":
    dev = serial.Serial("COM8", 38400)
    while True:
        try:
            data = map(int, map(float.fromhex, raw_input("> ").split()))
            crcL, crcH = crc16.getCRC16(data)
            data.append(crcL)
            data.append(crcH)
            print map(hex, data)
            data = bytearray(data)
            dev.write(data)
            time.sleep(.1)

            answer = readallbytes()
            payload = to_hex(answer)
            #data_string = "".join(chr(i) for i in payload)
            #value = struct.unpack(">f", data_string)[0] * 1000. + self.offset

            print payload
            # raw_input("ENTER")
        except Exception as e:
            print e
            dev.close()
            break
