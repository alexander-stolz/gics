import GIS
import time

V_s = GIS.VOL_SYRINGE

try:
    with open("volumes_corrected.txt", "a") as f:
        for i in xrange(10, 21, 5):
            t = i
            print t, "s"
            GIS.clean_gis()
            GIS.close_all_valves()
            GIS.open_he_valve(t)
            p1 = GIS.p1.get_pressure()
            GIS.goto(95)
            GIS.open_v2_valve()
            time.sleep(10)
            p2 = GIS.p1.get_pressure()
            GIS.goto(0)
            time.sleep(10)
            p3 = GIS.p1.get_pressure()
            # http://bit.ly/2fZjvt1
            V_c = p2 * p3 * V_s / (p1 * p2 - p1 * p3)
            V_r = p3 * V_s * (p1 - p2) / (p1 * (p2 - p3))
            print "%.2f mbar:\tV_c = %.2e\tV_r = %.2e" % (p1, V_c, V_r)
            print >> f, t, V_c, V_r, p1, p2, p3
except Exception as e:
    print e

GIS.close()
