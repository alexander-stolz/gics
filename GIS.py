__version__ = '17/05/16'
__author__ = 'Alexander M. Stolz'
__licence__ = """The software gics (gas injection control software) maintained
by Alexander M. Stolz is freely available and distributable. However, if you use
it for some work whose results are made public, then you have to reference it properly."""


print """
 Gas Injection Control Software, Alexander Stolz, University of Cologne, v17.06
--------------------------------------------------------------------------------
"""

HANDLE_SPARKS = False
FAKECRACK = False
SKIPCLEANING = False
MAILER = True
CHECK_SYSTEM = True
TCPIP = True
SHOW_OPEN_THREADS = True
TESTMAIL = False                                                                # setPrivate()

print "opening devices: ",
print "valves, ",
import Valves
print "pressure sensors, ",
import PressureSensors
print "syringe, ",
import Syringe
print "volumes (virtual), ",
import Volumes
print "faraday cup, ",
import FaradayCup
if TCPIP:
    print "ams, ",
    import Ams
print "switch, ",
import Switch
print "plotter (virtual), ",
import Plotter
# print "neural net"
# import NN2
print "analysis, ",
import OnlineAnalysis
print "mailer\n"
import Mailer
import syntax
import time
import thread
import threading
from PyQt4 import QtGui, QtCore
import design
import sys
import pickle
from numpy import linspace, mean, std, arange
import re
import getpass

app = None

STATUS = ""
SWITCHON = 0                                                                    # switch_device.button == 0 --> switch: up
SWITCHOFF = 1                                                                   # switch_device.button == 1 --> switch: down

GET_STATUS = False                                                              # depreciated
DRIVE = False                                                                   # true if measuring
PAUSE = False
SWIPE_DRIVE = False                                                             # true if swiping
OPTIMIZE = False                                                                # true if optimizing
WORKING = False
MOVING = False
BATCH_RUNNING = False                                                           # true if batch measurement running
KICKSTART = False                                                               # true until current > MIN_CURRENT
BREAKALL = False
EXIT = False
CRACKER_CHANGE = False                                                          # true while moving cracker
TARGET_MUG_PER_MINUTE = 1.4
BASE_FLOW = 2.2                                                                 # for kickstart
SPARKS = 0                                                                      # sparks since last reset
MIN_SPARKS = 3                                                                  # SPARKS > MIN_SPARKS and SPARKS/Minutes > MAX_SPARKS_PER_MINUTE and HANDLE_SPARKS --> do s.th.
MAX_SPARKS_PER_MINUTE = 1. / 5.
SOLID_ERROR_TRESHOLD = .7                                                       # prozent ; solange werden solids gemessen

TEMP_MIN = 125.                                                                 # depreciated
TEMP_MAX = 130.                                                                 # depreciated
TEMP_STEP = 1.
TEMP_MAX_DROP = 5.
WAIT_FOR_TARGET_CHANGE = 60
WAIT_FOR_HIGH_HE_CURRENT = 120
WAIT_FOR_LOW_HE_CURRENT = 600
HIGH_HE_CURRENT = 2e-6
LOW_HE_CURRENT = .25e-6
MIXTURE_OX = 5.3                                                                # percent
MIXTURE_BLANK = 5.                                                              # percent
MEASUREMENT_LIST = []                                                           # filled in loadMeasurementFile()
CRACKER_POSITION = 1
SYRINGE_MIXING_POSITION = 85                                                    # mm ; for mixing sample gas to targetMixture
MAGAZINE_SIZE = 8
BLOCK_DATA_DIRECTORY = ""                                                       # remote directory of current analysis (HVE AMS Software)
EMAIL_BATCH = ""                                                                # recipient(s) for Batch Report
EMAIL_SINGLE = ""                                                               # recipient(s) for Sample Measured
EMAIL_ADMIN = "amstolz@gmail.com"                                               # recipient(s) for privateMail()

COM_SYRINGE = "COM8"
COM_PRESSURE = "COM6"
COM_SWITCH = "COM11"

K = 1.380649e-23                                                                # Boltzmann
TEILCHEN_PRO_MOL = 6.022e23
LITER_PRO_MOL = 22.414
LITER_PRO_TEILCHEN = LITER_PRO_MOL / TEILCHEN_PRO_MOL
VOL_SYRINGE = 2.6861e-6
VOL_CRACKER_CLEAN = 1.3330e-6                                                   # cracker without glass + pipe till V2 ; measured
VOL_CRACKER = 7.834311e-7                                                       # depreciated
VOL_PIPE = 3.174258e-8                                                          # pipe V2 to syringe ; measured

Mailer.pw = getpass.getpass("email password > ")
if (not Mailer.pw):
    print "skipping mailer\n"

config_keywords = {
    "email_from": "Mailer.addr_from",
    "email_to_batch": "EMAIL_BATCH",
    "email_to_single": "EMAIL_SINGLE",
    "minimum_reservoir_temperature": "TEMP_MIN",
    "maximum_reservoir_temperature": "TEMP_MAX",
    "reservoir_temperature_step": "TEMP_STEP",
    "maximum_reservoir_temperature_drop": "TEMP_MAX_DROP",
    "maximum_sparks_per_minute": "MAX_SPARKS_PER_MINUTE",
    "wait_after_new_target": "WAIT_FOR_TARGET_CHANGE",
    "wait_for_high_he12_current": "WAIT_FOR_HIGH_HE_CURRENT",
    "high_he12_current": "HIGH_HE_CURRENT",
    "wait_for_low_he12_current": "WAIT_FOR_LOW_HE_CURRENT",
    "low_he12_current": "LOW_HE_CURRENT",
    "ox_mixture": "MIXTURE_OX",
    "blank_mixture": "MIXTURE_BLANK",
    "sample_magazine_size": "MAGAZINE_SIZE",
    "path_to_block_data": "BLOCK_DATA_DIRECTORY",
    "sparks_allowed": "MIN_SPARKS",
    "carbon_flow": "TARGET_MUG_PER_MINUTE",
    "kickstart_base_flow": "BASE_FLOW"
}

print "loading config.txt"
try:
    with open("config.txt", "r") as f:
        for row in f:
            if ":" in row:
                try:
                    r = row.split(":")
                    key = r[0].strip()
                    val = r[1].strip()
                    if (key == "path_to_block_data"):
                        val = (row.split(":", 1)[1]).strip()
                    exec("%s = %s" % (config_keywords[key], val))
                except Exception, e:
                    print r
                    print e
except:
    print "could not load config"

print "\nstarting devices\n"

print "valves, ",
valves_device = Valves.ValvesDevice()
print "pressure sensors, ",
pressure_device = PressureSensors.PressureDevice(port=COM_PRESSURE)
print "syringe, ",
syringe_device = Syringe.SyringeDevice(port=COM_SYRINGE)
print "volumes, ",
volumes_device = Volumes.Volumes()
print "switch, ",
switch_device = Switch.SwitchDevice(port=COM_SWITCH)
print "faraday cup, ",
if TCPIP:
    current_device = FaradayCup.FcDevice()
    time.sleep(2)
    ams_device = Ams.AmsDevice()
else:
    current_device = FaradayCup.FcDevice(ams=False, port="COM112")
print "analysis\n"
print BLOCK_DATA_DIRECTORY
analysis_device = OnlineAnalysis.Device(BLOCK_DATA_DIRECTORY)
# print "neural net\n"
# neural_net = NN2.NN()

current_device.start()
switch_device.start()
pressure_device.start()
# neural_net.start()

p1 = PressureSensors.P1(pressure_device)
p2 = PressureSensors.P2(pressure_device)

print "devices online"

T = 0.                                                                          # temperature. is set during init
RATIO = .05                                                                     # mixing ratio. Is changed later.

HE_MINIMAL_PRESSURE = 1900.                                                     # mbar ; he open until p1 > HE_MINIMAL_PRESSURE
MIN_CURRENT = 1e-6                                                              # le12 current treshold

CURRENT_EFFICIENCY = 0.                                                         # from get_current_efficiency
CURRENT_AMPERE = 0.                                                             # from get_extracted_current
CURRENT_OFFSET = 0.                                                             # fc offset for get_extracted_current
CURRENT_ERROR = 0.                                                              # from counting statistics ; 1. / (sum(analysis_device.samples[-1]["counts"])) ** .5

THREADS = []                                                                    # array containing all active threads
NUM_OPEN_THREADS = 0                                                            # len(THREADS)

TIMEDATE = lambda: "{0:0>4}{1:0>2}{2:0>2}@{3:0>2}h{4:0>2}".format(*time.localtime())


def mbar_to_mug_c(x):
    return x / (Volumes.MUG_C_TO_MBAR / volumes_device.v1)


def log(msg):
    open("log.txt", "a").write(str(msg) + "\n")


def append_thread(t=None):
    global THREADS, NUM_OPEN_THREADS
    THREADS = filter(lambda x: x.is_alive(), THREADS)
    if (t):
        THREADS.append(t)
    NUM_OPEN_THREADS = len(THREADS)
    if (not SHOW_OPEN_THREADS):
        try:
            save_open_threads()
        except:
            pass


def save_open_threads_thread():
    while (not EXIT):
        time.sleep(5)
        try:
            with open("threads.txt", "w") as f:
                for t in THREADS:
                    print >> f, t
        except:
            pass


def save_open_threads():
    try:
        with open("threads.txt", "w") as f:
            for t in THREADS:
                print >> f, t
    except:
        pass


def private_mail():
    global EMAIL_BATCH, EMAIL_SINGLE
    EMAIL_BATCH = EMAIL_ADMIN
    EMAIL_SINGLE = EMAIL_ADMIN
    print "mail private"


if (TESTMAIL):
    private_mail()


class Logger(object):
    def __init__(self, filename="log/" + TIMEDATE() + ".txt"):
        self.terminal = sys.stdout
        self.filename = filename

    def write(self, message):
        if (not re.search("VisibleDeprecationWarning", message)):
            self.terminal.write(message)
            try:
                open(self.filename, "a").write(message)
            except:
                time.sleep(.5)
                try:
                    open(self.filename, "a").write(message)
                except:
                    self.terminal.write("LOGGING ERROR: " + message)
            try:
                form.lbl_working.setText(message)
            except:
                pass

sys.stdout = Logger()
sys.stderr = Logger()


class Queue():
    """docstring for Queue"""
    def __init__(self, length, fillwith=0.):
        self.length = length
        self.queue = [fillwith] * length

    def put(self, x):
        self.queue.insert(0, x)
        return self.queue.pop()

    def is_all_positive(self):
        if filter(lambda x: x < 0, self.queue):
            return False
        else:
            return True

    def is_all_negative(self):
        if filter(lambda x: x > 0, self.queue):
            return False
        else:
            return True

    def all_greater(self, value):
        if filter(lambda x: x <= value, self.queue):
            return False
        else:
            return True

    def all_smaller(self, value):
        if filter(lambda x: x >= value, self.queue):
            return False
        else:
            return True

    def relative_deviation(self):
        try:
            return std(self.queue) / mean(self.queue)
        except:
            return 1000.

    def relative_max_deviation(self):
        try:
            ans = (max(self.queue) - min(self.queue)) / mean(self.queue) / self.length
            print "\rCurrent Slope: %.2f%%" % (ans * 100.),
            return ans
        except:
            return 1000.

    def max_deviation(self):
        try:
            ans = max(self.queue) - min(self.queue)
            print "\rCurrent Max Deviation: %.2f" % (ans),
            return ans
        except:
            return 1000.


def time_formatted(s):
    m = s // 60
    s = s % 60
    if m > 0.:
        return "%02i:%02i" % (m, s)
    else:
        return "%i s" % (s)


def stop_flush_system():
    global BREAKALL
    BREAKALL = True


def flush_system(t=1e99, dt=300):
    thread_flush_system = threading.Thread(target=flush_system_thread, args=(t, dt))
    thread_flush_system.name = "flush system thread"
    thread_flush_system.start()
    append_thread(thread_flush_system)


def flush_system_thread(t=1e99, dt=300):
    " flood system with helium for dt seconds and pump down afterwards "
    global BREAKALL
    t0 = time.clock()
    t_end = t0 + t

    while True:
        if (BREAKALL):
            BREAKALL = False
            break
        # cracker abpumpen
        print "\rpumping down: ",
        close_he_valve()
        set_selector_valve("blank")
        set_selector_valve("cracker")
        syringe_valve_to_cracker()
        open_v2_valve()
        open_pump_valve()
        for i in xrange(int(dt)):
            if (BREAKALL) or (time.clock() > t_end):
                break
            time.sleep(1)
            print "\rpumping down: ", time_formatted(i),
        print " -- end pressure: ", p1.get_pressure()

        # mit he fluten
        close_pump_valve()
        syringe_valve_to_cracker()
        open_v2_valve()
        open_he_valve()
        for i in xrange(int(dt)):
            if (BREAKALL) or (time.clock() > t_end):
                break
            time.sleep(1)
            print "\rflooding with helium: ", time_formatted(i),
        print "\n"
    open_v2_valve()
    open_pump_valve()
    goto(0)


def check_system():
    " selector valve, he pressure, syringe moving, pump working "
    global STATUS, WORKING
    STATUS = "CHECKING SYSTEM"
    WORKING = True

    # wait for weather
    while (not T):
        time.sleep(.1)

    print "\n{:<30}".format("Testing Selector Valve:"),
    if (set_selector_valve("blank") == 0) and ((set_selector_valve("cracker") == 0)):
        print "PASSED"
    else:
        print "NOT PASSED"
        STATUS = ""
        WORKING = False
        return -1

    print "{:<30}".format("Testing He:"),
    syringe_valve_to_cracker()
    open_v2_valve()
    open_pump_valve()
    goto(95)
    close_pump_valve()
    p = p1.get_pressure()
    open_he_valve(t=3)
    if (p1.get_pressure() > p + 100.):
        print "PASSED", "(%.1f --> %.1f)" % (p, p1.get_pressure())
    else:
        print "NOT PASSED", "(%.1f --> %.1f)" % (p, p1.get_pressure())
        STATUS = ""
        WORKING = False
        return -1

    print "{:<30}".format("Testing Syringe:"),
    p = p1.get_pressure()
    goto(0)
    if (p1.get_pressure() < p - 25.):
        print "PASSED", "(%.1f --> %.1f)" % (p, p1.get_pressure())
    else:
        print "NOT PASSED", "(%.1f --> %.1f)" % (p, p1.get_pressure())
        STATUS = ""
        WORKING = False
        return -1

    print "{:<30}".format("Testing Pump:"),
    if (p1.get_pressure() < 200.):
        open_he_valve(t=3)
    p = p1.get_pressure()
    open_pump_valve()
    time.sleep(3)
    if (p1.get_pressure() < p - 100.):
        print "PASSED", "(%.1f --> %.1f)" % (p, p1.get_pressure())
    else:
        print "NOT PASSED", "(%.1f --> %.1f)" % (p, p1.get_pressure())
        STATUS = ""
        WORKING = False
        return -1
    STATUS = ""
    WORKING = False
    print "\nReady\n"
    return 0


