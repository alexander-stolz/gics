MOL = 6.022e23
KB = 1.3806488e-23
PARTICLES_PER_MUG = 5.014e16
MUG_C_TO_MBAR = 2.0785667684000003e-06    # mbar / mug * m**3

VERBOSE = False

log = lambda msg: open("log.txt", "a").write(str(msg))


class Volumes():
    verbose = VERBOSE
    m1 = 0  # mug
    m2 = 0  # mug
    p1 = 0  # mbar
    p2 = 0  # mbar
    v1_clean = 1.3330e-6  # m ** 3 ; cracker
    v1 = 1.3330e-6
    # v1 = 7.834311e-7  # cracker with glass
    v2 = 2.6861e-6  # m ** 3 ; syringe actual volume
    v3 = 3.175889e-8  # m ** 3 ; pipe
    _v3 = 3.175889e-8  # m ** 3 ; pipe. 0 if syringe valve to ams
    v_syringe = 2.6861e-6  # m ** 3
    pos = 0.  # mm ; Position Spritze
    mixture = 0.00
    p2_test = 0.

    def __init__(self):
        pass

    def set_barbon_mass(self, mass):
        self.m1 = mass
        self.p1 = mass * MUG_C_TO_MBAR / self.v1
        if self.verbose:
            print "m1=%.1f, m2=%.1f, p1=%.1f, p2=%.1f" % (self.m1, self.m2, self.p1, self.p2)

    def set_mixture(self, percentage):
        self.mixture = percentage / 100.
        self.m2 = self.getM2()
        return self.m2

    def getM2(self):
        return self.p2 * self.mixture / MUG_C_TO_MBAR * self.v2

    def update_m2(self):
        self.m2 = self.getM2()

    def goto(self, pos):
        """ fahre spritze auf position """
        if (pos < 0.):
            pos = 0.
        elif (pos < 95.):
            self.p2 = self.p2 * (self.v3 + self.v2) / (self.v3 + self.v_syringe * (95. - pos) / 95.)
            self.v2 = self.v_syringe * (95. - pos) / 95.
            self.pos = pos
        elif (pos >= 95.):
            self.p2 = 0.
            self.v2 = self.v_syringe * (95. - pos) / 95.
            self.pos = pos
            return -1
        if self.verbose:
            print "m1=%.1f, m2=%.1f, p1=%.1f, p2=%.1f" % (self.m1, self.m2, self.p1, self.p2)

    def open_v2(self, p1_new=None):
        """ ventil zwischen cracker und spritze """
        p1_alt = self.p1
        if not p1_new:
            # kompletter ausgleich
            self.p1 = (self.p1 * self.v1 + self.p2 * (self.v2 + self.v3)) / (self.v1 + (self.v2 + self.v3))
            self.p2 = self.p1
        else:
            # v2 nur kurz offen
            self.p1 = p1_new
            self.p2 = (self.v1 * (p1_alt - p1_new) + self.p2 * (self.v2 + self.v3)) / (self.v2 + self.v3)
        delta_m = self.m1 * (1. - self.p1 / p1_alt)
        self.m1 -= delta_m
        self.m2 += delta_m
        self.mixture = self.get_mixture()
        if self.verbose:
            print "ratio=%.1f, m1=%.1f, m2=%.1f, p1=%.1f, p2=%.1f" % (self.get_mixture() * 100., self.m1, self.m2, self.p1, self.p2)

    def testOpenV2(self):
        """ ventil zwischen cracker und spritze """
        p1_alt = self.p1
        p1_test = (self.p1 * self.v1 + self.p2 * (self.v2 + self.v3)) / (self.v1 + (self.v2 + self.v3))
        p2_test = p1_test
        delta_m = self.m1 * (1. - p1_test / p1_alt)
        m1_test = self.m1 - delta_m
        m2_test = self.m2 + delta_m
        return m2_test, p2_test

    def add_he(self, mbar):
        self.p1 = mbar
        if self.verbose:
            print "m1=%.1f, m2=%.1f, p1=%.1f, p2=%.1f" % (self.m1, self.m2, self.p1, self.p2)

    def m2ToMbar(self):
        """ get partial pressure from m2 """
        return self.m2 * MUG_C_TO_MBAR / (self.v2 + self.v3)

    def testM2ToMbar(self, m2_test):
        """ get partial pressure from m2 """
        return m2_test * MUG_C_TO_MBAR / (self.v2 + self.v3)

    def m1ToMbar(self):
        """ get partial pressure from m2 """
        return self.m1 * MUG_C_TO_MBAR / self.v1

    def get_mixture(self):
        try:
            self.mixture = self.m2ToMbar() / self.p2
        except:
            self.mixture = 0.
        return self.mixture

    def testGetMixture(self, m2_test, p2_test):
        return self.testM2ToMbar(m2_test) / p2_test

    def mixToPercentage(self, percentage):
        for j in xrange(900):
            i = j / 10.
            self.goto(i)
            if self.p2 > self.p1 + 200.:
                # print "Not possible."
                break
            m2_test, p2_test = self.testOpenV2()
            mix = self.testGetMixture(m2_test, p2_test)
            # print mix
            if mix > percentage / 100.:
                self.open_v2()
                return i, mix
        return -1, -1

    def test_mix_to_percentage(self, percentage):
        for j in xrange(900):
            i = j / 10.
            self.goto(i)
            if self.p2 > self.p1 + 200.:
                # print "Not possible."
                break
            m2_test, p2_test = self.testOpenV2()
            mix = self.testGetMixture(m2_test, p2_test)
            # print mix
            if mix > percentage / 100.:
                return i, mix
        return -1, -1

    def reset(self):
        self.m1 = 0.
        self.m2 = 0.
        self.p1 = 0.
        self.p2 = 0.
        # self.pos = 0.
        self.v2 = self.v_syringe
        self.v2 = self.v1_clean


