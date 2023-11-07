from tkinter import*
import serial
from serial.tools import list_ports
from tkinter import messagebox
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
from struct import *
import time,threading
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
from pyqtgraph.Point import Point
import re, time, os, sys

global factor
global ser
global ports
global timer
global fig
global ax1

#Graphing style used to graph natural pulse
style.use('ggplot')

x_ax = [] #time
y1_ax = [] #amplitude
y2_ax = []
xtime=0

#serial setup variable
ser = serial.Serial()

def checkDeviceInfo():
    if(ser.is_open):
        di = Tk();
        di.title("Device")
        D1 = Label(di, text="Device name:",fg='blue',anchor='center')
        D1.grid(row=1,column=1)
        D1name = Label(di, text=ports[0].device,anchor='center')
        D1name.grid(row=1,column=2)
        D2 = Label(di, text="Description:",fg='blue',anchor='center')
        D2.grid(row=2,column=1)
        D2name = Label(di, text=ports[0].description,anchor='center')
        D2name.grid(row=2,column=2)
        D3 = Label(di, text="Manufacturer",fg='blue',anchor='center')
        D3.grid(row=3,column=1)
        D3name = Label(di, text=ports[0].manufacturer,anchor='center')
        D3name.grid(row=3,column=2)
    else:
        messagebox.showerror("System Message", "The device is not connected")


def connect():
    global ser
    global ports
    ports = list(list_ports.comports())
    ser = serial.Serial()
    ser.baudrate = 115200
    ser.port = ports[0].device
    ser.timeout = None
    ser.open()
    if ser.is_open:
        messagebox.showinfo("System Message", "Connected")
        print(ser)
    else:
        messagebox.showerror("System Message", "Disconnected")

def disconnect():
    global ser
    ser.close()



def grab_data():
    global xtime
    graph_data = ser.read(24)
    y = unpack('ddd', graph_data)
    if (abs(y[2]) - 31 < (1e-6)):
        x_ax.append(xtime * 0.005)
        y1_ax.append(y[0])
        y2_ax.append(y[1])
        xtime = xtime + 1
        if len(x_ax) > 100:
            del (x_ax[0])
            del (y1_ax[0])
            del (y2_ax[0])
    timer1 = threading.Timer(0.005, grab_data)  # Timer to call grab_data function every 0.005s
    timer1.start()
    if (xtime > 190):
        timer1.cancel()
        plt.close()
        xtime = 0  # reset counter


"""
@brief: Function used to graph out collected data
@object: ax1.plot -> plot(x,y,label) on the figure
         ax1.clear() -> clear figure
"""


def animate(i):
    global ax1
    global fig
    ax1.clear()
    ax1.plot(x_ax, y1_ax, label='Atrl_Signal')
    ax1.plot(x_ax, y2_ax, label='Vent_Signal')
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Amplitude (mV)')
    ax1.set_ylim(bottom=-2, top=2)
    ax1.set_title('Egram Data Visiualization')
    ax1.legend(loc='upper right')


"""
@brief: Function used to consistently graph natural pacing
@parameter: grab_data() -> grab data from the K64F board
         ani -> call animate function in 200 ms interval
         xtime -> variable used to indicate timing on x-axis of the graph 
         plt.show() -> show plotted graph on the figure
"""


def GRAPH_Mode_Modifier():
    global ser
    global xtime
    global timer
    global fig
    global ax1
    disconnect()
    disconnect()
    connect()
    if ser.is_open:
        fig = plt.figure()
        fig.set_size_inches(11, 6)
        ax1 = fig.add_subplot(1, 1, 1)
        grab_data()
        ani = animation.FuncAnimation(fig, animate, interval=200)
        '''timer = fig.canvas.new_timer(interval = 3000) #creating a timer object and setting an interval of 3000 milliseconds
        timer.add_callback(close_event)
        timer.start()'''
        plt.show()

    else:
        messagebox.showerror("System Message", "The Device is not connected")
    disconnect()

def egram():
    #connect()
    win = pg.GraphicsLayoutWidget(show =True)
    win.setWindowTitle('HeartView')
    p2 = win.addPlot()
    data1 = np.random.normal(size=300)
    curve2 = p2.plot(data1)
    ptr1 = 0

    def updata1():
        global data1,ptr1
        data1[:-1] = data1[1:]
        data1[-1]=np.random.normal()
        ptr1+=1
        curve2.setData(updata1)
        curve2.setPos(ptr1,0)

    timer = pg.QtCore.QTimer()
    timer.timeout.connect(updata1)
    timer.start(50)

    if __name__ == '__main__':
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec()


''''
class ScrollingPloter:
    def __init__(self, title_name, plot_num, x_data_num = 300, refresh_rate = 1):
        self.x_data_num = x_data_num
        self.title_name = title_name
        self.plot_num = plot_num
        self.refresh_rate = refresh_rate
        self.win = pg.GraphicsWindow()
        self.win.setWindowTitle(self.title_name)
        self.plot_array = []
        self.curve_array = []
        self.data_array = []
        self.timer_array = []
        self.slot_func_array = []
        self.func = []
        for i in range(0, plot_num):
            p = self.win.addPlot()
            p.showGrid(x=True,y=True)
            self.plot_array.append(p)
            init_data = np.zeros(x_data_num)
            self.data_array.append(init_data)
            curve = p.plot(self.data_array[i], pen="y", symbolBrush=(255,0,0), symbolPen='w')
            self.win.nextRow()
            self.curve_array.append(curve)
            self.func.append(self.noFunc)

    def noFunc(self):
        pass

    def setFunc(self, plot_index, func):
        self.timer = pg.QtCore.QTimer()
        self.func[plot_index] = func
        self.timer.timeout.connect(func)
        self.timer.start(1)

    ser = serial.Serial("COM2", 115200)

    def update(self):
        data_str = ser.readline()
        # "4.946620|0.080203|0.080203"
        data = data_str.decode("utf-8")
        print(data)
        data_arry = re.split("[|\n]", data)
        if data_arry[3] is "":
            x.data_array[0][:-1] = x.data_array[0][1:]
            x.data_array[0][-1] = (float(data_arry[0]))
            x.curve_array[0].setData(x.data_array[0])

            x.data_array[1][:-1] = x.data_array[1][1:]
            x.data_array[1][-1] = (float(data_arry[1]))
            x.curve_array[1].setData(x.data_array[1])

            x.data_array[2][:-1] = x.data_array[2][1:]
            x.data_array[2][-1] = (float(data_arry[2]))
            x.curve_array[2].setData(x.data_array[2])

    x = ScrollingPloter("test", 2)
    # timer = pg.QtCore.QTimer()
    # timer.timeout.connect(update)
    # timer.start(1)
    timer1 = pg.QtCore.QTimer()
    timer1.timeout.connect(update1)
    timer1.start(0.02)
    
    if __name__ == '__main__':
        import sys
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()
'''''