def set_le12_range(r):
    FaradayCup.SCALE_NE12 = r / 100.


def clear_plot():
    form.plot_device.reset()


def set_ox_mixture(mix):
    global MIXTURE_OX
    MIXTURE_OX = mix


def set_blank_mixture(mix):
    global MIXTURE_BLANK
    MIXTURE_BLANK = mix


def show_status(t=5):
    global GET_STATUS
    GET_STATUS = True
    time.sleep(t)
    GET_STATUS = False
    print ""


def check_vacuum():
    global WORKING, CRACKER_CHANGE
    if not WORKING:
        print "checking vaccuum."
        WORKING = True
        CRACKER_CHANGE = True
        close_cracker()
        success = pump_down()
        close_v2_valve()
        if (not success):
            open_cracker()
            time.sleep(.5)
            close_cracker()
            time.sleep(.5)
        open_cracker()
        WORKING = False
        CRACKER_CHANGE = False
        print "checking vaccuum ended."


def close_all_valves():
    for pin in xrange(16, 32):
        valves_device.set_pin_value(pin, 0)


def open_he_valve(t=None):
    # print "Open He Valve"
    valves_device.set_pin_value(Valves.valves["V6"], 1)
    if t:
        time.sleep(t)
        close_he_valve()


def close_he_valve():
    # print "Close He Valve"
    valves_device.set_pin_value(Valves.valves["V6"], 0)


def open_v2_valve(t=None):
    valves_device.set_pin_value(Valves.valves["V2"], 1, False)
    if t:
        time.sleep(t)
        close_v2_valve()


def close_v2_valve():
    valves_device.set_pin_value(Valves.valves["V2"], 0)


def open_v9_valve():
    valves_device.set_pin_value(Valves.valves["V9"], 1)


def close_v9_valve():
    valves_device.set_pin_value(Valves.valves["V9"], 0)


def open_v10_valve():
    valves_device.set_pin_value(Valves.valves["V10"], 1)


def close_v10_valve():
    valves_device.set_pin_value(Valves.valves["V10"], 0)


def open_pump_valve(t=None):
    valves_device.set_pin_value(Valves.valves["V1"], 1)
    if t:
        time.sleep(t)
        close_pump_valve()


def he_vac_to_he():
    print "he-vac to He"
    valves_device.set_pin_value(Valves.valves["he-vac"], 1)


def he_vac_to_vac():
    print "he-vac to Vac"
    valves_device.set_pin_value(Valves.valves["he-vac"], 0)


def close_pump_valve():
    valves_device.set_pin_value(Valves.valves["V1"], 0)


def open_ams_valve():
    print "Open AMS Valve"
    valves_device.set_pin_value(Valves.valves["ams"], 1)


def close_ams_valve():
    print "Close AMS Valve"
    valves_device.set_pin_value(Valves.valves["ams"], 0)


def set_selector_valve(valve):
    global STATUS
    STATUS = "changing selector valve"
    pin = Valves.selectorValve[valve]
    close_v2_valve()
    for i in xrange(10):
        if valves_device.get_pin_value(pin) == 1:
            break
        valves_device.set_pin_value(19, 1)
        time.sleep(.2)
        valves_device.set_pin_value(19, 0)
        time.sleep(.5)
    STATUS = ""
    if (i == 9):
        print "ERROR: Selector Valve"
        return -1
    else:
        return 0


def syringe_valve_to_ams():
    valves_device.set_pin_value(16, 1)
    volumes_device.v3 = 0.


def syringe_valve_to_cracker():
    valves_device.set_pin_value(16, 0)
    volumes_device.v3 = volumes_device._v3


def perform_offset_correction():
    global STATUS
    STATUS = "performing offset correction"
    print "Offset Correction"
    global WORKING
    WORKING = True
    close_all_valves()
    success = pump_down()
    _current_p1 = p1.get_pressure()
    _current_p2 = p2.get_pressure()
    p1_offset = p1.setOffset(_current_p1)
    p2_offset = p2.setOffset(_current_p2)
    if success:
        print "\nP1: ", _current_p1, " --> ", p1.get_pressure(), "Offset: ", p1_offset
        print "P2: ", _current_p2, " --> ", p2.get_pressure(), "Offset: ", p2_offset
        print "Offset Correction Finished"
    else:
        print "Offset correction failed. End value not reached within 5 minutes."
    WORKING = False
    STATUS = ""
    return success


def check_he():
    global STATUS
    STATUS = "checking helium"
    global HE_MAXIMUM_PRESSURE
    close_all_valves()
    set_selector_valve("C")
    open_he_valve()
    last_p1 = 0.
    while True:
        p1_pressure = p1.get_pressure()
        if p1_pressure < last_p1 + 1.:
            break
        last_p1 = p1_pressure
    HE_MAXIMUM_PRESSURE = p1_pressure
    return HE_MAXIMUM_PRESSURE
    STATUS = ""


def pump_down():
    print "pumping down.."
    global STATUS
    STATUS = "pumping down"
    _last_p1 = p1.get_pressure()
    _last_p2 = p2.get_pressure()
    end_value_reached = False
    syringe_valve_to_cracker()
    open_v2_valve()
    open_pump_valve()
    he_vac_to_vac()
    # 300 * 1 s = 5 min
    for i in xrange(300):
        time.sleep(1)
        _current_p1 = p1.get_pressure()
        _current_p2 = p2.get_pressure()
        print "\rP1, P2: ", format(_current_p1, ".2f"), format(_current_p2, ".2f"),
        if (abs(_last_p1 - _current_p1) < .05) and (abs(_last_p2 - _current_p2) < .2):
            time.sleep(5)
            close_pump_valve()
            print "\nchecking vacuum.. ",
            close_v2_valve()
            time.sleep(5)
            if (abs(_last_p1 - p1.get_pressure()) < 1.):                         # and (abs(_last_p2 - _current_p2) < 1.):
                end_value_reached = True
                print "OK."
                break
            else:
                print "NOT OK. Time elapsed: ", time_formatted(i)
                open_pump_valve()
                open_v2_valve()
                time.sleep(5)
        _last_p1 = _current_p1
        _last_p2 = _current_p2
    print "\n"
    volumes_device.reset()
    return end_value_reached
    STATUS = ""


def measure_he_flow():
    pass


def clean_gis():
    global STATUS
    STATUS = "cleaning"
    global WORKING
    WORKING = True
    print "Cleaning GIS."
    set_selector_valve("C")
    close_all_valves()    # sets also syringe valve to cracker
    open_ams_valve()
    perform_offset_correction()
    he_vac_to_he()
    goto(95, speed=200)
    print "Syringe: ",
    syringe_device.getCurrentPosition()
    close_pump_valve()
    open_he_valve()
    he_vac_to_he()
    syringe_valve_to_ams()
    time.sleep(.1)
    syringe_valve_to_cracker()
    time.sleep(.1)
    syringe_valve_to_ams()
    time.sleep(.1)
    syringe_valve_to_cracker()
    open_ams_valve()
    open_v2_valve()
    goto(0, speed=200)
    print "Syringe: ",
    syringe_device.getCurrentPosition()
    for i in xrange(200):
        _p1_pressure = p1.get_pressure()
        _p2_pressure = p2.get_pressure()
        print "\rP1: %.2f mbar  P2: %.2f mbar" % (_p1_pressure, _p2_pressure),
        time.sleep(1)
        if (_p1_pressure > HE_MINIMAL_PRESSURE) and (i > 15):
            break
    print "\n"
    close_he_valve()
    print "Open Pump Valve."
    open_pump_valve()
    goto(95, speed=200)
    goto(95, speed=200)
    pump_down()
    goto(0, speed=200)
    perform_offset_correction()
    print "Syringe: ",
    syringe_device.getCurrentPosition()
    volumes_device.reset()
    open_ams_valve()
    he_vac_to_he()
    WORKING = False
    STATUS = ""
    form.cleaning = False
    print "Cleaning Finished"


def go_to_next_cracker_position():
    global CRACKER_POSITION, CRACKER_CHANGE
    CRACKER_CHANGE = True
    if valves_device.get_pin_value(14) == 0:
        # confirm cracker is in place
        if (valves_device.get_pin_value(15) == 0):
            print "something is very wrong here. is the cracker in position?"
        in_position = True
        valves_device.set_pin_value(29, 1, .5)    # open
        valves_device.set_pin_value(28, 1)        # move
        print "\rok ok i pay attention now!",
        for i in xrange(1, 50):
            if (valves_device.get_pin_value(15) == 0):
                in_position = False
                print "\ri saw the cracker moving!!    ",
            time.sleep(.001)
        print "\rback to sleep.                     ",
        valves_device.set_pin_value(29, 0, .5)
        valves_device.set_pin_value(28, 0)
        if (valves_device.get_pin_value(15) == 1) and (not in_position):
            print "\rcracker in position."
        elif (in_position):
            print "\ri did not see the cracker rushing by :( please check manually. SORRY!"
        CRACKER_POSITION += 1
    if valves_device.get_pin_value(14) == 1:
        time.sleep(.5)
        if valves_device.get_pin_value(14) == 1:
            CRACKER_POSITION = MAGAZINE_SIZE
            print "last position reached."
    CRACKER_CHANGE = False
    return CRACKER_POSITION


def open_cracker():
    valves_device.set_pin_value(29, 1)


def close_cracker():
    valves_device.set_pin_value(29, 0)


def load_measurement_file(f=None, txt=None):
    global MEASUREMENT_LIST
    MEASUREMENT_LIST = []
    batchlist = []
    if f:
        input_file = open(f, "r")
    else:
        input_file = txt.split("\n")

    with open("measurements/" + TIMEDATE() + "_batchlist.txt", "a") as batchlist_file:
        for row in input_file:
            print >> batchlist_file, row
            if row.startswith("#"):
                continue
            try:
                pos = int(row.strip().split(" ", 1)[0])
                name = row.strip().split(" ", 1)[1]
                MEASUREMENT_LIST.append([pos, name])
                batchlist.append("ampoule %i - %s" % (pos, name))
            except Exception, e:
                if row.strip() == "ox":
                    MEASUREMENT_LIST.append([0, "ox"])
                    batchlist.append("bottle ox-ii")
                elif row.strip() == "blank":
                    MEASUREMENT_LIST.append([0, "blank"])
                    batchlist.append("bottle blank")
                elif row.strip() == "private":
                    private_mail()
                elif row.strip() == "optimize_start":
                    MEASUREMENT_LIST.append([-1, "optimize_start"])
                    batchlist.append("start optimize")
                elif row.strip() == "optimize_stop":
                    MEASUREMENT_LIST.append([-1, "optimize_stop"])
                    batchlist.append("stop optimize")
                elif row.startswith("drive"):
                    _, d = row.split()
                    MEASUREMENT_LIST.append([-1, ["drive", float(d)]])
                    batchlist.append("set drive: %.1f mug/min" % (float(d)))
                elif row.startswith("temp"):
                    _, t = row.split()
                    MEASUREMENT_LIST.append([-1, ["temp", float(t)]])
                    batchlist.append("set temp: %.1f" % (float(t)))
                elif row.startswith("sleep"):
                    _, t = row.split()
                    MEASUREMENT_LIST.append([-1, ["sleep", float(t)]])
                    batchlist.append("sleep: %.1f min" % (float(t)))
                elif row.startswith("solidox"):
                    _, p = row.split()
                    MEASUREMENT_LIST.append([-1, ["solidox", float(p)]])
                    batchlist.append("solid ox")
                elif row.startswith("solid"):
                    _, p = row.split()
                    MEASUREMENT_LIST.append([-1, ["solid", float(p)]])
                    batchlist.append("solid")
                elif row.startswith("title"):
                    _, title = row.split(" ", 1)
                    MEASUREMENT_LIST.append([-1, ["title", title]])
                elif row.startswith("notes"):
                    _, notes = row.split(" ", 1)
                    MEASUREMENT_LIST.append([-1, ["notes", notes]])
                elif row.startswith("swipe"):
                    _, x0, x1 = row.split()
                    MEASUREMENT_LIST.append([-1, ["swipe", float(x0), float(x1)]])
                    batchlist.append("swipe: %.1f-%.1f mug/min" % (x0, x1))
                elif row.startswith("mode"):
                    mode = row.split()[1]
                    MEASUREMENT_LIST.append([-1, ["mode", mode]])
                    batchlist.append("set mode: %s" % (mode))
                elif row.startswith("flow"):
                    flow = float(row.split()[1])
                    MEASUREMENT_LIST.append([-1, ["flow", flow]])
                    batchlist.append("flow: %.2f mug/min" % (flow))
                elif row.startswith("targets"):
                    targets = []
                    for t in row.split()[1:]:
                        try:
                            targets.append(int(t.strip(",")))
                        except Exception, e:
                            print "Error reading target list: \n", e
                    MEASUREMENT_LIST.append([-1, ["targets", targets]])
                    batchlist.append("add targets: %s" % (", ".join(map(str, targets))))
                elif row.startswith("target"):
                    try:
                        _, x0, x1 = row.split()
                    except:
                        _, x0 = row.split()
                        x1 = LOW_HE_CURRENT
                    MEASUREMENT_LIST.append([-1, ["target", int(x0), float(x1)]])
                    batchlist.append("load target: %i ; %.1e A" % (int(x0), float(x1)))
                elif row.startswith("exec"):
                    _, d = row.split(" ", 1)
                    MEASUREMENT_LIST.append([-2, d])
                    batchlist.append("execute: %s" % (d))
                elif (row.strip()):
                    print "Did not understand: ", row.strip()
        print >> batchlist_file, "\n----------------------------\n"
    if app:
        for item in batchlist:
            form.list_batch_list.addItem(item)


def set_cracker_position(pos):
    global CRACKER_POSITION
    CRACKER_POSITION = pos


def get_extracted_current():
    # current_device.measure = True
    # while current_device.measure:
    #     time.sleep(.05)
    #
    if (not current_device.refresh):
        ans = current_device.current - CURRENT_OFFSET
        current_device.refresh = True
    else:
        time.sleep(.2)
        ans = current_device.current - CURRENT_OFFSET
        current_device.refresh = True
    return ans


