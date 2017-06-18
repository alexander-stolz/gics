import pyqtgraph
from pyqtgraph import QtCore, QtGui
import time
import threading
from OnlineAnalysis import R13VPDB

ALIVE = True
pyqtgraph.setConfigOptions(antialias=True)


class MyQtWindow(pyqtgraph.GraphicsWindow):
    def closeEvent(self, event):
        global ALIVE
        ALIVE = False
        event.accept()


class Device(threading.Thread):
    name = "plotter thread"
    updating = False
    moving = False
    win = None
    plot_2 = None
    plt_current_vs_time = None
    line_2_0 = None
    line_2_1 = None
    line_2_2 = None
    line_2_3 = None
    line_0_0 = None
    line_0_1 = None
    line_1_0 = None
    plot_ratios = False
    current_error = 0.
    current_r14 = 0.
    current_d13c = 0.

    carbon_flow_array = []                                                                                         # current    (current -> eff)
    time_array = []                                                                                         # time
    efficiency_array_reduced = []                                                                                         # effiviency (current -> eff)
    le12_array = []                                                                                         # current
    current_carbon_current = []                                                                                        # current now
    current_efficiency = []                                                                                        # efficiency now
    efficiency_array = []                                                                                        # efficieny
    d13c_array = []
    d13c_smooth_array = []
    mass_flow_array = []
    r14_blocks_array = []
    r14_error_blocks_array = []
    d13c_blocks_array = []

    def __init__(self):
        threading.Thread.__init__(self)
        # self.lock = threading.Lock()
        self.win = MyQtWindow(title="Gas Injection System - Status")
        # self.win.resize(800, 700)
        self.win.resize(851, 749)

        # plt_current_vs_time_short:       0
        # plt_current_vs_time_all:         1
        # plt_eff_vs_current:              2
        # plot4: r14 vs time
        self.plot_0 = self.win.addPlot(row=0, col=0)
        self.plot_1 = self.win.addPlot(row=1, col=0)
        self.plot_2 = self.win.addPlot(row=2, col=0)
        self.plot_2.showGrid(x=True, y=True)
        self.plot_0.showGrid(x=False, y=True)
        self.plot_1.showGrid(x=False, y=True)

        self.plot_2.showAxis("right")
        self.plot_0.showAxis("right")
        self.plot_1.showAxis("right")

        self.plot_0_viewbox = pyqtgraph.ViewBox()
        self.plot_0.scene().addItem(self.plot_0_viewbox)
        self.plot_0.getAxis("right").linkToView(self.plot_0_viewbox)
        self.plot_0.getAxis("right").setGrid(False)
        self.plot_0_viewbox.setXLink(self.plot_0)

        self.line_2_0 = self.plot_2.plot()
        self.line_2_1 = self.plot_2.plot()
        self.line_2_2 = self.plot_2.plot()
        self.line_2_3 = self.plot_2.plot()
        self.line_0_0 = self.plot_0.plot()
        self.line_1_0 = self.plot_1.plot()
        self.line_1_1 = self.plot_1.plot()

        self.line_0_1 = pyqtgraph.PlotCurveItem(pen=pyqtgraph.mkPen(color='#025b94'))
        self.plot_0_viewbox.addItem(self.line_0_1)

        self.plot_0.setTitle("<font color='#ffffff'>Extracted Carbon-12 Current</font> in A   |   <font color='lightblue'>Ionization Efficiency</font> in %")
        self.plot_1.setTitle("<font color='#ffffff'>Extracted Carbon-12 Current</font> in A")
        self.plot_2.setTitle("<font color='#ffffff'>Efficiency</font> in % <font color='#ffffff'>vs. Carbon Flow</font> in mug / min")

        self.updateViews()
        self.plot_0.getViewBox().sigResized.connect(self.updateViews)

        self.vlines = []

        # self.plt_eff_vs_current.setXRange(0, 3)
        # self.plt_eff_vs_current.setYRange(0, 12)

    # def run(self):
    #     while ALIVE:
    #          time.sleep(.5)
    #     self.close()

    def addVLine(self, pos=None):
        if not pos:
            vline1 = pyqtgraph.InfiniteLine(pos=len(self.r14_blocks_array) - .5)
            vline2 = pyqtgraph.InfiniteLine(pos=len(self.r14_blocks_array) - .5)
        else:
            vline1 = pyqtgraph.InfiniteLine(pos=pos)
            vline2 = pyqtgraph.InfiniteLine(pos=pos)
        self.vlines.append(vline1)
        self.vlines.append(vline2)
        self.plot_1.addItem(vline1)
        self.plot_2.addItem(vline2)
        self.set_plot_ratios()

    def updateViews(self):
        if (not self.moving) and (not self.updating):
            self.plot_0_viewbox.setGeometry(self.plot_0.getViewBox().sceneBoundingRect())
            self.plot_0_viewbox.linkedViewChanged(self.plot_0.getViewBox(), self.plot_0_viewbox.XAxis)

    def plotGuess(self, x, y):
        return
        self.line_2_3.setData(x=x, y=y, pen=pyqtgraph.mkPen(color='#025b94'))

    def add_ratios(self, r14, e14, r13):
        self.updating = True
        self.r14_blocks_array.append(r14)
        self.r14_error_blocks_array.append(e14)
        self.d13c_blocks_array.append((r13  / R13VPDB - 1.) * 1000.)
        self.updating = False

    def set_plot_ratios(self, plotRatios=None):
        if (plotRatios):
            self.plot_ratios = plotRatios
        if (not self.plot_ratios):
            # for vline in self.vlines:
            #     vline.hide()
            self.plot_1.setTitle(
                "<font color='#ffffff'>Extracted Carbon-12 Current</font> in A")
            self.plot_2.setTitle(
                "<font color='#ffffff'>Efficiency</font> in % <font color='#ffffff'>vs. Carbon Flow</font> in mug / min")
        else:
            # for vline in self.vlines:
            #     vline.show()
            if (self.current_r14):
                self.plot_1.setTitle(
                    "<font color='#ffffff'>Carbon-14 / Carbon-12 </font> Ratio (%.2e +- %.2f %%)" % (self.current_r14, self.current_error * 100.))
            else:
                self.plot_1.setTitle(
                    "<font color='#ffffff'>Carbon-14 / Carbon-12 </font> Ratio")
            if (self.current_d13c):
                self.plot_2.setTitle(
                    "<font color='#ffffff'>d13C</font> (%.2f)" % (self.current_d13c))
            else:
                self.plot_2.setTitle(
                    "<font color='#ffffff'>d13C</font> (not corrected)")
        self.updateViews()

    def update(self):
        # time -> current/efficiency short
        if (not self.updating):
            self.updating = True

            if (len(self.time_array) == len(self.efficiency_array)):
                self.line_0_1.setData(
                    x=self.time_array[-750:], 
                    y=self.efficiency_array[-750:], 
                    pen=(6, 155, 255))
                self.line_0_0.setData(
                    x=self.time_array[-750:], 
                    y=self.le12_array[-750:], 
                    pen=(255, 255, 255))

            if (not self.plot_ratios):
                # time -> current
                if (len(self.time_array) == len(self.le12_array)):
                    self.line_1_0.setData(
                        x=self.time_array, 
                        y=self.le12_array, 
                        pen=(255, 255, 255), 
                        symbolPen=None, 
                        symbolBrush=None)

                # current -> efficiency : now, all, last5
                if (len(self.carbon_flow_array) == len(self.efficiency_array_reduced)):
                    self.line_2_0.setData(
                        x=self.carbon_flow_array, 
                        y=self.efficiency_array_reduced, 
                        pen=None, 
                        symbol="o", 
                        symbolBrush=(255, 255, 255), 
                        symbolPen=(255, 255, 255), 
                        symbolSize=4)
                    self.line_2_1.setData(
                        x=self.carbon_flow_array[-5:], 
                        y=self.efficiency_array_reduced[-5:], 
                        pen=None, 
                        symbol="o", 
                        symbolPen=(255, 0, 0))
                if (len(self.current_carbon_current) == len(self.current_efficiency)):
                    self.line_2_2.setData(
                        x=self.current_carbon_current, 
                        y=self.current_efficiency, 
                        pen=None, 
                        symbol="o", 
                        symbolPen=(0, 255, 0))
            else:
                # r14
                self.line_1_0.setData(
                    x=range(len(self.r14_blocks_array)), 
                    y=self.r14_blocks_array, 
                    pen=None, 
                    symbol="o", 
                    symbolBrush=(255, 255, 255), 
                    symbolPen=(255, 255, 255), 
                    symbolSize=6)

                # d13c
                self.line_2_0.setData(
                    x=range(len(self.d13c_blocks_array)), 
                    y=self.d13c_blocks_array, 
                    pen=None, 
                    symbol="o", 
                    symbolBrush=(255, 255, 255), 
                    symbolPen=(255, 255, 255), 
                    symbolSize=6)
                self.line_2_1.setData(
                    x=[], 
                    y=[], 
                    pen=None, 
                    symbol="o", 
                    symbolPen=(255, 0, 0))
                self.line_2_2.setData(
                    x=[], 
                    y=[], 
                    pen=None, 
                    symbol="o", 
                    symbolPen=(0, 255, 0))
            self.updating = False
            self.set_plot_ratios()                                              # sets plot titles

        if not ALIVE:
            self.closeMe()

    def start_timer(self):
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(200)

    def attach(self, geo):
        if (not self.win.isMinimized()) and (not self.win.isMaximized()) and (not self.moving):
            self.moving = True
            main_x = geo.x()
            main_y = geo.y()
            self.win.move(main_x - self.win.frameGeometry().width(), main_y)
            self.win.activateWindow()
            self.moving = False

    def reset(self):
        self.current_error = 0.
        self.carbon_flow_array = []
        self.efficiency_array_reduced = []
        self.time_array = []
        self.le12_array = []
        self.current_carbon_current = []
        self.current_efficiency = []
        # self.x22 = []
        self.efficiency_array = []
        self.d13c_array = []
        self.x31 = []
        self.d13c_smooth_array = []
        self.x32 = []
        self.mass_flow_array = []

    def closeMe(self):
        global ALIVE
        self.timer.stop()
        try:
            self.win.close()
        except:
            pass
        for item in [self.plot_2, self.plt_current_vs_time, self.plot_1, self.line_2_0, self.line_2_1, self.line_2_2, self.line_2_3, self.line_0_0, self.line_0_1, self.line_1_0, self.win]:
            try:
                del item
            except:
                pass
        del self.win
        ALIVE = False
