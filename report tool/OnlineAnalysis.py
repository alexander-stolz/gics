import glob
import struct
from math import sqrt
import pickle
from numpy import array, mean
from pylab import *
import Mailer

keyword_ox = "ox"
keyword_blank = "blank"
charge_state = 4.
RATIO_OX = 1.59168e-12
R13VPDB = 1.12372e-2
D13OX = -18.81                                                                                      # permill difference from VPDB
F14OX = 1.3408                                                                                      # pmC / 100


class Device():
    filenames = []
    directory = ""
    samples = []
    title = ""
    notes = ""
    target_position = 0

    def __init__(self, directory=None):
        self.directory = directory
        self.samples = []

    def reset(self):
        self.samples = []
        self.check_and_update()

    def check_and_update(self, new=False, samplename=""):
        " adds new block data if availabe. adds label if sample is measured "
        try:
            filenames = glob.glob(self.directory + "blck*.blk")
            if (filenames[-1] in self.filenames):
                return None
            else:
                for fn in filenames:
                    if (fn not in self.filenames):
                        self.filenames.append(fn)
                        if (samplename):
                            # try:
                                r14, e14, r13 = self.update(fn, new, samplename=samplename)
                                new = False
                            # except:
                            #     print "error reading: " + fn
                if (samplename):
                    return r14, e14, r13
        except Exception, e:
            pass

    def update(self, filename, new=False, samplename=""):
        try:
            data = open(filename, "rb").read()

            # roi1_cps = c14_counts / live_time
            c14_counts = struct.unpack_from("I", data[8:12])[0]
            live_time, c14_cps = struct.unpack_from("dd", data[28:44])

            he13 = struct.unpack_from("d", data[48:56])[0]
            he12 = struct.unpack_from("d", data[60:68])[0]

            r14 = struct.unpack_from("d", data[84:92])[0]
            r13 = struct.unpack_from("d", data[100:108])[0]

            target_current = struct.unpack_from("f", data[132:136])[0]

            if (new) or (len(self.samples) == 0) or (self.samples[-1]["name"] != samplename):
                self.samples.append({})
                self.samples[-1]["name"] = samplename
                self.samples[-1]["target_position"] = self.target_position
                self.samples[-1]["counts"] = [c14_counts]
                self.samples[-1]["relativeError"] = [1. / (sqrt(c14_counts) if c14_counts > 0 else 1.)]
                self.samples[-1]["detectorLiveTime"] = [live_time]
                self.samples[-1]["14cps"] = [c14_cps]
                self.samples[-1]["he13"] = [he13]
                self.samples[-1]["he12"] = [he12]
                self.samples[-1]["r14"] = [r14]
                self.samples[-1]["r13"] = [r13]
                self.samples[-1]["targetCurrent"] = [target_current]
                self.samples[-1]["isOx"] = keyword_ox in samplename
                self.samples[-1]["isBlank"] = keyword_blank in samplename
                self.samples[-1]["blocks"] = [int(filename[-9:-4]) + 1]
            else:
                self.samples[-1]["counts"].append(c14_counts)
                self.samples[-1]["relativeError"].append(1. / (sqrt(c14_counts) if c14_counts > 0 else 1.))
                self.samples[-1]["detectorLiveTime"].append(live_time)
                self.samples[-1]["14cps"].append(c14_cps)
                self.samples[-1]["he13"].append(he13)
                self.samples[-1]["he12"].append(he12)
                self.samples[-1]["r14"].append(r14)
                self.samples[-1]["r13"].append(r13)
                self.samples[-1]["targetCurrent"].append(target_current)
                self.samples[-1]["blocks"].append(int(filename[-9:-4]) + 1)
            if (c14_counts > 0):
                e14 = r14 / sqrt(c14_counts)
            else:
                e14 = r14
            return r14, e14, r13
        except Exception, e:
            print "Error reading block data:\n", e

    def get_last_sample_ratio(self):
        try:
            return mean(self.samples[-1]["r14"])
        except:
            return -1

    def get_last_sample_target_current(self):
        try:
            return mean(self.samples[-1]["targetCurrent"]), std(self.samples[-1]["targetCurrent"])
        except:
            return -1

    def get_last_sample_he12(self):
        try:
            return mean(self.samples[-1]["he12"]), std(self.samples[-1]["he12"])
        except:
            return -1

    def get_last_sample_counts(self):
        try:
            return sum(self.samples[-1]["counts"])
        except:
            return -1

    def get_last_sample_blocks(self):
        try:
            return self.samples[-1]["blocks"][0], self.samples[-1]["blocks"][-1]
        except:
            return -1

    def create_report(self, filename=None, online=True):
        " returns multiline string. prickes to file if filename is provided. "
        " no blank correction yet "

        report = ""

        try:
            r14Ox = []
            r14Blank = []

            e14Ox = []
            e14Blank = []

            c14Ox = 0
            c14Blank = 0

            r13Ox = []

            c12WeightOx = []
            c12WeightBlank = []
            he12WeightOx_blocks = []
            he12WeightBlank_blocks = []

            r14Ox_bf = []
            r14Ox_bf_blocks = []

            print "summing up counts",

            for i, sample in enumerate(self.samples):
                print "\r", i, sample["name"], sample["blocks"][0], sample["blocks"][-1],
                self.samples[i]["sample_sum14"] = sum(sample["counts"])
                self.samples[i]["sample_sum12"] = sum(
                    array(sample["he12"]) * array(sample["detectorLiveTime"]) / 1.602176565e-19 / charge_state)
                self.samples[i]["sample_sum13"] = sum(
                    array(sample["he13"]) * array(sample["detectorLiveTime"]) / 1.602176565e-19 / charge_state)
                self.samples[i]["sample_relativeError"] = 1. / sqrt(self.samples[i]["sample_sum14"])
                self.samples[i]["sample_r14"] = self.samples[i]["sample_sum14"] / self.samples[i]["sample_sum12"]
                self.samples[i]["sample_r13"] = self.samples[i]["sample_sum13"] / self.samples[i]["sample_sum12"]
                self.samples[i]["sample_targetCurrent"] = mean(sample["targetCurrent"])

                if sample["isOx"]:
                    r14Ox.append(self.samples[i]["sample_r14"])
                    e14Ox.append(self.samples[i]["sample_relativeError"])
                    c14Ox += self.samples[i]["sample_sum14"]
                    r13Ox.append(self.samples[i]["sample_r13"])
                    c12WeightOx.append(self.samples[i]["sample_sum12"])
                    he12WeightOx_blocks += sample["he12"]

                if sample["isBlank"]:
                    r14Blank.append(self.samples[i]["sample_r14"])
                    e14Blank.append(self.samples[i]["sample_relativeError"])
                    c14Blank += self.samples[i]["sample_sum14"]
                    c12WeightBlank.append(self.samples[i]["sample_sum12"])
                    he12WeightBlank_blocks += sample["he12"]

            # substract blank value
            r14Blank = array(r14Blank)
            c12WeightBlank = array(c12WeightBlank)

            print "\rsubstracting blanks",

            do_blank = (len(r14Blank) > 0)
            if (do_blank):
                blank_mean = sum(r14Blank * c12WeightBlank) / sum(c12WeightBlank)
                for i, sample in enumerate(self.samples):
                    self.samples[i]["corrected_r14_b_blocks"] = []
                    if sample["isBlank"]:
                        self.samples[i]["corrected_r14_b_blocks"] = self.samples[i]["r14"]
                        self.samples[i]["corrected_r14_b"] = self.samples[i]["sample_r14"]
                    else:
                        self.samples[i]["corrected_r14_b"] = self.samples[i]["sample_r14"] - blank_mean
                        for b, r14 in enumerate(sample["r14"]):
                            self.samples[i]["corrected_r14_b_blocks"].append(r14 - blank_mean)
            else:
                for i, sample in enumerate(self.samples):
                    self.samples[i]["corrected_r14_b"] = self.samples[i]["sample_r14"]
                    self.samples[i]["corrected_r14_b_blocks"] = self.samples[i]["r14"]

            # fractionation correction
            r13Ox = array(r13Ox)
            c12WeightOx = array(c12WeightOx)

            print "\rfractionation correction",

            do_frac = (len(r13Ox) > 0)
            if (do_frac):
                r13Ox_mean = sum(r13Ox * c12WeightOx) / sum(c12WeightOx)
                for i, sample in enumerate(self.samples):
                    self.samples[i]["corrected_d13C_blocks"] = []
                    self.samples[i]["corrected_r14_bf_blocks"] = []
                    for b, r13 in enumerate(array(sample["he13"]) / array(sample["he12"])):
                        self.samples[i]["corrected_d13C_blocks"].append((r13 * (1. + D13OX / 1000.) / r13Ox_mean - 1.) * 1000.)
                        self.samples[i]["corrected_r14_bf_blocks"].append(self.samples[i]["corrected_r14_b_blocks"][b] * (.975 / (1. + self.samples[i]["corrected_d13C_blocks"][b] / 1000.)) ** 2)
                    self.samples[i]["corrected_d13C"] = (self.samples[i]["sample_r13"] * (1. + D13OX / 1000.) / r13Ox_mean - 1.) * 1000.
                    self.samples[i]["corrected_r14_bf"] = self.samples[i]["corrected_r14_b"] * (.975 / (1. + self.samples[i]["corrected_d13C"] / 1000.)) ** 2
                    if sample["isOx"]:
                        r14Ox_bf.append(self.samples[i]["corrected_r14_bf"])
                        for b, r14_bf in enumerate(sample["corrected_r14_bf_blocks"]):
                            r14Ox_bf_blocks.append(r14_bf)
            else:
                for i, sample in enumerate(self.samples):
                    self.samples[i]["corrected_d13C_blocks"] = []
                    self.samples[i]["corrected_r14_bf_blocks"] = []
                    self.samples[i]["corrected_d13C"] = (self.samples[i]["sample_r13"] / R13VPDB - 1.) * 1000.
                    self.samples[i]["corrected_r14_bf"] = self.samples[i]["corrected_r14_b"]
                    for b, r13 in enumerate(array(sample["he13"]) / array(sample["he12"])):
                        self.samples[i]["corrected_d13C_blocks"].append((r13 / R13VPDB - 1.) * 1000.)
                    self.samples[i]["corrected_r14_bf_blocks"] = self.samples[i]["corrected_r14_b_blocks"]

            # standard normalisation
            r14Ox_bf = array(r14Ox_bf)
            e14Ox = array(e14Ox)
            r14Ox_bf_blocks = array(r14Ox_bf_blocks)
            he12WeightOx_blocks = array(he12WeightOx_blocks)

            print "\rox",

            do_ox = (len(r14Ox_bf) > 0)
            if (do_ox):
                r14Ox_bf_mean = sum(r14Ox_bf / (e14Ox ** 2)) / sum(1. / (e14Ox ** 2))
                r14Ox_bf_mean_blocks = sum(r14Ox_bf_blocks * he12WeightOx_blocks) / sum(he12WeightOx_blocks)
                for i, sample in enumerate(self.samples):
                    self.samples[i]["corrected_f14c_blocks"] = []
                    self.samples[i]["corrected_f14c"] = F14OX / r14Ox_bf_mean * self.samples[i]["corrected_r14_bf"]
                    for b, r14_bf in enumerate(sample["corrected_r14_bf_blocks"]):
                        self.samples[i]["corrected_f14c_blocks"].append(F14OX / r14Ox_bf_mean_blocks * r14_bf)
                    self.samples[i]["corrected_f14c_mean"] = sum(array(self.samples[i]["corrected_f14c_blocks"]) * array(self.samples[i]["he12"])) / sum(self.samples[i]["he12"])
                    self.samples[i]["corrected_d13C_mean"] = sum(array(self.samples[i]["corrected_d13C_blocks"]) * array(self.samples[i]["he12"])) / sum(self.samples[i]["he12"])
            else:
                for i, sample in enumerate(self.samples):
                    self.samples[i]["corrected_f14c"] = 0.
                    self.samples[i]["corrected_f14c_mean"] = 0.
                    self.samples[i]["corrected_d13C_mean"] = sum(array(self.samples[i]["corrected_d13C_blocks"]) * array(self.samples[i]["he12"])) / sum(self.samples[i]["he12"])

            print "\rox2",

            if (do_ox):
                r14Ox = array(r14Ox)
                ratio_ox = sum(r14Ox / (e14Ox ** 2)) / sum(1. / (e14Ox ** 2))
                k = RATIO_OX / ratio_ox
                if (len(r14Ox) == 1):
                    delta_k = k / sqrt(c14Ox)
                else:
                    delta_k = k * (std(r14Ox) / sqrt(len(r14Ox))) / ratio_ox
            else:
                k = 1.
                delta_k = 0.

            print "\rHTML",

            report += "<table cellspacing='5'>"
            report += "<tr><td>measured samples:</td>           <td>%i</td></tr>\n" % (len(self.samples))
            report += "<tr><td>measured ox samples:</td>        <td>%i</td></tr>\n" % (len(r14Ox))
            report += "<tr><td>measured blank samples:</td>     <td>%i</td></tr>\n" % (len(r14Blank))
            if (do_ox):
                report += "<tr><td>correction factor:</td>          <td>%.3f +- %.3f</td></tr>\n\n" % (k, delta_k)
            report += "</table><br /><table cellspacing='5'>"
            report += \
                "<tr><td align='center'>{:^5}</td>"\
                "<td align='center'>{:^9}</td>"\
                "<td align='center'>{:^5}</td>"\
                "<td align='center'>{:^5}</td>"\
                "<td align='center'>{:^7}</td>"\
                "<td align='center'>{:^10}</td>"\
                "<td align='center'>{:^10}</td>"\
                "<td align='center'>{:^10}</td>"\
                "<td align='center'>{:^10}</td>"\
                "<td align='center'>{:^8}</td>"\
                "<td align='center'>{:^15}</td>"\
                "<td align='left'>{}</td></tr>\n".format(
                    "#",
                    "blocks",
                    "Ox",
                    "Blank",
                    "Counts",
                    "measured",
                    "corrected",
                    "d13C",
                    "F14C",
                    "error",
                    "age",
                    "label")

            for i, sample in enumerate(self.samples):
                self.samples[i]["corrected_r14"] = self.samples[i]["sample_r14"] * k
                self.samples[i]["sample_relativeError_corrected"] = sqrt((sample["sample_relativeError"]) ** 2 + (delta_k / k) ** 2)
                self.samples[i]["corrected_r14_error"] = self.samples[i]["corrected_r14"] * self.samples[i]["sample_relativeError_corrected"]

                report += "<tr><td align='center'>{:^5d}</td>"\
                    "<td align='center'>{:>4d}-{:<4d}</td>"\
                    "<td align='center'>{:^5d}</td>"\
                    "<td align='center'>{:^5d}</td>"\
                    "<td align='center'>{:^7d}</td>"\
                    "<td align='center'>{:^10.2e}</td>"\
                    "<td align='center'>{:^10.2e}</td>"\
                    "<td align='center'>{:^10.2f}</td>"\
                    "<td align='center'>{:^10.4f}</td>"\
                    "<td align='center'>{:^6.2f}% </td>"\
                    "<td align='center'>{:>6d} +- {:<5d}</td>"\
                    "<td align='left'>{}</td></tr>\n".format(
                        i,
                        sample["blocks"][0], sample["blocks"][-1],
                        sample["isOx"],
                        sample["isBlank"],
                        sample["sample_sum14"],
                        self.samples[i]["sample_r14"],
                        self.samples[i]["corrected_r14"],
                        self.samples[i]["corrected_d13C"],
                        self.samples[i]["corrected_f14c_mean"],
                        self.samples[i]["sample_relativeError_corrected"] * 100.,
                        (int(-8033. * log(self.samples[i]["corrected_f14c_mean"])) if do_ox else 0), (int(8033. * self.samples[i]["sample_relativeError_corrected"]) if do_ox else 0),
                        sample["name"])

            report += "</table><br />\n"

            if (do_blank):
                report += "[x] blank correction. blank mean: %1.2e<br />\n" % (blank_mean)
            else:
                report += "[ ] no blank correction.<br />\n"
            if (do_frac):
                report += "[x] fractionation correction. d13c ox mean: %1.2f<br />\n" % ((r13Ox_mean / R13VPDB - 1.) * 1000.)
            else:
                report += "[ ] no fractionation correction.<br />\n"
            if (do_ox):
                report += "[x] standard correction. ox mean: %1.2e<br />\n" % (ratio_ox)
            else:
                report += "[ ] no standard correction.<br />\n"

            if filename:
                try:
                    print "\rreport                     ",
                    with open("measurements/" + filename + "_report.txt", "w") as f:
                        f.write(Mailer.formatToPlainText(report))
                    print "\ranalysis                        ",
                    with open("measurements/" + filename + "_analysis.analysis", "wb") as f:
                        pickle.dump(self.samples, f)
                    print "\rpng                                  ",
                    self.savePng("measurements/" + filename + ".png", online=online)
                except Exception, e:
                    print "error while saving report file: ", e

        except Exception, e:
            print "an error occured while creating the report:\n", e

        return report

    def savePng(self, filename, online=True):
        print "\r save png                     ",
        rcParams['figure.figsize'] = 9, 12
        print "\r save png figsize                     ",

        fig, ax = subplots(4, 2)
        print "\r save png subplots                     "

        for i, sample in enumerate(self.samples):
            print i, sample["name"], sample["blocks"][0], sample["blocks"][-1], format(sample["corrected_f14c"], ".3f"), format(sample["corrected_f14c_mean"], ".3f")

        print "\rplot 00",

        # blocks
        ax[0][0].bar(range(len(self.samples)), map(lambda s: len(s["blocks"]), self.samples), align='center', alpha=0.5)
        # ax[0][0].set_xticks(range(len(self.samples)))
        # ax[0][0].set_xticklabels(map(lambda s: s["name"], self.samples))
        ax[0][0].set_xlabel('sample number')
        ax[0][0].set_ylabel('blocks')

        print "\rplot 01",

        # currents
        if (not online) or (not self.filenames):
            for i, sample in enumerate(self.samples):
                ax[0][1].plot(array(sample["he12"]) * 1e6, label=str(i))

            ax[0][1].set_xlabel('blocks')
            ax[0][1].set_ylabel('12C 4+ (muA)')
            # ax[0][1].legend(loc=4)
            ax[0][1].grid()
        else:
            self.addSampleCA(1, len(self.filenames), "everything")
            ax[0][1].plot(self.samples[-1]["blocks"], array(self.samples[-1]["he12"]) * 1e6, "k-")
            ax[0][1].set_xlim(self.samples[-1]["blocks"][0], self.samples[-1]["blocks"][-1])
            self.samples = self.samples[:-1]

            max_he = 0.
            for i, sample in enumerate(self.samples):
                ax[0][1].plot(sample["blocks"], array(sample["he12"]) * 1e6, label=str(i))
                he = array(sample["he12"]).max() * 1e6
                if (he > max_he):
                    max_he = (he if he < 100. else max_he)

            ax[0][1].set_xlabel('block')
            ax[0][1].set_ylabel('12C 4+ (muA)')
            ax[0][1].set_ylim(0., max_he + 1)
            # ax[0][1].legend(loc=4)
            ax[0][1].grid()

        print "\rplot 10",

        # r14
        ax[1][0].errorbar(range(0, len(self.samples)), map(lambda s: s["corrected_r14"], self.samples), map(lambda s: s["corrected_r14_error"], self.samples), fmt="o")
        # ax[1][0].set_xticks(range(1, len(self.samples) + 1))
        # ax[1][0].set_xticklabels(map(lambda s: s["name"], self.samples))
        ax[1][0].set_xlim(-1, len(self.samples))
        ax[1][0].set_xlabel('sample number')
        ax[1][0].set_ylabel('14C / 12C')
        ax[1][0].grid()

        # ratios log
        """
        ax[1][1].errorbar(range(0, len(self.samples)), map(lambda s: s["corrected_r14"], self.samples), map(lambda s: s["corrected_r14_error"], self.samples), fmt="o")
        # ax[1][1].set_xticks(range(1, len(self.samples) + 1))
        # ax[1][1].set_xticklabels(map(lambda s: s["name"], self.samples))
        ax[1][1].set_xlim(-1, len(self.samples))
        ax[1][1].set_xlabel('sample number')
        ax[1][1].set_ylabel('14C / 12C (log scale)')
        ax[1][1].set_yscale("log")
        """

        print "\rplot 11",

        # F14C
        # ax[1][1].plot(range(0, len(self.samples)), map(lambda s: s["corrected_f14c_mean"], self.samples), "bo")
        ax[1][1].errorbar(range(0, len(self.samples)), map(lambda s: s["corrected_f14c_mean"], self.samples), map(lambda s: s["sample_relativeError_corrected"] * s["corrected_f14c_mean"], self.samples), fmt="o")
        ax[1][1].set_xlim(-1, len(self.samples))
        ax[1][1].set_xlabel('sample number')
        ax[1][1].set_ylabel('F14C')
        ax[1][1].grid()

        print "\rplot 20",

        # r14
        r14 = []
        for sample in self.samples:
            r14 += sample["corrected_r14_b_blocks"]
        ax[2][0].plot(r14, "bo", markersize=3)
        ax[2][0].set_xlabel('blocks')
        ax[2][0].set_ylabel('14C / 12C')
        ax[2][0].set_xlim(0, len(r14))
        ax[2][0].grid()

        print "\rplot 21",

        # r14_bf
        r14 = []
        for sample in self.samples:
            r14 += sample["corrected_r14_bf_blocks"]
        ax[2][1].plot(r14, "bo", markersize=3)
        ax[2][1].set_xlabel('blocks')
        ax[2][1].set_ylabel('14C / 12C (frac. corr.)')
        ax[2][1].set_xlim(0, len(r14))
        ax[2][1].grid()

        print "\rplot 30",

        # d13C
        ax[3][0].plot(range(0, len(self.samples)), map(lambda s: s["corrected_d13C_mean"], self.samples), "ko")
        ax[3][0].set_xlim(-1, len(self.samples))
        ax[3][0].set_xlabel('sample number')
        ax[3][0].set_ylabel('d13C')
        ax[3][0].grid()

        print "\rplot 31",

        # r13
        r13 = []
        for sample in self.samples:
            if ["r13"] in sample.keys():
                r13 += sample["r13"]
            else:
                r13 += [sample["he13"][i] / sample["he12"][i] for i in xrange(len(sample["he12"]))]
        ax[3][1].plot(r13, "ko", markersize=3)
        ax[3][1].set_xlabel('blocks')
        ax[3][1].set_ylabel('13C / 12C')
        ax[3][1].set_xlim(0, len(r13))
        ax[3][1].grid()

        print "\rsaving plot"

        fig.tight_layout()
        savefig(filename)

    def load_analysis_file(self, filename):
        try:
            self.samples += pickle.load(open(filename, "rb"))
        except:
            self.samples += pickle.load(open(filename, "r"))
        print "loaded"

    def addSampleF(self, block_first, block_last, samplename):
        #   " add sample from fsires file. load with loadFsiresFile() "
        #   " Blk C14cnts Totalcnts Moleculescnts totalcnts totalcnts LiveTime C14cps C13cur C12cur LE13cur LE12cur C14/C13 C14/C12 C13/C12 C13/LE13 C12/LE12 LE13/LE12 TargetCur Flags "
        #   try:
            c14_counts = int(self.fsires[block_first - 1][1])
            live_time = self.fsires[block_first - 1][6]
            c14_cps = self.fsires[block_first - 1][7]
            he13 = self.fsires[block_first - 1][8]
            he12 = self.fsires[block_first - 1][9]
            r14 = self.fsires[block_first - 1][13]
            r13 = self.fsires[block_first - 1][14]
            target_current = self.fsires[block_first - 1][18]
            block = int(self.fsires[block_first - 1][0])

            self.samples.append({})
            self.samples[-1]["name"] = samplename
            self.samples[-1]["counts"] = [c14_counts]
            self.samples[-1]["relativeError"] = [1. / (sqrt(c14_counts) if c14_counts > 0 else 1.)]
            self.samples[-1]["detectorLiveTime"] = [live_time]
            self.samples[-1]["14cps"] = [c14_cps]
            self.samples[-1]["he13"] = [he13]
            self.samples[-1]["he12"] = [he12]
            self.samples[-1]["r14"] = [r14]
            self.samples[-1]["r13"] = [r13]
            self.samples[-1]["targetCurrent"] = [target_current]
            self.samples[-1]["isOx"] = keyword_ox in samplename
            self.samples[-1]["isBlank"] = keyword_blank in samplename
            self.samples[-1]["blocks"] = [block]

            for i in range(block_first, block_last):
                c14_counts = int(self.fsires[i][1])
                live_time = self.fsires[i][6]
                c14_cps = self.fsires[i][7]
                he13 = self.fsires[i][8]
                he12 = self.fsires[i][9]
                r14 = self.fsires[i][13]
                target_current = self.fsires[i][18]
                block = int(self.fsires[i][0])

                self.samples[-1]["counts"].append(c14_counts)
                self.samples[-1]["relativeError"].append(1. / (sqrt(c14_counts) if c14_counts > 0 else 1.))
                self.samples[-1]["detectorLiveTime"].append(live_time)
                self.samples[-1]["14cps"].append(c14_cps)
                self.samples[-1]["he13"].append(he13)
                self.samples[-1]["he12"].append(he12)
                self.samples[-1]["r14"].append(r14)
                self.samples[-1]["r13"].append(r13)
                self.samples[-1]["targetCurrent"].append(target_current)
                self.samples[-1]["blocks"].append(block)
            self.samples[-1]["sample_sum14"] = [sum(self.samples[-1]["counts"])]
        #   except Exception, e:
        #       print e

    def addSampleCA(self, block_first, block_last, name):
        try:
            self.update(self.filenames[block_first - 1], new=True, samplename=name)
            for i in range(block_first, block_last):
                self.update(self.filenames[i], new=False, samplename=name)
        except Exception, e:
            print e

    def loadFsiresFile(self, filename):
        self.fsires = []
        if (filename.rsplit(".", 1)[-1] != "fsires"):
            filename += ".fsires"
        try:
            txt = open(filename, "r").readlines()
            txt_iter = iter(txt)
            while (txt_iter.next().strip() != "[BLOCK DATA]"):
                pass
            txt_iter.next()
            for line in txt_iter:
                try:
                    self.fsires.append(map(float, line.split()))
                except Exception, e:
                    print "error in line:" % (line), "\n", e
        except Exception, e:
            print e
        print "fsires loaded."

    def loadCurrentAnalysis(self, directory):
        if (directory[-1] != "/") and (directory[-1] != "\\"):
            directory += "/"
        self.filenames = glob.glob(directory + "blck*.blk")
        print "filenames loaded."

    def plotCA(self, key="he12"):
        samples_backup = self.samples
        self.samples = []
        self.addSampleCA(1, len(self.filenames), "name")
        plot(range(1, len(self.filenames) + 1), self.samples[0][key], "k")
        show()
        self.samples = samples_backup

    def plotF(self, key="he12"):
        samples_backup = self.samples
        self.samples = []
        self.addSampleF(1, len(self.fsires), "name")
        plot(range(1, len(self.fsires) + 1), self.samples[0][key], "k")
        show()
        self.samples = samples_backup

    def plot(self, key="he12", fmt="k-"):
        try:
            for sample in self.samples:
                plot(sample["blocks"], sample[key], fmt)
            show()
        except Exception, e:
            print "Error while ploting: ", e

    createReport = create_report
