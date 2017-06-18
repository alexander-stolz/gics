import Valves
import time

dev = Valves.Device()

lastvalues = [0] * 32

#while raw_input("end? > ").strip() != "end":
try:
	print "listening"
	while True:
		changed = False
		values = [0] * 32
		for i in xrange(0, 32):
			# print "\r", i,
			values[i] = dev.getPinValue(i)
			if lastvalues[i] != values[i]:
				print i, values[i]
				changed = True
		time.sleep(.1)
		lastvalues = values
		if changed:
			print "---"
			#break
finally:
	dev.close()

"""
16 = 1: selector to ams

11 = 0
12 = 1 : V3 to 3
"""