def get_current_efficiency():
    # *-.1 wegen SO110-FC  TODO
    extracted_c12_particle_current = get_extracted_current() / 1.602176565e-19
    injected_c12_particle_current = get_particle_current() * volumes_device.get_mixture()
    try:
        return extracted_c12_particle_current / injected_c12_particle_current
    except:
        return 0.


def start_optimize():
    global OPTIMIZE
    if not OPTIMIZE:
        OPTIMIZE = True
        thread_optimize = threading.Thread(target=optimize_thread, name="optimize thread")
        thread_optimize.start()
        append_thread(thread_optimize)


def stop_optimize():
    global OPTIMIZE
    OPTIMIZE = False


def optimize_thread():
    global OPTIMIZE, TARGET_MUG_PER_MINUTE, SWIPE_DRIVE
    print "Optimize Started."
    start_time = time.clock()
    SWIPE_DRIVE = False
    last_efficiency = get_current_efficiency()
    last_mug_per_min = get_carbon_mug_per_min()
    step_direction = + 1.
    step_size = .15
    last_change = time.clock()
    dt = 0.
    history_length = 10
    currents = Queue(history_length)
    while OPTIMIZE:
        if TARGET_MUG_PER_MINUTE < 1.2:
            dt = 40.
            step_size = .07
            slope_treshold = form.spinbox_min_slope.value() / 100.
        elif TARGET_MUG_PER_MINUTE < 2.:
            dt = 30.
            step_size = .1
            slope_treshold = form.spinbox_min_slope.value() / 100.
        elif TARGET_MUG_PER_MINUTE < 3.:
            dt = 10.
            step_size = .15
            slope_treshold = form.spinbox_min_slope.value() / 100.
        elif TARGET_MUG_PER_MINUTE < 3.5:
            dt = 5.
            step_size = .2
            slope_treshold = form.spinbox_min_slope.value() / 100.
        else:
            step_direction = - 1
            dt = 1.
            step_size = .2
            slope_treshold = form.spinbox_min_slope.value() / 100.
        if (DRIVE) and (not KICKSTART) and (valves_device.get_pin_value(Valves.valves["ams"]) == 1) and (valves_device.get_pin_value(Valves.valves["syringe"]) == 1):
            extracted_current = get_extracted_current()
            oldest_current = currents.put(extracted_current)
            if (extracted_current > MIN_CURRENT):
                if currents.relative_max_deviation() < slope_treshold:
                    dt = 1.
                if time.clock() >= last_change + dt:
                    efficiency = get_current_efficiency()
                    carbon_current = get_carbon_mug_per_min()
                    # if form.chk_learn.isChecked() and ((time.clock() - start_time) > 300.):
                    #    neural_net.addSample(x=[volumes_device.getMixture(), carbon_current], y=efficiency)
                    if efficiency > last_efficiency:
                        step_direction = step_direction
                    else:
                        step_direction = - step_direction
                    TARGET_MUG_PER_MINUTE = carbon_current + step_size * step_direction
                    if TARGET_MUG_PER_MINUTE < .3:
                        TARGET_MUG_PER_MINUTE = carbon_current + .05
                        step_direction = + 1
                    last_change = time.clock()
                    last_efficiency = efficiency
                    if form.plot_device:
                        form.plot_device.carbon_flow_array.append(carbon_current)
                        form.plot_device.efficiency_array_reduced.append(efficiency * 100.)
                    time.sleep(2)
            else:
                TARGET_MUG_PER_MINUTE += .05
        time.sleep(1)
    del currents
    print "Optimize Ended."


def load_analysis(filename):
    analysis_device.load_analysis_file(filename)


def get_carbon_mug_per_min():
    return volumes_device.get_mixture() * get_particle_current() / Volumes.PARTICLES_PER_MUG * 60.


def measure_capillary(mbar_start=500, mbar_stop=2100, step_size=200, measure_time=10 * 60, filename="capillary.txt"):
    thread_measure_capillary = threading.Thread(
        target=measure_capillary_2_thread,
        name="measure capillary thread",
        args=(mbar_start, mbar_stop, step_size, measure_time, filename)
    )
    thread_measure_capillary.start()
    append_thread(thread_measure_capillary)


def stop_measure_capillary():
    global BREAKALL
    BREAKALL = True


def measure_capillary_thread(mbar_start=500, mbar_stop=2800, filename="capillary.txt"):
    global BREAKALL
    set_selector_valve("C")
    perform_offset_correction()
    close_all_valves()
    open_v2_valve()
    open_he_valve(3)
    syringe_valve_to_ams()
    volumes_device.p2 = p2.get_pressure()
    open_ams_valve()
    for mbar in range(mbar_start, mbar_stop + 1, 50):
        speed_array = []
        # goto(50)
        # goto(80)
        goto(0)
        if p2.get_pressure() < mbar:
            goto(50)
            syringe_valve_to_cracker()
            open_he_valve(3)
            syringe_valve_to_ams()
        goto(0)
        while (p2.get_pressure() > mbar - 100):
            syringe_valve_to_cracker()
            time.sleep(.5)
            syringe_valve_to_ams()
        volumes_device.p2 = p2.get_pressure()
        while (p2.get_pressure() < mbar - .5) or (p2.get_pressure() > mbar + .5):
            newPos = p2.get_pressure() * (volumes_device.pos - 95.) / mbar + 95.
            pos = goto(.0 * volumes_device.pos + 1. * newPos)
        for i in xrange(15):
            t = time.clock()
            while p2.get_pressure() > mbar * .99:
                time.sleep(.01)
                if BREAKALL:
                    BREAKALL = False
                    with open(filename, "a") as f:
                        print >> f, mbar, mean(speed_array), std(speed_array), "\t".join(speed_array)
                    return
            dt = time.clock() - t
            v = volumes_device.v2
            while (p2.get_pressure() < mbar - .5) or (p2.get_pressure() > mbar + .5):
                newPos = p2.get_pressure() * (volumes_device.pos - 95.) / mbar + 95.
                pos = goto(.0 * volumes_device.pos + 1. * newPos)
            dv = v - volumes_device.v2
            speed_array.append(dv / dt)
            print "%i. %i mbar -> %.2f mul/min ; mean = %.2f +- %.2f %%" % (
                i + 1,
                mbar,
                dv / dt * 6e10,
                mean(speed_array) * 6e10,
                std(speed_array) / mean(speed_array) * 100.
            )

        with open(filename, "a") as f:
            print >> f, mbar, mean(speed_array), std(speed_array), "\t".join(map(str, speed_array))


def measure_capillary_2_thread(mbar_start, mbar_stop, step_size, measure_time, filename="capillary.txt"):
    global BREAKALL
    BREAKALL = False
    print "start measure capillary. %i..%i step %i mbar ; %i s --> %s" % (mbar_start, mbar_stop, step_size, measure_time, filename)
    set_selector_valve("C")
    perform_offset_correction()
    close_all_valves()
    open_v2_valve()
    open_he_valve(3)
    syringe_valve_to_ams()
    volumes_device.p2 = p2.get_pressure()
    set_selector_valve("blank")
    open_pump_valve()
    close_ams_valve()
    for mbar in range(mbar_start, mbar_stop + 1, step_size):
        goto(0)
        if p2.get_pressure() < mbar:
            if mbar < 1800:
                goto(50)
            else:
                goto(0)
            set_selector_valve("cracker")
            open_pump_valve()
            time.sleep(5)
            close_pump_valve()
            syringe_valve_to_cracker()
            open_he_valve(3)
            syringe_valve_to_ams()
            set_selector_valve("blank")
        goto(0)
        close_pump_valve()
        while (p2.get_pressure() > mbar - 100):
            syringe_valve_to_cracker()
            time.sleep(.5)
            syringe_valve_to_ams()
        open_pump_valve()
        volumes_device.p2 = p2.get_pressure()
        while (p2.get_pressure() < mbar - .5) or (p2.get_pressure() > mbar + .5):
            new_pos = p2.get_pressure() * (volumes_device.pos - 95.) / mbar + 95.
            pos = goto(.0 * volumes_device.pos + 1. * new_pos)

        open_ams_valve()

        mm_counter = 0.
        t = time.clock()
        v = volumes_device.v2
        while (time.clock() - t < measure_time):
            if BREAKALL:
                BREAKALL = False
                print "measure capillary stoped"
                return
            if p2.get_pressure() < mbar:
                goto(volumes_device.pos + .1)
                mm_counter += .1
            dt = time.clock() - t
            dv = v - volumes_device.v2  # m_counter * 1e-3 * 2.6861e-6 / 95e-3
            print "\r%i/%i s. %i mbar -> %.2f mul/min ; %.2f mm" % (
                dt,
                measure_time,
                mbar,
                dv / dt * 6e10,
                mm_counter),
            time.sleep(.1)
        print " "
        with open(filename, "a") as f:
            print >> f, mbar, dv / dt * 6e10, p2.get_pressure(), mm_counter
    print "Measure Capillary Ended."


def dp_over_dt(p):
    """ this was measured ; Pa -> Pa / s """
    return 0.00384715200578          \
        - 9.29548284517e-06 * p      \
        - 2.00424827251e-09 * p ** 2 \
        + 3.30984204636e-16 * p ** 3 \
        - 1.45563540105e-21 * p ** 4


def get_particle_current(p=None):
    """ returns particles / s """
    if not p:
        p = p2.get_pressure()    # mbar
    m3_per_s = (0.0335061 * p + 2.51953) / 6e10
    return p * 100. * m3_per_s / (K * T)


def hold_pressure(mbar):
    global TARGET_MUG_PER_MINUTE
    TARGET_MUG_PER_MINUTE = get_particle_current(mbar) / Volumes.PARTICLES_PER_MUG * 60. * volumes_device.get_mixture()


def carbon_mug_per_min_to_mbar(mug_per_min):
    try:
        particle_current = mug_per_min * Volumes.PARTICLES_PER_MUG / 60. / volumes_device.get_mixture()
    except:
        particle_current = mug_per_min * Volumes.PARTICLES_PER_MUG / 60. / .05
    for p in xrange(1, 3000):
        if get_particle_current(p) > particle_current:
            break
    return p


def start_measurement(solid=False):
    global SPARKS
    SPARKS = 0

    if (not solid):
        syringe_valve_to_ams()
        drive(BASE_FLOW, kickstart=form.chk_kickstart.isChecked(), default_current=TARGET_MUG_PER_MINUTE)
        open_ams_valve()
        # startOptimize()
        close_v9_valve()
        close_v10_valve()
        open_v2_valve()
        close_he_valve()
        he_vac_to_vac()
        open_pump_valve()
    else:
        drive_solid()


def stop_measurement():
    global DRIVE
    DRIVE = False
    close_ams_valve()
    time.sleep(3)


def drive_solid():
    thread_drive_solid = threading.Thread(
        target=drive_solid_thread,
        name="drive solid thread"
    )
    thread_drive_solid.start()
    append_thread(thread_drive_solid)


def drive_solid_thread():
    global DRIVE, KICKSTART
    KICKSTART = False
    DRIVE = True
    # time.sleep(5)
    error = 9999.
    while (error > (SOLID_ERROR_TRESHOLD / 100.)):
        time.sleep(2)
        try:
            error = 1. / (sum(analysis_device.samples[-1]["counts"])) ** .5
        except:
            error = 9999.
    DRIVE = False


def drive(mug_per_min, kickstart=False, default_current=1.4):
    global TARGET_MUG_PER_MINUTE, DRIVE
    TARGET_MUG_PER_MINUTE = mug_per_min
    if not DRIVE:
        thread_drive_thread = threading.Thread(target=drive_thread, args=(kickstart, default_current))
        thread_drive_thread.name = "drive thread"
        thread_drive_thread.start()
        append_thread(thread_drive_thread)


def go_to_cracker_position(p):
    global CRACKER_CHANGE
    CRACKER_CHANGE = True
    if p > CRACKER_POSITION:
        while CRACKER_POSITION < p:
            go_to_next_cracker_position()
        CRACKER_CHANGE = False
        return p
    else:
        CRACKER_CHANGE = False
        return -1


def load_target(p):
    " helper function "
    return ams_device.load_target(p)


def start_batch_measurement():
    global MEASUREMENT_LIST, CRACKER_POSITION, BATCH_RUNNING
    BATCH_RUNNING = True
    min_pos = 9
    for p, n in MEASUREMENT_LIST:
        if p > 0 and p < min_pos:
            min_pos = p
    if min_pos < CRACKER_POSITION:
        print "Set Cracker Position first."
        return

    thread_batch_measurement = threading.Thread(
        target=batch_measurement_thread,
        name="batch measurement thread"
    )
    thread_batch_measurement.start()
    append_thread(thread_batch_measurement)


