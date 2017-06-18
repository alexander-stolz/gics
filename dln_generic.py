from dln import *

DLN_MAX_HOST_LENGTH = 50
DLN_DEFAULT_SERVER_PORT = 9656

DLN_HW_TYPE_DLN1 = 1
DLN_HW_TYPE_DLN2 = 2
DLN_HW_TYPE_DLN3 = 3
DLN_HW_TYPE_DLN4 = 4
DLN_HW_TYPE_DLN5 = 5

class DLN_VERSION(Structure):
    _fields_ = [("hardwareType", c_uint),
                ("hardwareVersion", c_uint),
                ("firmwareVersion", c_uint),
                ("serverVersion", c_uint),
                ("libraryVersion", c_uint)]

def DlnGpioPinPullupEnable(handle, pin):
    return cdll.dln.DlnGpioPinPullupEnable(handle, c_uint(pin))

def DlnGpioPinSetDirection(handle, pin, direction):
    """ 0: input, 1: output """
    return cdll.dln.DlnGpioPinSetDirection(handle, c_uint(pin), c_uint(direction))

def DlnGpioPinEnable(handle, pin):
    return cdll.dln.DlnGpioPinEnable(handle, c_uint(pin))

def DlnGpioPinGetVal(handle, pin):
    value = c_uint8()
    cdll.dln.DlnGpioPinGetVal(handle, c_uint(pin), byref(value))
    return value

def DlnGpioPinSetOutVal(handle, pin, value):
    return cdll.dln.DlnGpioPinSetOutVal(handle, c_uint(pin), c_uint8(value))

def DlnGpioPinDisable(handle, pin):
    return cdll.dln.DlnGpioPinDisable(handle, c_uint(pin))

def DlnRegisterNotification(handle, notification):
    #notification =
    result = cdll.dln.DlnRegisterNotification(handle, notification);
    return result

def DlnUnregisterNotification(handle):
    result = cdll.dln.DlnUnregisterNotofication(handle)
    return result

def DlnConnect(host, port):
    result = cdll.dln.DlnConnect(c_char_p(host), c_ushort(port))
    return result

def DlnOpenDevice(deviceNumber):
    deviceHandle = c_ushort()
    result = cdll.dln.DlnOpenDevice(c_uint(deviceNumber), byref(deviceHandle))
    return (result, deviceHandle)

def DlnGetVersion(handle):
    version = DLN_VERSION()
    result = cdll.dln.DlnGetVersion(handle, byref(version))
    return (result, version)

def DlnCloseHandle(handle):
    result = cdll.dln.DlnCloseHandle(handle)
    return result

def DlnDisconnect(host, port):
    result = cdll.dln.DlnDisconnect(c_char_p(host), c_ushort(port))
    return result

def DlnDisconnectAll():
    result = cdll.dln.DlnDisconnectAll()
    return result

def DlnGetDeviceCount():
    deviceCount = c_uint()
    result = cdll.dln.DlnGetDeviceCount(byref(deviceCount))
    return (result, deviceCount)

def DlnOpenDeviceBySn(deviceSn):
    deviceHandle = c_ushort()
    result = cdll.dln.DlnOpenDeviceBySn(c_uint(deviceSn), byref(deviceHandle))
    return (result, deviceHandle)

def DlnOpenDeviceById(deviceId):
    deviceHandle = c_ushort()
    result = cdll.dln.DlnOpenDeviceById(c_uint(deviceId), byref(deviceHandle))
    return (result, deviceHandle)

def DlnOpenStream(deviceHandle):
    streamHandle = c_ushort()
    result = cdll.dln.DlnOpenStream(deviceHandle, byref(streamHandle))
    return (result, streamHandle)

def DlnCloseAllHandles():
    result = cdll.dln.DlnCloseAllHandles()
    return result

def DlnGetDeviceSn(handle):
    deviceSn = c_uint()
    result = cdll.dln.DlnGetDeviceSn(handle, byref(deviceSn))
    return (result, deviceSn)

def DlnSetDeviceId(handle, deviceiId):
    result = cdll.dln.DlnSetDeviceId(handle, c_uint(deviceId))
    return result

def DlnGetDeviceId(handle):
    deviceId = c_uint()
    result = cdll.dln.DlnGetDeviceId(handle, byref(deviceId))
    return result
