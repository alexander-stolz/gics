import OnlineAnalysis
from sys import argv
import os
import pickle

dev = OnlineAnalysis.Device("")

main_menu = """1. load analysis file
2. load fsires file
3. load current analysis directory
4. add sample from current file
5. plot he12
6. plot custom
7. .analysis to _report.txt
8. print samples
9. create report
0. print this menu

quit with ctrl + c
"""

print main_menu

filemode = ""

while True:
    try:
        selection = input("> ")
    except:
        print "only numbers [0-9] allowed. quit with ctrl + c"
        continue
    try:
        if (selection == 0):
            print main_menu
        elif (selection == 1):
            fn = raw_input("filename > ")
            dev.load_analysis_file(fn)
            filemode = "analysis"
        elif (selection == 2):
            fn = raw_input("filename > ")
            dev.loadFsiresFile(fn)
            filemode = "fsires"
        elif (selection == 3):
            dn = raw_input("directory > ")
            dev.loadCurrentAnalysis(dn)
            filemode = "ca"
        elif (selection == 4):
            start, stop, name = raw_input("start,stop,name > ").split(",")
            if (filemode == "fsires"):
                dev.addSampleF(int(start), int(stop), name)
            if (filemode == "ca"):
                dev.addSampleCA(int(start), int(stop), name)
        elif (selection == 5):
            if (filemode == "fsires"):
                dev.plotF()
            if (filemode == "ca"):
                dev.plotCA()
            if (filemode == "analysis"):
                dev.plot()
        elif (selection == 6):
            key = raw_input("key > ")
            try:
                if (filemode == "fsires"):
                    dev.plotF(key)
                if (filemode == "ca"):
                    dev.plotCA(key)
                if (filemode == "analysis"):
                    dev.plot(key)
            except Exception as e:
                print "error: ", e
        elif (selection == 7):
            fn = raw_input("filename > ")
            try:
                samples = pickle.load(open(fn, "rb"))
                print "opened as binary"
            except:
                samples = pickle.load(open(fn, "r"))
                print "opened as ascii"
            with open(fn + "_report.txt", "w") as f:
                for i, sample in enumerate(samples):
                    print i, sample["name"]
                    print >> f, i, sample["name"]
                    for key in sample.keys():
                        print >> f, "\t[%s]" % key, sample[key]
                        print "\t[%s]" % key, sample[key]
                    print "\n"
        elif (selection == 8):
            for i, sample in enumerate(dev.samples):
                print i, sample["name"], sample["blocks"][0], sample["blocks"][-1]
        elif (selection == 9):
            break
    except Exception as e:
        print e
        continue

filename = raw_input("filename > ")

try:
    os.stat("measurements")
except:
    os.mkdir("measurements")

report = dev.createReport(filename)
report += "<p><img src='%s.png' /></p>" % (filename)

open("measurements/" + filename + ".html", "w").write(report)