def batch_measurement_thread():
    global STATUS
    STATUS = ""
    global DRIVE, MEASUREMENT_LIST, CRACKER_POSITION, PAUSE, LOW_HE_CURRENT, SOLID_ERROR_TRESHOLD, BATCH_RUNNING, TARGET_MUG_PER_MINUTE, CURRENT_ERROR
    timedate = TIMEDATE()
    title = ""
    notes = ""
    optimize = False
    targets = []
    target_position = 0
    cs_temp = ams_device.get_cs_temperature()
    target_voltage = ams_device.get_target_voltage()
    extraction_voltage = ams_device.get_extraction_voltage()
    mode = "new"
    if not SKIPCLEANING:
        clean_gis()
    open_pump_valve()
    with open("measurements/_measurements.txt", "a") as f:
        print >> f, "\n\n", timedate
        print >> f, "pos", "name", "m1", "m2", "%mixture", "x", "time"
        for item_number, (p, n) in enumerate(MEASUREMENT_LIST):
            solid = False
            solid_ox = False
            print p, n
            if (not BATCH_RUNNING):
                break
            # p = 0 : gas from bottle
            if p == 0:
                if n.strip() == "ox":
                    transfer_ox()
                elif n.strip() == "blank":
                    transfer_blank()
            # p = -1 : keyword
            elif p == -1:
                if n == "optimize_start":
                    start_optimize()
                    form.list_batch_list.takeItem(0)
                    continue
                if n == "optimize_stop":
                    stop_optimize()
                    form.list_batch_list.takeItem(0)
                    continue
                if n[0] == "drive":
                    drive(float(n[1]))
                    continue
                if n[0] == "sleep":
                    t = n[1]
                    print "waiting"
                    for i in range(int(t * 60.)):
                        print "\r", time_formatted(t * 60 - i),
                        time.sleep(1)
                    form.list_batch_list.takeItem(0)
                    continue
                if n[0] == "flow":
                    flow = n[1]
                    TARGET_MUG_PER_MINUTE = flow
                    form.list_batch_list.takeItem(0)
                    continue
                if n[0] == "swipe":
                    continue
                if n[0] == "title":
                    title = " - " + n[1]
                    analysis_device.title = n[1]
                    continue
                if n[0] == "notes":
                    notes = n[1]
                    analysis_device.notes = notes
                    continue
                if n[0] == "temp":
                    ams_device.set_cs_temperature(n[1])
                    form.list_batch_list.takeItem(0)
                    continue
                if n[0] == "targets":
                    targets += n[1]
                    form.list_batch_list.takeItem(0)
                    print "Target list: ", targets
                    continue
                if n[0] == "mode":
                    mode = n[1]
                    continue
                if n[0] == "solid":
                    SOLID_ERROR_TRESHOLD = n[1]
                    solid = True
                if n[0] == "solidox":
                    SOLID_ERROR_TRESHOLD = n[1]
                    solid = True
                    solid_ox = True
                if n[0] == "target":
                    target_position = int(n[1])
                    targets = [target_position] + targets
                    LOW_HE_CURRENT = float(n[2])
                    print "Target list: ", targets
                    form.list_batch_list.takeItem(0)
                    continue
            # p = -2 : execute
            elif p == -2:
                try:
                    exec(n)
                except:
                    print "Execution of %s not possible." % (n)
                form.list_batch_list.takeItem(0)
                continue
            else:
                if (BATCH_RUNNING) and (go_to_cracker_position(p) > -1):
                    close_pump_valve()
                    he_vac_to_he()
                    open_v2_valve()
                    time.sleep(10)
                    he_vac_to_vac()
                    open_pump_valve(30)
                if (crack_and_transfer() == -1):
                    print "Skipping Sample."
                    form.list_batch_list.takeItem(0)
                    continue
            if (not solid):
                n = n.replace("\\", "-").replace("/", "-")
                m1 = volumes_device.m1
                m2 = volumes_device.m2
                mix = volumes_device.get_mixture()
            else:
                try:
                    if (solid_ox):
                        n = "solid ox sample (target %i)" % targets[0]
                    else:
                        n = "solid sample (target %i)" % targets[0]
                    m1 = 0.
                    m2 = 9999.
                    mix = 1.
                except:
                    print "no target selected. skipping sample."
                    form.list_batch_list.takeItem(0)
                    continue
            min_sparks = MIN_SPARKS
            print "Current Job: ", p, n, m1, m2, mix, volumes_device.v1 / volumes_device.v1_clean
            print >> f, p, n, m1, m2, mix * 100., volumes_device.v1 / volumes_device.v1_clean,

            for i in range(10):
                if not BATCH_RUNNING:
                    break
                # if (ams_device.getTargetVoltage() < 1.) or (ams_device.getExtractionVoltage() < 1.):
                #     ams_device.setTargetVoltage(target_voltage)
                #     ams_device.setExtractionVoltage(extraction_voltage)
                if (targets):
                    if (not solid) and (mode == "keep") and (i == 0):
                        pass
                    else:
                        target_position = targets[0]
                        targets = targets[1:]
                        print "Loading target: ", target_position
                        ams_device.load_target(target_position)
                    for i in xrange(WAIT_FOR_TARGET_CHANGE):
                        if not BATCH_RUNNING:
                            break
                        print "\rwait: ", WAIT_FOR_TARGET_CHANGE - i,
                        time.sleep(1)
                # if (ams_device.getTargetVoltage() < 1.) or (ams_device.getExtractionVoltage() < 1.):
                #     continue
                he12_queue = Queue(length=6, fillwith=1.)
                if (not solid):
                    for i in xrange(WAIT_FOR_HIGH_HE_CURRENT):
                        if not BATCH_RUNNING:
                                break
                        print "\rwaiting for HE12 current < %.1e:  %.1e A  (%i s)   " % (HIGH_HE_CURRENT, current_device.he12_current, WAIT_FOR_HIGH_HE_CURRENT - i),
                        time.sleep(1)
                        he12_queue.put(current_device.he12_current)
                        if (he12_queue.all_smaller(HIGH_HE_CURRENT)):
                            break
                    if (current_device.he12_current > HIGH_HE_CURRENT):
                        print "\n\nBad target.\n"
                    else:
                        for i in xrange(WAIT_FOR_LOW_HE_CURRENT):
                            if not BATCH_RUNNING:
                                break
                            he12_queue.put(current_device.he12_current)
                            print "\rwaiting for HE12 current < %.1e:  %.1e A  (%i s)   " % (LOW_HE_CURRENT, current_device.he12_current, WAIT_FOR_LOW_HE_CURRENT - i),
                            time.sleep(1)
                            if (he12_queue.all_smaller(LOW_HE_CURRENT)):
                                break
                        if (he12_queue.all_smaller(LOW_HE_CURRENT)):
                            break
            if not BATCH_RUNNING:
                break
            clear_plot()
            t0 = time.clock()
            if form.plot_device:
                form.plot_device.reset()
            if (solid):
                close_ams_valve()
                he_vac_to_vac()
            start_measurement(solid)
            time.sleep(30)
            if p > 0:
                go_to_next_cracker_position()
                close_pump_valve()
                he_vac_to_he()
                open_v2_valve()
                time.sleep(15)
                he_vac_to_vac()
                open_pump_valve()
            temp_dropped = 0
            new_sample = True                                                   # for online analysis
            analysis_device.check_and_update()
            while DRIVE:
                time.sleep(10)
                if (not solid) and (not form.ams):                              # if ams is closed
                    analysis_device.check_and_update()                               # ignore block
                    continue
                if (not KICKSTART):                                             # only analyze if current is high enough
                    response = analysis_device.check_and_update(new_sample, n)       # check if new block data are availabe in BLOCK_DATA_DIRECTORY
                    print "\rreading block: ", n,
                    if response:
                        print "%.3e" % response[0],
                        form.plot_device.add_ratios(*response)
                        form.plot_device.current_d13C = (mean(analysis_device.samples[-1]["r13"]) / OnlineAnalysis.R13VPDB - 1.) * 1000.
                        form.plot_device.current_r14 = mean(analysis_device.samples[-1]["r14"])
                        try:
                            CURRENT_ERROR = 1. / (sum(analysis_device.samples[-1]["counts"])) ** .5
                        except:
                            CURRENT_ERROR = 0.
                        form.plot_device.current_error = CURRENT_ERROR
                        if (CURRENT_ERROR * 100. < form.spinbox_min_error.value()):
                            print "minimum error reached: ", CURRENT_ERROR
                            DRIVE = False
                        # form.plot_device.setPlotRatios()
                    if (new_sample):
                        new_sample = False
                        analysis_device.target_position = target_position
                    if (HANDLE_SPARKS):
                        sparks_per_minute = SPARKS / (time.clock() - t0) * 60.
                        if (sparks_per_minute > MAX_SPARKS_PER_MINUTE) and (cs_temp - ams_device.get_cs_temperature() < TEMP_MAX_DROP) and (SPARKS > min_sparks):
                            if (temp_dropped < 2):
                                temp_dropped += 1
                                ams_device.set_cs_temperature(ams_device.get_cs_temperature() - TEMP_STEP)
                                print "\rtoo many discharges. dropping temperature and waiting."
                                close_ams_valve()
                                for i in range(5 * 60):
                                    time.sleep(1)
                                    analysis_device.check_and_update()
                                    print "\r", time_formatted(5 * 60 - i),
                                print "\n"
                                open_ams_valve()
                                min_sparks += SPARKS
                else:
                    analysis_device.check_and_update()                                                     # adds blocks to c14_device.filenames, so they won't be analyzed
            new_sample = False                                                                      # just to be sure
            # stopMeasurement()
            measurement_time = time.clock() - t0
            print >> f, measurement_time                                                            # write measurement time to file

            # XXX
            PAUSE = True
            syringe_valve_to_cracker()
            he_vac_to_he()
            open_ams_valve()
            if form.plot_device:
                x1, y1 = form.plot_device.carbon_flow_array, form.plot_device.efficiency_array_reduced
                x2, y2 = form.plot_device.time_array, form.plot_device.le12_array
                y22 = form.plot_device.efficiency_array
                y31 = form.plot_device.d13c_array
                mass_flow = form.plot_device.mass_flow_array
                fn = "measurements/" + TIMEDATE() + "_%i %s (%i).txt" % (p, n, time.clock())
                with open(fn, "w") as f2:
                    f2.write("[pos]%s\n" % (p))
                    f2.write("[name]%s\n" % (n))
                    f2.write("[mass cracked]%s\n" % (m1 + m2))
                    f2.write("[mass measured]%s\n" % (m2))
                    f2.write("[mix]%s\n" % (mix))
                    f2.write("[c flow vs efficiency]\n")
                    f2.writelines(["%f " % (a) for a in x1])
                    print >> f2, "\n",
                    f2.writelines(["%f " % (a) for a in y1])
                    f2.write("\n[time in s vs cup current in A vs efficiency in % vs delta c13 in permille vs mass flow in mug/min]\n")
                    f2.writelines(["%f " % (a) for a in x2])
                    print >> f2, "\n",
                    f2.writelines(["%e " % (a) for a in y2])
                    print >> f2, "\n",
                    f2.writelines(["%f " % (a) for a in y22])
                    print >> f2, "\n",
                    f2.writelines(["%f " % (a) for a in y31])
                    print >> f2, "\n",
                    f2.writelines(["%f " % (a) for a in mass_flow])
                print "sending mail",
                if (type(n) == list):
                    n_ = "; ".join(map(str, n))
                else:
                    n_ = n
                ratio = analysis_device.get_last_sample_ratio()
                counts = analysis_device.get_last_sample_counts()
                target_current, target_std = analysis_device.get_last_sample_target_current()
                he12_current, he12_std = analysis_device.get_last_sample_he12()
                block_start, block_stop = analysis_device.get_last_sample_blocks()
                message = TIMEDATE() + "\n\n"
                message += "<table>"
                message += "<tr><td>sample:</td>               <td>%s %s</td></tr>\n" % (p, n_)
                message += "<tr><td>target position:</td>      <td>%i</td></tr>\n" % (target_position)
                if (not solid):
                    message += "<tr><td>mass cracked:</td>         <td>%.1f mug</td></tr>\n" % (m1 + m2)
                    message += "<tr><td>mass measured:</td>        <td>%.1f mug</td></tr>\n" % (m2)
                    message += "<tr><td>mixing ratio:</td>         <td>%.1f %%</td></tr>\n" % (mix * 100.)
                    message += "<tr><td>carbon flow:</td>          <td>%.2f mug / min</td></tr>\n" % (TARGET_MUG_PER_MINUTE)
                    message += "<tr><td>efficiency:</td>           <td>(%.1f +- %.1f) %%</td></tr>\n" % (mean(y22), std(y22))
                message += "<tr><td>measured ratio:</td>       <td>%.2e +- %.1f %%</td></tr>\n" % (ratio, 100. / (counts) ** .5)
                message += "<tr><td>measurement time:</td>     <td>" + time_formatted(measurement_time) + "</td></tr>\n"
                message += "<tr><td>12C (4+) current:</td>     <td>(%.2f +- %.2f) muA</td></tr>\n" % (he12_current * 1e6, he12_std * 1e6)
                message += "<tr><td>target current:</td>       <td>(%.2f +- %.2f) mA</td></tr></td></tr>\n" % (target_current, target_std)
                message += "<tr><td>14C counts:</td>           <td>%i</td></tr>\n" % (counts)
                message += "<tr><td>blocks:</td>               <td>%i - %i</td></tr>\n" % (block_start, block_stop)
                message += "<tr><td>Cs reservoir:</td>         <td>%.1f deg. C</td></tr>\n" % (ams_device.get_cs_temperature())
                message += "<tr><td>target voltage:</td>       <td>%.3f kV</td></tr>\n" % (ams_device.get_target_voltage())
                message += "<tr><td>discharges:</td>           <td>%i</td></tr>\n\n\n" % (SPARKS)
                message += "</table>"

                print "sample measured"
                print "----------------------------------------------------"
                print message.strip().replace("<table>", "").replace("</table>", "").replace("<td>", "").replace("</td>", "").replace("<tr>", "").replace("</tr>", "").replace('<br />', "")
                print "----------------------------------------------------"

                # message += open(fn, "r").read().replace("\n", "<br \>\n")
                Mailer.send_message("GIS: Sample Measured" + title, message, EMAIL_SINGLE)
                print "\rmail sent."
            sparks_per_minute = SPARKS / (t0 - time.clock()) * 60.
            if (sparks_per_minute > MAX_SPARKS_PER_MINUTE) and (cs_temp - ams_device.get_cs_temperature() < TEMP_MAX_DROP):
                ams_device.set_cs_temperature(ams_device.get_cs_temperature() - TEMP_STEP)
                print "Cs reservoir TEMPERATURE REDUCED due to sparks"
            if app:
                try:
                    form.list_batch_list.takeItem(0)
                except Exception, e:
                    print e
            if (item_number < len(MEASUREMENT_LIST) - 1):
                clean_gis()
            open_v2_valve()
            open_pump_valve()
            open_ams_valve()
            he_vac_to_he()
            if TCPIP:
                next_measurement()
            else:
                print "Change Target and Wait for Low Current. Then next()"
                while PAUSE and BATCH_RUNNING:
                    time.sleep(1)
    print "Last Sample was measured."
    print "running = false"
    BATCH_RUNNING = False
    # form.txtedit_batch_in.setEnabled(True)

    print "create report. "
    report = analysis_device.create_report(timedate)
    print "done"
    report += "<br /><br />\nbatch file:<br />\n-----------------------------------------<br />\n"
    report += form.txtedit_batch_in.toPlainText().replace("\n", "\n<br />")

    if notes:
        report += "<br /><br />\nnotes:<br />\n%s" % (str(notes))

    report += '<br /><br /><p><img src="cid:image1"></p><br /><br /><br />'
    print "send message. ",
    Mailer.send_message("GIS: Batch Report" + str(title), report, to=EMAIL_BATCH, image="measurements/" + timedate + ".png")
    print "done"

    STATUS = ""


def next_measurement():
    global PAUSE
    PAUSE = False


