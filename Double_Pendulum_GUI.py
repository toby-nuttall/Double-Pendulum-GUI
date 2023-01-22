
import sys

from PyQt5 import QtCore, QtWidgets

import numpy as np

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation

from PyQt5.QtCore import Qt

from PyQt5.QtWidgets import (
    QMainWindow, QApplication,
    QLabel, QToolBar, QAction, QStatusBar, QSlider, QPushButton
)


from numpy import sin, cos
import matplotlib.pyplot as plt
from collections import deque


G = 9.8  # acceleration due to gravity, in m/s^2
L1 = 1.0  # length of pendulum 1 in m
L2 = 1.0  # length of pendulum 2 in m
L = L1 + L2  # maximal length of the combined pendulum
M1 = 1.0  # mass of pendulum 1 in kg
M2 = 1.0  # mass of pendulum 2 in kg
t_stop = 2.5  # how many seconds to simulate
history_len = 500  # how many trajectory points to display


def derivs(t, state):
    dydx = np.zeros_like(state)

    dydx[0] = state[1]

    delta = state[2] - state[0]
    den1 = (M1+M2) * L1 - M2 * L1 * cos(delta) * cos(delta)
    dydx[1] = ((M2 * L1 * state[1] * state[1] * sin(delta) * cos(delta)
                + M2 * G * sin(state[2]) * cos(delta)
                + M2 * L2 * state[3] * state[3] * sin(delta)
                - (M1+M2) * G * sin(state[0]))
               / den1)

    dydx[2] = state[3]

    den2 = (L2/L1) * den1
    dydx[3] = ((- M2 * L2 * state[3] * state[3] * sin(delta) * cos(delta)
                + (M1+M2) * G * sin(state[0]) * cos(delta)
                - (M1+M2) * L1 * state[1] * state[1] * sin(delta)
                - (M1+M2) * G * sin(state[2]))
               / den2)

    return dydx

dt = 0.01
t = np.arange(0, t_stop, dt)

class MyMplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)

        self.ax = fig.add_subplot(autoscale_on=False, xlim=(-L, L), ylim=(-L, 1.))

        

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        #FigureCanvas.setSizePolicy(
        #    self, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        #)
        #self.ax = fig.add_subplot(autoscale_on=False, xlim=(-L, L), ylim=(-L, 1.))
        fig.subplots_adjust(left = 0.11,bottom = 0.25)
        #FigureCanvas.updateGeometry(self)


class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.main_widget = QtWidgets.QWidget(self)
        self.canvas = MyMplCanvas(self.main_widget, width=6, height=6 * L, dpi=100)

        self.TH1 = 90
        self.TH2 = 90

        self.label = QLabel(f"top pendulum angle :{self.TH1} degrees",self)
        self.label2 = QLabel(f"bottom pendulum angle :{self.TH2} degrees",self)

        self.th1 = QSlider(Qt.Horizontal, self)
        self.th1.setGeometry(70,600,200,30)
        self.th1.valueChanged[int].connect(self.changeValue)
        self.th1.setTickPosition(QSlider.TicksBelow)
        self.th1.setTickInterval(10)
        self.th1.setMinimum(0)
        self.th1.setMaximum(180)
        self.th1.setValue(90)
         
        
        self.th2 = QSlider(Qt.Horizontal, self)
        self.th2.setGeometry(350,600,200,30)
        self.th2.valueChanged[int].connect(self.changeValue2)
        self.th2.setTickPosition(QSlider.TicksBelow)
        self.th2.setTickInterval(10)
        self.th2.setMinimum(0)
        self.th2.setMaximum(180)
        self.th2.setValue(90)

        self.toggle_button = QPushButton("start", self)
        self.toggle_button.setCheckable(True)
        self.toggle_button.clicked.connect(self.toggle)
        self.toggle_button.setStyleSheet("background-color : green")

        self.xdata = []
        self.ydata = []

        

        

        vbox = QtWidgets.QVBoxLayout(self.main_widget)
    
        vbox.addWidget(self.canvas)
        vbox.addWidget(self.toggle_button)
        vbox.addWidget(self.label)
        vbox.addWidget(self.th1)
        vbox.addWidget(self.label2)
        vbox.addWidget(self.th2)
        
        # self.setLayout(vbox)

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

    def toggle(self):
        if self.toggle_button.isChecked():
            self.GO()
            self.toggle_button.setText("stop")
            self.toggle_button.setStyleSheet("background-color : red")
        
        else:
            self.restart()
            self.toggle_button.setText("start")
            self.toggle_button.setStyleSheet("background-color : green")


    
    def restart(self):
        self.ani.event_source.stop()
        self.ani = 0
        self.line.remove()
        self.trace.remove()
        self.time_text.remove()
        self.time_template = 'time = %.1fs'
        self.canvas.draw()
    
    def GO(self):
        for _ in range(2):
            self.start_func_animation()

    def start_func_animation(self):
        
            self.y = np.empty((len(t), 4))
            self.y[0] = np.radians([self.TH1, 0, self.TH2, 0])
            for i in range(1, len(t)):
                self.y[i] = self.y[i - 1] + derivs(t[i - 1], self.y[i - 1]) * dt

            self.line, = self.canvas.ax.plot([], [], 'o-', lw=2)
            self.trace, = self.canvas.ax.plot([], [], '.-', lw=1, ms=2)
            self.time_template = 'time = %.1fs'
            self.time_text = self.canvas.ax.text(0.05, 0.9, '', transform=self.canvas.ax.transAxes)
            self.history_x, self.history_y = deque(maxlen=history_len), deque(maxlen=history_len)

            self.canvas.draw()

            self.ani = FuncAnimation(self.canvas.figure, self.animate, frames = 250, interval=10)

    def animate(self,i):

        if i < 251 : 
  
            x1 = L1*sin(self.y[:, 0])
            y1 = -L1*cos(self.y[:, 0])

            x2 = L2*sin(self.y[:, 2]) + x1
            y2 = -L2*cos(self.y[:, 2]) + y1

            thisx = [0, x1[i], x2[i]]
            thisy = [0, y1[i], y2[i]]

            if i == 0:
                self.history_x.clear()
                self.history_y.clear()
            
            self.history_x.appendleft(thisx[2])
            self.history_y.appendleft(thisy[2])

            self.line.set_data(thisx, thisy)
            self.trace.set_data(self.history_x, self.history_y)
            self.time_text.set_text(self.time_template % (i*dt))

            print(i)
                

            return self.line, self.trace, self.time_text
    
    def changeValue2(self,value):
        self.TH2 = value
        self.label2.setText(f"bottom pendulum angle :{self.TH2} degrees")
        
    
    def changeValue(self, value):
        self.TH1 = value
        self.label.setText(f"top pendulum angle :{self.TH1} degrees")


if __name__ == "__main__":
    App = QtWidgets.QApplication(sys.argv)
    aw = ApplicationWindow()
    aw.show()
    sys.exit(App.exec_())