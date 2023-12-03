import matplotlib.pyplot as plt

class VadPlotter:
    def __init__(self):
        plt.ion()  # Enable interactive mode
        self.fig, self.ax = plt.subplots()
        self.xdata, self.ydata = [], []
        self.line, = self.ax.plot([], [], 'r-')  # Red line for VAD decisions
        self.__init_plot()

    def __init_plot(self):
        self.ax.set_xlim(0, 10)  # Set initial x-axis limits
        self.ax.set_ylim(-0.5, 1.5)   # Binary decision (0 or 1)
        self.ax.set_xlabel('Time (seconds)')
        self.ax.set_ylabel('VAD Decision')

    def update_plot(self, time, vad_decision):
        self.xdata.append(time)
        self.ydata.append(vad_decision)
        self.line.set_data(self.xdata, self.ydata)

        # Adjust the x-axis dynamically
        if time >= self.ax.get_xlim()[1]:
            self.ax.set_xlim(0, time + 1)

        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