def measure_efficiency_curve_thread(min_flow=.3, max_flow=2., only_once=False):
    global OPTIMIZE, TARGET_MUG_PER_MINUTE, SWIPE_DRIVE, DRIVE
    print "Measure Efficiency Curve Started."
    start_time = time.clock()
    SWIPE_DRIVE = True
    OPTIMIZE = False
    last_efficiency = get_current_efficiency()
    last_mug_per_min = get_carbon_mug_per_min()
    step_direction = + 1.
    step_size = .1
    last_change = time.clock()
    min_waiting_time = 30.
    history_length = 10
    efficiency_queue = Queue(history_length)
    TARGET_MUG_PER_MINUTE = min_flow
    while (DRIVE):
        time.sleep(5)
        efficiency_queue.put(get_current_efficiency() * 100.)
        slope_treshold = form.spinbox_min_slope.value()
        if (efficiency_queue.max_deviation() < slope_treshold) and (time.clock() - last_change > min_waiting_time):
            if (TARGET_MUG_PER_MINUTE + step_size <= max_flow):
                TARGET_MUG_PER_MINUTE += step_size
            else:
                if (only_once):
                    break
                TARGET_MUG_PER_MINUTE = min_flow
            last_change = time.clock()
            # form.carbon_current_changed()
    del efficiency_queue
    SWIPE_DRIVE = False
    print "Ended."


def measure_efficiency_curve(min_flow=.3, max_flow=2., only_once=False):
    thread_efficiency_curve_thread = threading.Thread(target=measure_efficiency_curve_thread, args=(min_flow, max_flow, only_once))
    thread_efficiency_curve_thread.name = "efficiency curve thread"
    thread_efficiency_curve_thread.start()
    append_thread(thread_efficiency_curve_thread)


def find_optimum_thread(min_flow, max_flow, min_voltage, max_voltage, target_potential, pressure, gas, target, filename, flow_curve):
    global BREAKALL
    BREAKALL = False
    flow_backup = form.plot_device.carbon_flow_array
    efficiency_backup = form.plot_device.efficiency_array_reduced
    if (pressure):
        if (gas == "ox"):
            transfer_ox(target_pressure=pressure)
        if (gas == "blank"):
            transfer_blank(target_pressure=pressure)
    if (target):
        load_target(target)
        for i in range(WAIT_FOR_TARGET_CHANGE):
            if (BREAKALL):
                BREAKALL = False
                return
            time.sleep(1)
            print "\rwaiting: ", WAIT_FOR_TARGET_CHANGE - i,
        if (get_extracted_current() > 5e-6):
            if (BREAKALL):
                BREAKALL = False
                return
            set_le12_range(10e-6)
        while (get_extracted_current() > .5e-6):
            if (BREAKALL):
                BREAKALL = False
                return
            print "\rwait for low current: ", get_extracted_current(),
            time.sleep(1)
    drive(min_flow, kickstart=True, default_current=min_flow)
    open_ams_valve()
    while KICKSTART:
        if (BREAKALL):
            BREAKALL = False
            return
        time.sleep(10)

    ams_device.set_target_voltage(min_voltage)
    ams_device.set_extraction_voltage(target_potential - min_voltage)

    time.sleep(3)
    if (get_extracted_current() > 10e-6):
        set_le12_range(10e-6)

    for i in range(120):
        time.sleep(1)
        print "\rwaiting: ", 120 - i,
    print "\n"

    open_v2_valve()
    open_pump_valve()

    form.plot_device.carbon_flow_array = flow_backup
    form.plot_device.efficiency_array_reduced = efficiency_backup
    with open("measurements/" + TIMEDATE() + "_" + filename + "_voltage_flow_map.txt", "w") as f:
        outer_efficiency_queue = Queue(5)
        best_flow = 0.
        best_voltage = 0.
        best_efficiency = 0.
        for flow in arange(min_flow, max_flow, .1):
            print "%.2f mug/min --> ..." % (flow),
            drive(flow)
            time.sleep(10)
            inner_efficiency_queue = Queue(3)
            optimal_voltage = 0.
            max_efficiency = 0.
            for voltage in arange(min_voltage, max_voltage, .1):
                if (BREAKALL):
                    BREAKALL = False
                    return
                ams_device.set_target_voltage(voltage)
                ams_device.set_extraction_voltage(target_potential - voltage)
                time.sleep(10)
                eff = get_current_efficiency()
                print "\r%.2f mug/min --> %.2f kV --> %.2f %%" % (flow, voltage, eff * 100.), "." * int(eff * 100. * 5.), "     ",
                if (eff > max_efficiency):
                    max_efficiency = eff
                    optimal_voltage = voltage
                elif (inner_efficiency_queue.all_greater(eff)):
                    break
                inner_efficiency_queue.put(eff)
            print >> f, "%.2f mug/min --> %.2f kV --> %.2f %%" % (flow, optimal_voltage, max_efficiency * 100.), "#" * int(max_efficiency * 100. * 5.)
            print "\r%.2f mug/min --> %.2f kV --> %.2f %%" % (flow, optimal_voltage, max_efficiency * 100.), "#" * int(max_efficiency * 100. * 5.)
            form.plot_device.carbon_flow_array = flow_backup
            form.plot_device.efficiency_array_reduced = efficiency_backup
            form.plot_device.carbon_flow_array.append(flow)
            form.plot_device.efficiency_array_reduced.append(max_efficiency * 100.)
            flow_backup = form.plot_device.carbon_flow_array
            efficiency_backup = form.plot_device.efficiency_array_reduced

            min_voltage = optimal_voltage - .8
            if (max_efficiency > best_efficiency):
                best_flow = flow
                best_voltage = optimal_voltage
                best_efficiency = max_efficiency
            if outer_efficiency_queue.all_greater(max_efficiency):
                break
            outer_efficiency_queue.put(max_efficiency)

        drive(best_flow)
        ams_device.set_target_voltage(best_voltage)
        ams_device.set_extraction_voltage(target_potential - best_voltage)
        print "Ended."
        if (flow_curve):
            measure_efficiency_curve()


def find_optimum(min_flow=.5, max_flow=2., min_voltage=4., max_voltage=10., target_potential=35.19, pressure=500, gas="blank", target=None, filename="", flow_curve=False):
    thread_voltage_flow_opt_thread = threading.Thread(target=find_optimum_thread, args=(
        min_flow,
        max_flow,
        min_voltage,
        max_voltage,
        target_potential,
        pressure,
        gas,
        target,
        filename,
        flow_curve))
    thread_voltage_flow_opt_thread.name = "find optimum voltage and flow thread"
    thread_voltage_flow_opt_thread.start()
    append_thread(thread_voltage_flow_opt_thread)


def optimize_voltage_and_flow_thread(start_flow, min_flow, max_flow, min_voltage, max_voltage, target_potential, pressure, gas, target):
    if (pressure):
        if (gas == "ox"):
            transfer_ox(target_pressure=pressure)
        if (gas == "blank"):
            transfer_blank(target_pressure=pressure)
    if (target):
        load_target(target)
        for i in range(WAIT_FOR_TARGET_CHANGE):
            time.sleep(1)
            print "\rwaiting: ", WAIT_FOR_TARGET_CHANGE - i,
        print "\n"
    drive(start_flow, kickstart=True, default_current=start_flow)
    open_ams_valve()
    while KICKSTART:
        time.sleep(10)
    for i in range(120):
        time.sleep(1)
        print "\rwaiting: ", 120 - i,
    print "\n"
    max_efficiency = 0.
    opt_voltage = 0.

    print "1. Optimize Voltage"
    ams_device.set_target_voltage(min_voltage)
    ams_device.set_extraction_voltage(target_potential - min_voltage)
    for i in range(60):
        time.sleep(1)
        print "\rwaiting: ", 60 - i,
    print "\n"
    with open("measurements/" + TIMEDATE() + "_voltage_flow_optimize.txt", "w") as f:
        print >> f, "flow: ", start_flow, "\n"
        print >> f, "target voltage, efficiency percentage"
        print >> f, "-------------------------------------"
        for target_voltage in arange(min_voltage, max_voltage, .1):
            ams_device.set_target_voltage(target_voltage)
            ams_device.set_extraction_voltage(target_potential - target_voltage)
            time.sleep(10)
            eff = get_current_efficiency()
            print >> f, target_voltage, eff * 100.
            print "%.2f kV --> %.2f %%" % (target_voltage, eff * 100.), "#" * int((eff * 100.) * 5.)
            if (eff > max_efficiency):
                max_efficiency = eff
                opt_voltage = target_voltage
        ams_device.set_target_voltage(opt_voltage)
        ams_device.set_extraction_voltage(target_potential - opt_voltage)
        print "optimal voltage: ", opt_voltage

        print "\n2. Optimize Flow"
        measure_efficiency_curve(min_flow, max_flow, True)
        time.sleep(1)
        form.plot_device.reset()

        time.sleep(10)
        while (SWIPE_DRIVE):
            time.sleep(1)
        flow_efficiency = zip(form.plot_device.carbon_flow_array, form.plot_device.efficiency_array_reduced)

        max_eff = 0.
        opt_flow = 0.
        print >> f, "\n\ntarget voltage: ", opt_voltage, "\n"
        print >> f, "mug/min carbon, efficiency percentage"
        print >> f, "-------------------------------------"
        for flow, eff in flow_efficiency:
            print >> f, flow, eff
            print "%.2f mug/min --> %.2f %%" % (flow, eff), "#" * int((eff) * 5.)
            if (eff > max_eff):
                max_eff = eff
                opt_flow = flow
        drive(opt_flow)

        max_efficiency = 0.
        final_opt_voltage = 0.

        print "\n3. Optimize Voltage"
        ams_device.set_target_voltage(min_voltage)
        ams_device.set_extraction_voltage(target_potential - min_voltage)
        time.sleep(60.)
        print >> f, "\n\nflow: ", opt_flow, "\n"
        print >> f, "target voltage, efficiency percentage"
        print >> f, "-------------------------------------"
        for target_voltage in arange(opt_voltage - .5, opt_voltage + .5, .1):
            ams_device.set_target_voltage(target_voltage)
            ams_device.set_extraction_voltage(target_potential - target_voltage)
            time.sleep(10)
            eff = get_current_efficiency()
            print >> f, target_voltage, eff
            print "%.2f kV --> %.2f %%" % (target_voltage, eff * 100.), "#" * int((eff * 100.) * 5.)
            if (eff > max_efficiency):
                max_efficiency = eff
                final_opt_voltage = target_voltage
        ams_device.set_target_voltage(final_opt_voltage)
        ams_device.set_extraction_voltage(target_potential - final_opt_voltage)

        print "\nbest settings:"
        print "flow = ", opt_flow
        print "target voltage = ", final_opt_voltage
        print "efficiency = ", max_efficiency * 100.

        print >> f, "\nbest settings:"
        print >> f, "flow = ", opt_flow
        print >> f, "target voltage = ", final_opt_voltage
        print >> f, "efficiency = ", max_efficiency * 100.
    print "Ended."


def optimize_voltage_and_flow(start_flow=1., min_flow=.5, max_flow=1.7, min_voltage=3.5, max_voltage=7., target_potential=35.19, pressure=500., gas="blank", target=None):
    thread_opt_voltage_flow_thread = threading.Thread(target=optimize_voltage_and_flow_thread, args=(
        start_flow,
        min_flow,
        max_flow,
        min_voltage,
        max_voltage,
        target_potential,
        pressure,
        gas,
        target))
    thread_opt_voltage_flow_thread.name = "optimize voltage and flow thread"
    thread_opt_voltage_flow_thread.start()
    append_thread(thread_opt_voltage_flow_thread)


def swipe_drive(l, r, waiting_time=30):
    global SWIPE_DRIVE, TARGET_MUG_PER_MINUTE
    if (SWIPE_DRIVE):
        SWIPE_DRIVE = False
        TARGET_MUG_PER_MINUTE = l
        time.sleep(35)
    SWIPE_DRIVE = True
    thread.start_new_thread(swipe_drive_thread, (l, r, waiting_time))


def swipe_drive_thread(l, r, waiting_time):
    global DRIVE, TARGET_MUG_PER_MINUTE, SWIPE_DRIVE, OPTIMIZE
    print "Swipe Started"
    SWIPE_DRIVE = True
    OPTIMIZE = False
    steps = [l + i / 10. * (r - l) for i in xrange(11)]
    steps += [r - i / 10. * (r - l) for i in xrange(11)]
    while (DRIVE) and (SWIPE_DRIVE):
        for target_current in steps:
            if (DRIVE) and (SWIPE_DRIVE):
                TARGET_MUG_PER_MINUTE = target_current
                time.sleep(waiting_time)
    SWIPE_DRIVE = False
    print "swipe ended."


