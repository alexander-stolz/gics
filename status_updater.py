import Ams
import time

filename = "status.txt"

dev = Ams.AmsDevice()

try:
    while True:
        with open(filename, "w") as f:
            print >> f, "Extraction Voltage: ", dev.get_extraction_voltage()
            print >> f, "Target Voltage: ", dev.get_target_voltage()
            print >> f, "Cs Temperature: ", dev.get_cs_temperature()
        time.sleep(60)
finally:
    dev.close()