def plotMixtureByPos(m1, mbarHe):
    a = Volumes()
    pos = []
    mixture = []
    for i in xrange(80):
        a.reset()
        a.set_barbon_mass(m1)
        a.open_v2()
        a.add_he(mbarHe)
        a.goto(i)
        a.open_v2()
        pos.append(i)
        mixture.append(a.get_mixture() * 100.)
    plot(pos, mixture)
    del a

a = Volumes()


def twoStageMixture(m1, mbarHe1, mbarHe2, mix1, mix2):
    if mix1 and (mix1 < mix2):
        return -1e9, 1e9, 1e9, 1e9, 1e9
    a.reset()
    a.set_barbon_mass(m1)
    a.open_v2()
    a.add_he(mbarHe1)
    if mix1:
        pos1, percentage1 = a.mixToPercentage(mix1)
    else:
        pos1 = 0
        percentage1 = 0
    a.goto(75.)
    p2_1 = a.p2
    a.add_he(mbarHe2)
    pos2, percentage2 = a.mixToPercentage(mix2)
    a.goto(75.)
    p2_2 = a.p2
    #print "%i mug:\t %imm --> %.1f%% (%imbar) \t %imm --> %.1f%% (%imbar) \t ; %.1f %% ; " % (m1, pos1, percentage1 * 100., p2_1, pos2, percentage2 * 100., p2_2, a.m2 / m1 * 100.), mix1, mix2
    # return a.m2 / m1 * 100., p2_2
    if p2_2 < 1000.:
        return -1e9, 1e9, 1e9, 1e9, 1e9
    else:
        ratio = a.m2 / m1 # * 100.
        return ratio, pos1, pos2, percentage1, percentage2

"""
for mix1 in [5., 10.]:
    for mix2 in [2., 5., 8.]:
        mass = []
        percentage = []
        for m1 in xrange(1, 100, 1):
            try:
                _ratio, _p = twoStageMixture(m1, 2000., mix1, mix2)
                if _p > 900:
                    mass.append(m1)
                    percentage.append(_ratio)
            except Exception as e:
                print e
                continue
        try:
            plot(mass, percentage, label="%i, %i" % (mix1, mix2))
        except:
            pass
"""

mass = []
percentage1 = []
percentage2 = []
pressure = []
ratio = []

fkt = lambda p, m1: 1. - (twoStageMixture(m1, p[0], p[1], p[2])[0])
fkt = lambda p, m1: 1. - (twoStageMixture(m1, 1000., p[0], p[1])[0])

from sys import argv


def find_best_transfer(mrange=None, mbarHe1range=None, mbarHe2range=None, mix1done=None, tofile=False):
    if tofile:
        f = open("best_values.txt", "w")
    if not mrange:
        mrange = xrange(1, 100, 1)
    else:
        mrange = [mrange]
    if not mbarHe1range:
        mbarHe1range = xrange(700, 2000, 100)
    else:
        mbarHe1range = [mbarHe1range]
    if not mbarHe2range:
        mbarHe2range = xrange(700, 2000, 100)
    else:
        mbarHe2range = [mbarHe2range]
    mix = 5
    if len(argv) == 2:
        print "i am here. argv:", argv
        mix = int(argv[1])
    for m in mrange:
        min_mixture = mix
        while True:
            best_He1 = 0
            best_He2 = 0
            best_mix1 = 0
            best_mix2 = 0
            best_ratio = 0.
            best_pos1 = 0.
            best_pos2 = 0.
            for mbarHe1 in mbarHe1range:
                for mbarHe2 in mbarHe2range:
                    if not mix1done:
                        mix1range = [None] + range(min_mixture, 30, 1)
                    else:
                        mix1range = [mix1done]
                    for mix1 in mix1range:
                        for mix2 in xrange(min_mixture, 10):
                            ratio, pos1, pos2, percentage1, percentage2 = twoStageMixture(m, mbarHe1, mbarHe2, mix1, mix2)
                            if ratio > best_ratio:
                                best_ratio, best_pos1, best_pos2, best_mix1, best_mix2 = ratio, pos1, pos2, percentage1, percentage2
                                best_He1 = mbarHe1
                                best_He2 = mbarHe2
            if (best_ratio > 0) or (min_mixture == 0):
                print "\r",
                break
            else:
                min_mixture -= 1
                print "\rmixture -1: ", min_mixture,
        if tofile:
            print >> f, m, best_ratio, best_He1, best_He2, best_pos1, best_pos2, best_mix1, best_mix2
        #res = optimize.minimize(fkt, x0=[1000., 20., 1.], args=(m,), bounds=[(500., 2000.,), (10., 100.), (1., 20.)])
        #res = optimize.minimize(fkt, x0=[10., 5.], args=(m,), bounds=[(10., 100.), (1., 20.)], method="Nelder-Mead")
        if VERBOSE:
            print m, best_ratio * 100., best_He1, best_He2, best_pos1, best_pos2, best_mix1 * 100., best_mix2 * 100.
    if tofile:
        f.close()
    return best_He1, best_He2, best_pos1, best_pos2, best_ratio, best_mix1, best_mix2

if __name__ == '__main__':
    find_best_transfer(tofile=True)
# del a