def drive_thread(kickstart=False, default_current=1.4):
    """ starts in new thread """
    global TARGET_MUG_PER_MINUTE, DRIVE, GET_STATUS, CURRENT_AMPERE, CURRENT_EFFICIENCY, KICKSTART, SPARKS

    lock = threading.Lock()
    start_time = time.clock()
    KICKSTART = kickstart

    target_p2 = carbon_mug_per_min_to_mbar(TARGET_MUG_PER_MINUTE)
    if target_p2 > 3000.:
        target_p2 = 3000.
        print "Target Pressure (%.1f mbar) to high. Going to 3000 mbar." % (target_p2),
    DRIVE = True
    next_learn_time = 0.

    discharge = False
    while DRIVE:
        if (KICKSTART) and (not kickstart):                                     # kickstart == False --> start normal drive
            time.sleep(5)
            KICKSTART = False
        if (kickstart) and (get_extracted_current() < MIN_CURRENT):             # LE12 < MIN_CURRENT --> increase gas flow
            time.sleep(5)
            if (TARGET_MUG_PER_MINUTE < 3.5) and (
                    not carbon_mug_per_min_to_mbar(TARGET_MUG_PER_MINUTE + .05) > 3000.):
                TARGET_MUG_PER_MINUTE += .05
        elif (kickstart):                                                       # LE12 > MIN_CURRENT --> kickstart = False ; reduce gas flow
            kickstart = False
            TARGET_MUG_PER_MINUTE = default_current

        target_p2 = carbon_mug_per_min_to_mbar(TARGET_MUG_PER_MINUTE)
        if target_p2 > 3000.:
            target_p2 = 3000.
        current_p2 = p2.get_pressure()
        CURRENT_AMPERE = get_extracted_current()
        CURRENT_EFFICIENCY = get_current_efficiency() * 100.

        if (form.plot_device) and (not form.plot_device.updating):
            _carbon_current = get_carbon_mug_per_min()
            form.plot_device.updating = True
            form.plot_device.current_carbon_current = [_carbon_current]
            form.plot_device.current_efficiency = [CURRENT_EFFICIENCY]
            form.plot_device.time_array.append(time.clock())
            form.plot_device.le12_array.append(CURRENT_AMPERE)
            form.plot_device.efficiency_array.append(CURRENT_EFFICIENCY)
            form.plot_device.mass_flow_array.append(_carbon_current)
            he12 = current_device.he12_current
            if (he12 == 0.) or (CURRENT_AMPERE < (form.plot_device.le12_array[-1]) * .75):
                form.plot_device.d13c_array.append(0.)
                form.plot_device.d13c_smooth_array.append(0.)
                if (not kickstart) and (not discharge):
                    SPARKS += 1
                    discharge = True
                    print "\rdischarge @ %i : %.2f sparks / 10 minutes" % (
                        time.clock(),
                        SPARKS / (time.clock() - start_time) * 600.
                    )
            else:
                form.plot_device.d13c_array.append((current_device.he13current / he12 / OnlineAnalysis.R13VPDB - 1.) * 1000.)
                form.plot_device.d13c_smooth_array.append(.05 * form.plot_device.d13c_array[-1] + .95 * (form.plot_device.d13c_smooth_array[-1] if len(form.plot_device.d13c_smooth_array) > 0 else 0.))
                discharge = False
            form.plot_device.updating = False

        if (current_p2 < target_p2 - 10.) or (current_p2 > target_p2 + 10.):
            if (volumes_device.pos < 93.5):
                new_pos = current_p2 * (volumes_device.pos - 95.) / target_p2 + 95.
                pos = goto(.0 * volumes_device.pos + 1. * new_pos)
            else:
                if (current_p2 < target_p2 - 10.):
                    goto(volumes_device.pos + .1)
            if pos == -1:
                DRIVE = False
        if GET_STATUS:
            print "\r%.1f mm, P2/Target: %.1f / %.1f mbar (%.2f mug/min). %.2f%%. %.1e A" % (
                volumes_device.pos,
                current_p2,
                target_p2,
                TARGET_MUG_PER_MINUTE,
                get_current_efficiency() * 100.,
                get_extracted_current()),
        time.sleep(.15)
    print "Measurement Stopped"

    return 0


def goto_thread(pos):
    thread_goto = threading.Thread(target=goto, args=(pos,), name="goto thread")
    thread_goto.start()
    append_thread(thread_goto)


def goto(pos, speed=None):
    global WORKING, STATUS, MOVING
    while MOVING:
        time.sleep(1)
    MOVING = True
    WORKING = True
    STATUS = "syringe to %.1f mm" % (pos)
    pos_old = volumes_device.pos
    if speed:
        syringe_device.set_speed(speed)
    if pos < 94.7:
        if pos < 0.:
            pos = 0.
        if pos > pos_old:
            for i in linspace(pos_old, pos, 100):
                volumes_device.goto(i)
                if volumes_device.p2 > 2900.:
                    break
            thread_goto_new_pos = threading.Thread(target=goto_new_position, args=(pos_old, i))
            thread_goto_new_pos.name = "goto new pos thread"
            thread_goto_new_pos.start()
            append_thread(thread_goto_new_pos)

            syringe_device.goto(i)
            pos = i
        else:
            thread_goto_new_pos = threading.Thread(target=goto_new_position, args=(pos_old, pos))
            thread_goto_new_pos.name = "goto new pos thread"
            thread_goto_new_pos.start()
            append_thread(thread_goto_new_pos)
            syringe_device.goto(pos)
    else:
        for i in linspace(pos_old, 95, 100):
            volumes_device.goto(i)
            if volumes_device.p2 > 2900.:
                break
        thread_goto_new_pos = threading.Thread(target=goto_new_position, args=(pos_old, i))
        thread_goto_new_pos.name = "goto new pos thread"
        thread_goto_new_pos.start()
        append_thread(thread_goto_new_pos)

        syringe_device.goto(i)
        pos = -1
    volumes_device.p2 = p2.get_pressure()
    WORKING = False
    STATUS = ""
    if speed:
        syringe_device.set_speed(10)
    MOVING = False
    return pos


def goto_new_position(last_pos, pos):
    if last_pos < pos:
        r = range(int(last_pos), int(pos) + 1)
    else:
        r = range(int(last_pos), int(pos) - 1, -1)
    for i in r:
        volumes_device.goto(i)
        form.slider_syringe.setValue(i)
        time.sleep(.1)
    volumes_device.goto(pos)


def fake_crack():
    open_pump_valve()
    open_v2_valve()
    open_he_valve(.02)
    time.sleep(.5)
    close_v2_valve()
    time.sleep(5)
    close_pump_valve()


def transfer_ox(mixture=None, target_pressure=200., target_mixture=None, target_mass=None):
    """ Ox-II Gas at Port 4 from Selector Valve """
    global STATUS
    STATUS = "transfer ox"
    if not mixture:
        mixture = MIXTURE_OX
    transfer_sample_gas("ox", mixture, target_pressure, target_mixture, target_mass)
    volumes_device.set_mixture(mixture)
    STATUS = ""


def transfer_blank(mixture=None, target_pressure=500., target_mixture=None, target_mass=None):
    """ Blank Gas at Port 3 from Selector Valve """
    global STATUS
    STATUS = "transfer blank"
    if not mixture:
        mixture = MIXTURE_BLANK
    transfer_sample_gas("blank", mixture, target_pressure, target_mixture)
    volumes_device.set_mixture(mixture)
    STATUS = ""


def transfer_sample_gas(port, mixture, target_pressure=1300., target_mixture=None, target_mass=None):
    global WORKING
    WORKING = True
    print "Transfer Sample Gas."
    if (target_mixture) and (target_mixture > mixture):
        print "Target Mixture > Original Mixture!"
        target_mixture = None
    mixture /= 100.
    set_selector_valve(port)
    close_all_valves()
    syringe_valve_to_ams()
    he_vac_to_he()
    open_v2_valve()
    time.sleep(5)
    he_vac_to_vac()
    open_pump_valve()
    syringe_valve_to_cracker()
    goto(0)
    # perform_offset_correction()
    time.sleep(20)
    close_all_valves()
    time.sleep(.5)
    # goto(0)
    if (port == "4") or (port == "ox"):
        print "Open V9 Valve"
        open_v9_valve()
    elif (port == "3") or (port == "blank"):
        print "Open V10 Valve"
        open_v10_valve()
    time.sleep(.5)
    p1_old = p1.get_pressure()
    print "P1/P2: ", p1_old, p2.get_pressure()
    time.sleep(2)
    while p1.get_pressure() > p1_old + 10.:
        print "\rPressure = ", p1_old,
        time.sleep(1)
        p1_old = p1.get_pressure()
    if (not target_mixture):
        pos = 95. * (1. - target_pressure / p1_old)
        print "P1/P2: ", p1.get_pressure(), p2.get_pressure()
        print "\nGo to %.1f mm" % (pos)
        goto(pos)
        print "P1/P2: ", p1.get_pressure(), p2.get_pressure()
        open_v2_valve()
        time.sleep(1)
        print "Open V2"
        print "P1/P2: ", p1.get_pressure(), p2.get_pressure()
        for i in xrange(1000):
            if p1.get_pressure() > p1_old - 100.:
                break
            print "\rPressure = ", p1.get_pressure(),
            time.sleep(.1)
        close_v2_valve()
        close_v9_valve()
        close_v10_valve()
    else:
        global SYRINGE_MIXING_POSITION
        mixture_orig = mixture
        """
        for p in xrange(SYRINGE_MIXING_POSITION, 95):
            volumes_device.reset()
            volumes_device.goto(p)
            volumes_device.p1 = HE_MINIMAL_PRESSURE
            volumes_device.p2 = p1_old
            volumes_device.setMixture(mixture_orig)
            pos, mixture = volumes_device.testMixToPercentage(targetMixture)
            print p, mixture
            if (mixture > 0) and (mixture < targetMixture):
                volumes_device.reset()
                print "Syringe to %.2f mm." % (p)
                goto(p)
                break
        """
        goto(SYRINGE_MIXING_POSITION)
        volumes_device.reset()
        open_v2_valve()
        time.sleep(5)
        close_v2_valve()
        close_v9_valve()
        close_v10_valve()
        print "\nP1/P2: ", p1.get_pressure(), p2.get_pressure()
        set_selector_valve("C")
        close_ams_valve()
        syringe_valve_to_ams()
        open_v2_valve()
        open_pump_valve()
        time.sleep(5)
        close_pump_valve()
        close_v2_valve()
        print "\nP1/P2: ", p1.get_pressure(), p2.get_pressure()
        open_he_valve()
        p1_pressure = p1.get_pressure()
        while (p1_pressure < HE_MINIMAL_PRESSURE):
            print "\rP1 He: ", p1_pressure,
            time.sleep(1)
            p1_pressure = p1.get_pressure()
        print "\n"
        close_he_valve()
        syringe_valve_to_cracker()
        p2_pressure = p2.get_pressure()
        volumes_device.p2 = p2_pressure
        volumes_device.m2 = p2_pressure * mixture_orig / Volumes.MUG_C_TO_MBAR * (volumes_device.v2 + volumes_device.v3)
        p1_pressure = p1.get_pressure()
        volumes_device.p1 = p1_pressure
        pos, mixture = volumes_device.test_mix_to_percentage(target_mixture)
        print "\nP1/P2: ", p1.get_pressure(), p2.get_pressure()
        print "Syringe to %.2f mm" % (pos)
        goto(pos)
        p2_pressure_old = p2.get_pressure()
        print "\nP1/P2: ", p1.get_pressure(), p2_pressure_old
        open_v2_valve(.5)
        volumes_device.open_v2(p1.get_pressure())
    syringe_valve_to_ams()
    p2_pressure_new = p2.get_pressure()
    print "\nP1/P2: ", p1.get_pressure(), p2_pressure_new
    print "goto 0 mm"
    goto(0)
    p2_pressure = p2.get_pressure()
    print "P1/P2: ", p1.get_pressure(), p2_pressure
    volumes_device.p2 = (p2_pressure)
    if target_mixture:
        mixture = p2_pressure_old * mixture_orig / p2_pressure_new
        print "mixture: %.2f %%" % (mixture * 100.)
    volumes_device.m2 = (p2_pressure * mixture / Volumes.MUG_C_TO_MBAR * volumes_device.v2)
    volumes_device.p2 = p2_pressure
    WORKING = False


def crack():
    """ returns mugC or None """
    global STATUS
    STATUS = "cracking"
    close_v2_valve()
    open_pump_valve()
    # openHeValve(3)
    open_v2_valve()
    pos = 95 * (1. + (VOL_PIPE - VOL_CRACKER_CLEAN) / (VOL_SYRINGE))
    print "Syringe to: ", pos
    goto(pos)
    time.sleep(5)
    close_v2_valve()
    # print "V1 - (V2 + V3) = ", volumes_device.v1_clean - (volumes_device.v2 + volumes_device.v3)
    for i in xrange(3):
        p = p1.get_pressure()
        if (p > 1.) or (p < -1.):
            if (not perform_offset_correction()) and (i == 2):
                return -1
        else:
            break
    time.sleep(5)
    close_all_valves()
    for i in xrange(10):
        print "cracking.."
        if FAKECRACK:
            fake_crack()
        else:
            valves_device.set_pin_value(Valves.valves["crack"], 1)
            valves_device.set_pin_value(Valves.valves["crack"], 0)
        time.sleep(1)
        if p1.get_pressure() > p + 2:
            time.sleep(2)
            p1_pressure = p1.get_pressure()
            mass = mbar_to_mug_c(p1_pressure)
            open_v2_valve()
            time.sleep(15)
            p1Pressure_new = p1.get_pressure()
            # korrekturfaktor x
            x = p1Pressure_new / (p1_pressure - p1Pressure_new)
            volumes_device.v1 = volumes_device.v1_clean * x
            Volumes.a.v1 = volumes_device.v1_clean * x
            print "p1, p1', x, m, m': ", p1_pressure, p1Pressure_new, x, mass, mbar_to_mug_c(p1_pressure)
            print "Volume reduced from cracked glass by:  %.2f%%" % ((1. - x) * 100.)
            goto(0)
            return mbar_to_mug_c(p1_pressure)
    print "Could not Crack Sample."
    STATUS = ""
    return -1


def crack_and_transfer():
    global STATUS
    STATUS = "crack and transfer"
    # cleanGis()
    volumes_device.verbose = False
    set_selector_valve("C")
    close_all_valves()    # sets also syringe valve to cracker
    mass = crack()
    if mass == -1:
        return -1
    volumes_device.set_barbon_mass(mass)
    print "1. Diffuse %.1f mug Sample to Syringe." % (mass)
    open_v2_valve(10)
    volumes_device.open_v2()
    # he1, he2, pos1, pos2, ratio, mix1, mix2 = Volumes.findBestTransfer(mass)
    while p1.get_pressure() < 200:
        print "\r2. Fill Cracker with He: %.1f mbar." % (p1.get_pressure()),
        open_he_valve(.01)
        time.sleep(1)
    time.sleep(2)
    Volumes.VERBOSE = False
    print "\r2. Fill Cracker with He: %.1f mbar. Done" % (p1.get_pressure())
    he1, he2, pos1, pos2, ratio, mix1, mix2 = Volumes.find_best_transfer(mass, p1.get_pressure())
    print "3. Find Best Transfer Procedure:  \n\tSyringe to %.1f mm --> open V2 (%.1f %% Mixture)\n\tHe to %.1f mbar\n\tSyringe to %.1f mm --> open V2 (%.1f %% Mixture)" % (pos1, mix1 * 100., he2, pos2, mix2 * 100.)
    print "\t==> Transfered: %.1f %%\n" % (ratio * 100.)
    volumes_device.verbose = False
    volumes_device.add_he(he1)
    print "4. Goto Position %.1f mm --> open V2" % (pos1)
    goto(pos1)
    volumes_device.goto(pos1)
    open_v2_valve(.5)
    volumes_device.open_v2(p1.get_pressure())
    # das hier optimieren
    timestep = (1. if he2 > 1000. else .02)
    while p1.get_pressure() < he2:
        print "\r5. Fill Cracker with He: %.1f mbar." % (p1.get_pressure()),
        open_he_valve(.02)
        time.sleep(1)
    time.sleep(2)
    print "\r5. Fill Cracker with He: %.1f mbar. Done" % (p1.get_pressure())
    he1, he2, pos1, pos2, ratio, mix1, mix2 = Volumes.find_best_transfer(mass, he1, p1.get_pressure(), mix1)
    volumes_device.add_he(he2)
    print "New Position re-calculated to %.1f mm" % (pos2)
    print "6. Goto Position %.1f mm --> open V2" % (pos2)
    goto(pos2)
    volumes_device.goto(pos2)
    open_v2_valve(.5)
    volumes_device.open_v2(p1.get_pressure())
    print "mix=%.1f%%, %.1f%% transfered to syringe." % (volumes_device.get_mixture() * 100., volumes_device.m2 / mass * 100.)
    print "p2 simulated = %.1f, p2 real = %.1f\n" % (volumes_device.p2, p2.get_pressure())
    goto(0)
    volumes_device.goto(0)
    he_vac_to_vac()
    close_ams_valve()
    syringe_valve_to_ams()
    print "Syringe is ready."
    return mass
    STATUS = ""


