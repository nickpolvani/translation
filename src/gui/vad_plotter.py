import sys
import matplotlib

matplotlib.use("Qt5Agg")  # Set the PyQt5 backend
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtCore import pyqtSignal


class VadPlotter(QWidget):
    def __init__(self, vad_prediction_ready: pyqtSignal, max_time=30.0, parent=None):
        super(VadPlotter, self).__init__(parent)
        self.setMinimumSize(300, 200)
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.xdata, self.ydata = [], []
        (self.line,) = self.ax.plot([], [], "r-")  # Red line for VAD decisions
        self.max_time = max_time

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.canvas)
        self.setLayout(self.layout)

        self.vad_prediction_ready = vad_prediction_ready
        self.vad_prediction_ready.connect(self.update_plot)
        self.__init_plot()

    def __init_plot(self):
        self.ax.set_xlim(0, self.max_time)  # Set initial x-axis limits
        self.ax.set_ylim(-0.5, 1.5)  # Binary decision (0 or 1)
        self.ax.set_xlabel("Time (seconds)")
        self.ax.set_ylabel("VAD Decision")
        self.show()

    def update_plot(self, time, vad_decision):
        if time < self.max_time:
            self.xdata.append(time)
            self.ydata.append(vad_decision)
            self.line.set_data(self.xdata, self.ydata)

            # Adjust the x-axis dynamically
            if time >= self.ax.get_xlim()[1]:
                self.ax.set_xlim(0, time + 1)
        else:
            self.xdata.pop(0)
            self.ydata.pop(0)
            self.xdata.append(time)
            self.ydata.append(vad_decision)
            self.line.set_data(self.xdata, self.ydata)
            if time >= self.ax.get_xlim()[1]:
                self.ax.set_xlim(self.xdata[0] - 1, time + 1)

        self.canvas.draw()