def close():
    print "shutting down.."
    global STATUS
    global DRIVE, BREAKALL, EXIT
    STATUS = "closing.."
    DRIVE = False
    BREAKALL = True
    EXIT = True
    close_all_valves()
    open_v2_valve()
    # neural_net.stop = True
    # neural_net.save()
    print "0 / 5 (save data)",
    pickle.dump({"p1_offset": p1.offset, "p2_offset": p2.offset}, open("settings.b", "wb"))
    try:
        form.close_gui()
    except:
        pass
    print "\r1 / 5 (disconnect diolan board)",
    valves_device.close()
    print "\r2 / 5 (disconnect pressure sensors)",
    pressure_device.close()
    print "\r3 / 5 (disconnect syringe device)  ",
    syringe_device.close()
    print "\r4 / 5 (disconnect ams tcp/ip)     ",
    current_device.close()
    if TCPIP:
        ams_device.close()
    print "\r5 / 5 (disconnect arduino)    "
    switch_device.close()
    STATUS = ""


class MainWindow(QtGui.QMainWindow, design.Ui_MainWindow):
    name = "gui thread"
    lock = threading.Lock()
    ams = False
    pump = False
    v2 = False
    v9 = False
    v10 = False
    he = False
    syringe_to_ams = False
    syringe_moving = False
    last_pos = volumes_device.pos
    cracker_open = False
    syringe_driving = False
    counter = 5
    time_to_go = 0.
    cleaning = False

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.plot_device = Plotter.Device()
        self.plot_device.name = "plotter thread"
        self.setupUi(self)

        self.lbl_pos.setText("-- mm")

        self.btn_ams.clicked.connect(self.amsValve_clicked)
        self.btn_view.clicked.connect(self.show_batch_clicked)
        self.btn_pump.clicked.connect(self.pump_clicked)
        self.btn_hevac_he.clicked.connect(self.heVacHe_clicked)
        self.btn_hevac_vac.clicked.connect(self.heVacVac_clicked)
        self.btn_v2.clicked.connect(self.v2_clicked)
        self.btn_offset.clicked.connect(self.offset_clicked)
        self.btn_selector_cracker.clicked.connect(self.selector_cracker_clicked)
        self.btn_selector_blank.clicked.connect(self.selector_blank_clicked)
        self.btn_selector_ox.clicked.connect(self.selector_ox_clicked)
        self.btn_he.clicked.connect(self.he_clicked)
        self.btn_transfer_blank.clicked.connect(self.transfer_blank_clicked)
        self.btn_transfer_ox.clicked.connect(self.transfer_ox_clicked)
        self.btn_start_drive.clicked.connect(self.drive_clicked)
        self.btn_syringe_valve.clicked.connect(self.syringe_valve_clicked)
        self.btn_optimize.clicked.connect(self.optimize_clicked)
        self.btn_clean.clicked.connect(self.clean_clicked)
        self.btn_blank.clicked.connect(self.blank_clicked)
        self.btn_ox.clicked.connect(self.ox_clicked)
        self.btn_cracker_open.clicked.connect(self.open_cracker_clicked)
        self.btn_cracker_crack_transfer.clicked.connect(self.crack_transfer_clicked)
        self.btn_batch_start.clicked.connect(self.batch_start_clicked)
        self.btn_batch_stop.clicked.connect(self.batch_stop_clicked)
        self.btn_batch_next.clicked.connect(self.batch_next_clicked)
        self.btn_execute.clicked.connect(self.execute_clicked)
        self.btn_clear_plot.clicked.connect(clear_plot)
        self.btn_mix_blank.clicked.connect(self.mix_blank_clicked)
        self.btn_mix_ox.clicked.connect(self.mix_ox_clicked)
        self.btn_save_data.clicked.connect(self.save_data_clicked)
        self.btn_fc_offset.clicked.connect(self.fc_offset_clicked)
        self.btn_plot_ratios.clicked.connect(self.plot_ratios_clicked)
        self.btn_attach_window.clicked.connect(self.moveEvent)

        for i in range(1, 9):
            exec("self.btn_cracker%i.clicked.connect(self.cracker%i_clicked)" % (i, i))

        self.slider_syringe.sliderPressed.connect(self.syringe_pressed)
        self.slider_syringe.sliderReleased.connect(self.syringe_released)

        self.line_10.setFrameShadow(0)
        self.line_5.setFrameShadow(0)
        self.line_4.setFrameShadow(0)
        self.line_cracker2.setFrameShadow(0)
        self.line_v2syringe.setFrameShadow(0)
        self.line_syringe.setFrameShadow(0)
        self.line_11.setFrameShadow(0)

        self.spinbox_carbon_current.valueChanged.connect(self.carbon_current_changed)
        self.spinbox_p2.valueChanged.connect(self.p2_changed)

        self.highlighter = syntax.Highlighter(self.txtedit_batch_in.document())

        self.set_button_colors()
        # self.plot_device.start()
        self.start_timer()
        self.plot_device.start_timer()
        append_thread(self.plot_device)

        self.btn_plot_ratios.setChecked(True)
        self.plot_ratios_clicked()
        self.btn_view.setChecked(True)
        self.show_batch_clicked()
        self.btn_attach_window.setChecked(True)
        self.moveEvent(None)

        if (CHECK_SYSTEM):
            thread_check_system = threading.Thread(target=check_system, name="check system thread")
            thread_check_system.start()
            append_thread(thread_check_system)

    def closeEvent(self, e):
        print "closing GUI"
        self.close_gui()
        e.accept()

    def start_timer(self):
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(100)

    def get_syringe_position(self, last_pos, pos):
        self.syringe_driving = True
        if last_pos < pos:
            r = range(int(last_pos), int(pos) + 1)
        else:
            r = range(int(last_pos), int(pos) - 1, -1)
        for i in r:
            self.slider_syringe.setValue(i)
            self.lbl_pos.setText("%.1f mm" % i)
            time.sleep(.1)
        self.syringe_driving = False

    def getColor(self):
        p = p2.get_pressure()
        r0, g0, b0 = 173, 216, 230
        r1, g1, b1 = 183, 172, 232
        x = .33 + p / 3000.

        try:
            stylesheet = """QSlider::groove:horizontal {
            border: 1px solid #999999;
            height: 18px;

            border-radius: 9px;
            }

            QSlider::handle:horizontal {
            width: 18px;
            }

            QSlider::add-page:qlineargradient {
            background: darkgrey;
            border-top-right-radius: 9px;
            border-bottom-right-radius: 9px;
            border-top-left-radius: 0px;
            border-bottom-left-radius: 0px;
            }

            QSlider::sub-page:qlineargradient {
            background: #%02x%02x%02x;
            border-top-right-radius: 0px;
            border-bottom-right-radius: 0px;
            border-top-left-radius: 0px;
            border-bottom-left-radius: 0px;
            }""" % (r0 + x * (r1 - r0), g0 + x * (g1 - g0), b0 + x * (b1 - b0))

            self.slider_syringe.setStyleSheet(stylesheet)
        except:
            pass

        # self.slider_syringe.repaint()

    def animate(self):
        if (not Plotter.ALIVE):
            print "Closing GUI"
            self.timer.stop()
            self.close()

        if (not BATCH_RUNNING):
            self.txtedit_batch_in.setEnabled(True)
        if (DRIVE):
            # self.time_to_go = .1 * (p2.getPressure() * 100. * volumes_device.v2 / (K * T) / getParticleCurrent()) + .90 * self.time_to_go
            # self.lock.acquire()
            self.time_to_go = volumes_device.m2 / TARGET_MUG_PER_MINUTE * 60.
            if (CURRENT_ERROR):
                title = "LE12/HE12/HE13: %.1e/%.1e/%.1e A | %.1f %% | +-%.2f %% | %s" % (get_extracted_current(), current_device.he12_current, current_device.he13current, CURRENT_EFFICIENCY, CURRENT_ERROR * 100., time_formatted(self.time_to_go))
            else:
                title = "LE12/HE12/HE13: %.1e/%.1e/%.1e A | %.1f %% | %s" % (get_extracted_current(), current_device.he12_current, current_device.he13current, CURRENT_EFFICIENCY, time_formatted(self.time_to_go))
            # self.lock.release()
        else:
            title = "LE12/HE12/HE13: %.1e/%.1e/%.1e A" % (get_extracted_current(), current_device.he12_current, current_device.he13current)
        self.setWindowTitle(title)
        # self.lock.acquire()
        self.plot_device.win.setWindowTitle(title)
        # self.lock.release()
        if (STATUS):
            # self.lock.acquire()
            self.lbl_working.setText(STATUS)
            # self.lock.release()
        # self.lock.acquire()
        pos = volumes_device.pos
        # self.lock.release()
        if (not self.syringe_moving) and (int(self.last_pos) != self.slider_syringe.value()):
            # self.lock.acquire()
            self.slider_syringe.setValue(int(pos))
            # self.lock.release()
        self.last_pos = pos
        self.lbl_pos.setText("%.1f mm" % pos)
        # self.lock.acquire()
        self.lcd_p1.display(p1.get_pressure())
        self.lcd_p2.display(p2.get_pressure())
        self.lcd_m2.display(volumes_device.m2)
        self.lcd_mixture.display(volumes_device.mixture * 100.)
        # self.lock.release()
        if (not MOVING) and (self.ams) and (self.syringe_to_ams):
            # self.lock.acquire()
            volumes_device.p2 = p2.get_pressure()
            # self.lock.release()
            volumes_device.update_m2()
        if (WORKING) and (STATUS) == "":
            # self.lock.acquire()
            self.lbl_working.setText("working..")
            # self.lock.release()
        if (TARGET_MUG_PER_MINUTE != self.spinbox_carbon_current.value()):
            # self.lock.acquire()
            self.spinbox_carbon_current.setValue(TARGET_MUG_PER_MINUTE)
            # self.lock.release()
        self.getColor()
        if (not CRACKER_CHANGE):
            if (switch_device.switch == SWITCHON) and (not self.cracker_open):
                close_v2_valve()
                open_cracker()
                self.cracker_open = True
            elif (switch_device.switch == SWITCHOFF) and (self.cracker_open):
                close_cracker()
                self.cracker_open = False
            if (switch_device.button == 2):
                switch_device.button = 0
                if (not self.cracker_open):
                    self.clean_clicked()
                else:
                    thread_check_vacuum = threading.Thread(target=check_vacuum, name="check vacuum thread")
                    thread_check_vacuum.start()
                    append_thread(thread_check_vacuum)
        if (self.counter / 5 == 1):
            self.counter = 0
            self.set_button_colors()
            """
            if (valves_device.getPinValue(Valves.switch) == 1) and (not self.cracker_open):
                openCracker()
                self.cracker_open = True
            elif (valves_device.getPinValue(Valves.switch) == 0) and (self.cracker_open):
                closeCracker()
                self.cracker_open = False
            """
        self.counter += 1

    def set_button_colors(self):
        he = "background-color: #bb99ff; border: 1px solid #999999"
        vac = "background-color: #99bbff; border: 1px solid #999999"
        ams = "background-color: #c79d70; border: 1px solid #999999"
        v2 = ams
        drive = "background-color: #70c783; border: 1px solid #999999"
        optimize = ""
        offset = "background-color: #7093c7; border: 1px solid #999999"
        closed = "background-color: #dfdfdf; border: 1px solid #999999;"
        closed_flat = "background-color: #dfdfdf; border: 1px solid #999999;"
        not_in_position = "background-color: #ff0000"
        selector = offset  # "background-color: #70c789; border: 1px solid #999999;"
        blank = offset
        ox = offset
        cracker = offset
        cleaning = False

        # if DOING_OFFSET:
        #     self.btn_offset.setFrameShadow(offset)
        # else:
        #     self.btn_offset.setFrameShadow(closedflat)
        if (self.chk_in_position.isChecked()):
            self.chk_in_position.setStyleSheet("")
        else:
            self.chk_in_position.setStyleSheet(not_in_position)

        if (CRACKER_POSITION > 0) and (self.chk_in_position.isChecked()):
            for i in range(1, CRACKER_POSITION):
                exec("self.btn_cracker%i.setStyleSheet(closed_flat)" % i)
                exec("self.btn_cracker%i.setEnabled(False)" % i)
            for i in range(CRACKER_POSITION, 9):
                exec("self.btn_cracker%i.setStyleSheet(closed_flat)" % i)
                exec("self.btn_cracker%i.setEnabled(True)" % i)
            exec("self.btn_cracker%i.setStyleSheet(cracker)" % CRACKER_POSITION)
        else:
            for i in range(1, 9):
                exec("self.btn_cracker%i.setStyleSheet(closed_flat)" % i)
                exec("self.btn_cracker%i.setEnabled(True)" % i)

        if DRIVE:
            self.btn_start_drive.setChecked(True)
        else:
            self.btn_start_drive.setChecked(False)

        if OPTIMIZE:
            self.btn_optimize.setChecked(True)
        else:
            self.btn_optimize.setChecked(False)

        if valves_device.get_pin_value(Valves.valves["open"]) == 1:
            self.btn_cracker_open.setChecked(True)
            self.cracker_open = True
        else:
            self.btn_cracker_open.setChecked(False)
            self.cracker_open = False

        if valves_device.get_pin_value(Valves.valves["V0"]) == 1:
            self.btn_syringe_valve.setText("")
            self.btn_syringe_valve.setStyleSheet("background-image:url(./button2.png)")
            self.syringe_to_ams = True
        else:
            self.btn_syringe_valve.setText("")
            self.btn_syringe_valve.setStyleSheet("background-image:url(./button.png)")
            self.syringe_to_ams = False

        if valves_device.get_pin_value(Valves.valves["blank"]) == 1:
            self.btn_blank.setStyleSheet(blank)
            self.v10 = True
        else:
            self.btn_blank.setStyleSheet(closed)
            self.v10 = False

        if valves_device.get_pin_value(Valves.valves["ox"]) == 1:
            self.btn_ox.setStyleSheet(ox)
            self.v9 = True
        else:
            self.btn_ox.setStyleSheet(closed)
            self.v9 = False

        if valves_device.get_pin_value(Valves.selectorValve["C"]) == 1:
            self.btn_selector_cracker.setStyleSheet(selector)
            self.line_cracker1.setFrameShadow(0)
            self.line_bottles1.setFrameShadow(48)
            self.line_bottles2.setFrameShadow(48)
        else:
            self.btn_selector_cracker.setStyleSheet(closed_flat)
            self.line_cracker1.setFrameShadow(48)

        if valves_device.get_pin_value(Valves.selectorValve["3"]) == 1:
            self.btn_selector_blank.setStyleSheet(selector)
            self.line_bottles1.setFrameShadow(0)
            self.line_bottles2.setFrameShadow(48)
        else:
            self.btn_selector_blank.setStyleSheet(closed_flat)

        if valves_device.get_pin_value(Valves.selectorValve["4"]) == 1:
            self.btn_selector_ox.setStyleSheet(selector)
            self.line_bottles1.setFrameShadow(0)
            self.line_bottles2.setFrameShadow(0)
        else:
            self.btn_selector_ox.setStyleSheet(closed_flat)

        if valves_device.get_pin_value(Valves.valves["he"]) == 1:
            self.btn_he.setStyleSheet(he)
            self.he = True
        else:
            self.btn_he.setStyleSheet(closed_flat)
            self.he = False

        if valves_device.get_pin_value(Valves.valves["pump"]) == 1:
            self.line_pump.setFrameShadow(0)
            self.btn_pump.setStyleSheet(vac)
            self.pump = True
        else:
            self.line_pump.setFrameShadow(48)
            self.btn_pump.setStyleSheet(closed)
            self.pump = False

        if valves_device.get_pin_value(Valves.valves["ams"]) == 1:
            self.btn_ams.setStyleSheet(ams)
            self.line_ams.setFrameShadow(0)
            self.ams = True
        else:
            self.btn_ams.setStyleSheet(closed_flat)
            self.line_ams.setFrameShadow(48)
            self.ams = False

        if valves_device.get_pin_value(Valves.valves["he-vac"]) == 1:
            self.line_hevac_he.setFrameShadow(0)
            self.line_hevac_vac.setFrameShadow(48)
            self.btn_hevac_he.setStyleSheet(he)
            self.btn_hevac_vac.setStyleSheet(closed)
        else:
            self.line_hevac_he.setFrameShadow(48)
            self.line_hevac_vac.setFrameShadow(0)
            self.btn_hevac_vac.setStyleSheet(vac)
            self.btn_hevac_he.setStyleSheet(closed)

        if valves_device.get_pin_value(Valves.valves["V2"]) == 1:
            self.btn_v2.setStyleSheet(v2)
            self.v2 = True
        else:
            self.btn_v2.setStyleSheet(closed_flat)
            self.v2 = False

    def moveEvent(self, e=None):
        if self.btn_attach_window.isChecked():
            self.plot_device.attach(self.frameGeometry())

    def plot_ratios_clicked(self):
        self.plot_device.set_plot_ratios(self.btn_plot_ratios.isChecked())

    def fc_offset_clicked(self):
        global CURRENT_OFFSET
        if self.btn_fc_offset.isChecked():
            CURRENT_OFFSET = get_extracted_current()
        else:
            CURRENT_OFFSET = 0.
        print CURRENT_OFFSET

    def save_data_clicked(self):
        c_flow, eff = self.plot_device.carbon_flow_array, self.plot_device.efficiency_array_reduced
        t, le12 = self.plot_device.time_array, self.plot_device.le12_array
        eff_full = self.plot_device.efficiency_array
        d13c = self.plot_device.d13c_array
        mass_flow = self.plot_device.mass_flow_array
        with open("measurements/" + TIMEDATE() + "_manually saved (%i).txt" % (time.clock()), "w") as f2:
            f2.write("[pos]%s\n" % ("---"))
            f2.write("[name]%s\n" % ("---"))
            f2.write("[mass cracked]%s\n" % ("---"))
            f2.write("[mass measured]%s\n" % ("---"))
            f2.write("[mix]%s\n" % ("---"))
            f2.write("[c flow vs efficiency]\n")
            f2.writelines(["%f " % (a) for a in c_flow])
            print >> f2, "\n",
            f2.writelines(["%f " % (a) for a in eff])
            f2.write("\n[time in s vs cup current in A vs efficiency in % vs delta c13 in permille vs mass flow in mug/min]\n")
            f2.writelines(["%f " % (a) for a in t])
            print >> f2, "\n",
            f2.writelines(["%f " % (a) for a in le12])
            print >> f2, "\n",
            f2.writelines(["%f " % (a) for a in eff_full])
            print >> f2, "\n",
            f2.writelines(["%f " % (a) for a in d13c])
            print >> f2, "\n",
            f2.writelines(["%f " % (a) for a in mass_flow])
        print "data saved"

    def mix_blank_clicked(self):
        volumes_device.p2 = p2.get_pressure()
        volumes_device.set_mixture(MIXTURE_BLANK)
        volumes_device.update_m2()

    def mix_ox_clicked(self):
        volumes_device.p2 = p2.get_pressure()
        volumes_device.set_mixture(MIXTURE_OX)
        volumes_device.update_m2()

    def carbon_current_changed(self):
        global TARGET_MUG_PER_MINUTE
        self.plot_device.carbon_flow_array.append(get_carbon_mug_per_min())
        self.plot_device.efficiency_array_reduced.append(get_current_efficiency() * 100.)
        TARGET_MUG_PER_MINUTE = self.spinbox_carbon_current.value()
        if volumes_device.get_mixture() > 0:
            self.spinbox_p2.setValue(carbon_mug_per_min_to_mbar(TARGET_MUG_PER_MINUTE))

    def p2_changed(self):
        if volumes_device.get_mixture() > 0:
            hold_pressure(self.spinbox_p2.value())

    def execute_clicked(self):
        try:
            exec(str(self.lineedit_execute.text()))
        except Exception, e:
            print e
            print "no valid command."
            pass
        self.lineedit_execute.setText("")

    def cracker1_clicked(self):
        p = 1
        if self.chk_in_position.isChecked():
            go_to_cracker_position(p)
        else:
            set_cracker_position(p)
            self.chk_in_position.setChecked(True)

    def cracker2_clicked(self):
        p = 2
        if self.chk_in_position.isChecked():
            go_to_cracker_position(p)
        else:
            set_cracker_position(p)
            self.chk_in_position.setChecked(True)

    def cracker3_clicked(self):
        p = 3
        if self.chk_in_position.isChecked():
            go_to_cracker_position(p)
        else:
            set_cracker_position(p)
            self.chk_in_position.setChecked(True)

    def cracker4_clicked(self):
        p = 4
        if self.chk_in_position.isChecked():
            go_to_cracker_position(p)
        else:
            set_cracker_position(p)
            self.chk_in_position.setChecked(True)

    def cracker5_clicked(self):
        p = 5
        if self.chk_in_position.isChecked():
            go_to_cracker_position(p)
        else:
            set_cracker_position(p)
            self.chk_in_position.setChecked(True)

    def cracker6_clicked(self):
        p = 6
        if self.chk_in_position.isChecked():
            go_to_cracker_position(p)
        else:
            set_cracker_position(p)
            self.chk_in_position.setChecked(True)

    def cracker7_clicked(self):
        p = 7
        if self.chk_in_position.isChecked():
            go_to_cracker_position(p)
        else:
            set_cracker_position(p)
            self.chk_in_position.setChecked(True)

    def cracker8_clicked(self):
        p = 8
        if self.chk_in_position.isChecked():
            go_to_cracker_position(p)
        else:
            set_cracker_position(p)
            self.chk_in_position.setChecked(True)

    def batch_start_clicked(self):
        text = self.txtedit_batch_in.toPlainText()
        ans = QtGui.QMessageBox.Ok
        if ("ox" not in text):
            msgbox = QtGui.QMessageBox()
            msgbox.setWindowTitle("warning")
            msgbox.setText("no ox standard(s) marked")
            msgbox.setInformativeText("press OK to continue or mark your ox sample(s) with the keyword 'ox'.")
            msgbox.setStandardButtons(QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
            ans = msgbox.exec_()
        if (not self.chk_in_position.isChecked()):
            msgbox = QtGui.QMessageBox()
            msgbox.setWindowTitle("warning")
            msgbox.setText("Cracker position undefined")
            msgbox.setInformativeText("Select active cracker position and start again!")
            msgbox.setStandardButtons(QtGui.QMessageBox.Cancel)
            ans = msgbox.exec_()
        if (ans == QtGui.QMessageBox.Ok):
            self.txtedit_batch_in.setEnabled(False)
            self.list_batch_list.clear()
            load_measurement_file(txt=str(text))
            start_batch_measurement()

    def batch_stop_clicked(self):
        global BATCH_RUNNING
        BATCH_RUNNING = False
        stop_measurement()
        self.txtedit_batch_in.setEnabled(True)

    def batch_next_clicked(self):
        global DRIVE
        DRIVE = False

    def crack_transfer_clicked(self):
        if not WORKING:
            thread_crack_and_transfer = threading.Thread(target=crack_and_transfer, name="crack and transfer thread")
            thread_crack_and_transfer.start()
            append_thread(thread_crack_and_transfer)

    def open_cracker_clicked(self):
        if self.cracker_open:
            close_cracker()
        else:
            open_cracker()
            self.chk_in_position.setChecked(False)

    def blank_clicked(self):
        if not self.v10:
            open_v10_valve()
        else:
            close_v10_valve()

    def ox_clicked(self):
        if not self.v9:
            open_v9_valve()
        else:
            close_v9_valve()

    def clean_clicked(self):
        if not self.cleaning:
            self.cleaning = True
            thread_clean_gis = threading.Thread(target=clean_gis, name="clean gis thread")
            thread_clean_gis.start()
            append_thread(thread_clean_gis)

    def optimize_clicked(self):
        if OPTIMIZE:
            stop_optimize()
        else:
            start_optimize()

    def syringe_released(self):
        self.syringe_moving = False
        thread_goto = threading.Thread(target=goto, args=(self.slider_syringe.value(),))
        thread_goto.name = "goto thread"
        thread_goto.start()
        append_thread(thread_goto)

    def syringe_pressed(self):
        self.syringe_moving = True

    def syringe_valve_clicked(self):
        if self.syringe_to_ams:
            syringe_valve_to_cracker()
        else:
            syringe_valve_to_ams()
        self.set_button_colors()

    def drive_clicked(self):
        if not DRIVE:
            start_measurement()
        else:
            stop_measurement()

    def he_clicked(self):
        if self.he:
            close_he_valve()
        else:
            open_he_valve()
        self.set_button_colors()

    def transfer_blank_clicked(self):
        if not WORKING:
            thread_transfer_blank = threading.Thread(target=transfer_blank, name="transfer blank thread")
            thread_transfer_blank.start()
            append_thread(thread_transfer_blank)

    def transfer_ox_clicked(self):
        if not WORKING:
            thread_transfer_ox = threading.Thread(target=transfer_ox, name="transfer ox thread")
            thread_transfer_ox.start()
            append_thread(thread_transfer_ox)

    def selector_cracker_clicked(self):
        global WORKING
        WORKING = True
        set_selector_valve("C")
        WORKING = False
        self.set_button_colors()

    def selector_blank_clicked(self):
        global WORKING
        WORKING = True
        set_selector_valve("3")
        WORKING = False
        self.set_button_colors()

    def selector_ox_clicked(self):
        global WORKING
        WORKING = True
        set_selector_valve("4")
        WORKING = False
        self.set_button_colors()

    def offset_clicked(self):
        if not WORKING:
            thread_perform_offset_correction = threading.Thread(
                target=perform_offset_correction,
                name="offset correction thread")
            thread_perform_offset_correction.start()
            append_thread(thread_perform_offset_correction)

    def v2_clicked(self):
        if not self.v2:
            open_v2_valve()
        else:
            close_v2_valve()
        self.set_button_colors()

    def pump_clicked(self):
        if not self.pump:
            open_pump_valve()
        else:
            close_pump_valve()
        self.set_button_colors()

    def heVacHe_clicked(self):
            he_vac_to_he()
            self.set_button_colors()

    def heVacVac_clicked(self):
            he_vac_to_vac()
            self.set_button_colors()

    def show_batch_clicked(self):
        if self.btn_view.isChecked():
            self.resize(self.width(), 749)
        else:
            self.resize(self.width(), 470)
        self.moveEvent(None)

    def amsValve_clicked(self):
        self.ams = not self.ams
        if self.ams:
            open_ams_valve()
        else:
            close_ams_valve()
        self.set_button_colors()

    def close_gui(self):
        self.timer.stop()
        try:
            self.plot_device.closeMe()
        except:
            pass
        self.close()


if __name__ == '__main__':
    if ("--rescue" in sys.argv):
        CHECK_SYSTEM = False
        print "\nvalves and syringe in original position."
        print "load last measurement with load_analysis(filename)\n"

    app = QtGui.QApplication(sys.argv)
    form = MainWindow()

    if (SHOW_OPEN_THREADS):
        thread_save_open_threads = threading.Thread(
            target=save_open_threads_thread,
            name="save open threads thread"
        )
        thread_save_open_threads.start()
        append_thread(thread_save_open_threads)

    print "Weather: %.1f deg C / %.1f deg C" % (
        p1.get_temperature(),
        p2.get_temperature()
    )
    try:
        print "loading last offset values"
        settings = pickle.load(open("settings.b", "rb"))
        p1.offset = settings["p1_offset"]
        p2.offset = settings["p2_offset"]
    except:
        print "something went wrong"

    if (not TCPIP) or (FAKECRACK) or (SKIPCLEANING) or (not MAILER):
        print "\nWARNING:  TEST MODE!!!\n------------------------"
        print "TCPIP: ", TCPIP
        print "FAKECRACK: ", FAKECRACK
        print "SKIPCLEANING: ", SKIPCLEANING
        print "CHECK_SYSTEM: ", CHECK_SYSTEM
        print "MAILER: ", MAILER

    form.show()

    T = 273.15 + p2.get_temperature()

    app.exec_()
    close()

print "Have a nice day :)"

del app

if (SHOW_OPEN_THREADS):
    print threading.enumerate()

sys.exit()
