'''
Plotter:
    
    This is a set of functions that plots some given data and auto-updates it.
    This one is a more optimized one, so it wouldn't lag horribly like the
    previous one did
'''

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication,QMainWindow,QWidget,QPushButton,QVBoxLayout
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys
import nidaqmx
import numpy as np
import pandas as pd
from pathlib import Path
import time
import h5py
import atexit

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        
        
        layout = QVBoxLayout()
        
        w = QWidget()
        w.setLayout(layout) # set layout to our central widget
        self.setCentralWidget(w) # set w as central widget

        self.pg1 = pg.PlotWidget()
        #self.setCentralWidget(self.graphWidget)
        
        layout.addWidget(self.pg1)
        print(sys.argv)
        #Taking input values and defining them
        connection = sys.argv
        
        self.voltage_change = str(connection[-1]).split(',') #List of int strings with commas
        connection.pop(-1)
        self.resistor = str(connection[-1]) #String
        connection.pop(-1)
        self.view = str(connection[-1]).split(',') #List of strings with commas
        connection.pop(-1)
        self.name = str(connection[-1]) #String
        self.view = self.view[0].split(';')
        print(self.view)
        self.viewers=1
        
        if len(self.view)>1:
            self.viewers = 2
            self.pg2 = pg.PlotWidget()
            layout.addWidget(self.pg2)
        if len(self.view)>2:
            self.viewers = 3
            self.pg3 = pg.PlotWidget()
            layout.addWidget(self.pg3)
        if len(self.view)>3:
            self.viewers = 4
            self.pg4 = pg.PlotWidget()
            layout.addWidget(self.pg4)

        self.signalx = []
        self.signaly = []
        self.temp = []
        self.capacitancex = []
        self.capacitancey = []
        self.filename = '{}/Data.h5'.format(self.name)
        self.voltage_min = float(self.voltage_change[0])
        self.voltage_max = float(self.voltage_change[1])
        self.voltage_incriment = float(self.voltage_change[2])
        self.current_voltage = self.voltage_min
        
        #Setting the start voltage for the heater
        self.change_voltage_output()

        self.counter = 0

        self.pg1.setBackground('k')

        pen = pg.mkPen(color=(255, 255, 255))
        self.data_line = self.pg1.plot(np.array([0,0]), np.array([0,0]), pen=pen)
        if self.viewers>1:
            self.data_line2 = self.pg2.plot(np.array([0,0]), np.array([0,0]), pen=pen)
        if self.viewers>2:
            self.data_line3 = self.pg3.plot(np.array([0,0]), np.array([0,0]), pen=pen)
        if self.viewers>3:
            self.data_line4 = self.pg4.plot(np.array([0,0]), np.array([0,0]), pen=pen)
        
        self.timer = QtCore.QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()

    def update_plot_data(self):
        '''Updates plot, collects all the data from the lockin, writes the info
        and changes voltage'''
        
        data = self.collect_from_LA()
        
        self.signalx.append(float(data[0][0]))
        self.signaly.append(float(data[1][0]))
        self.capacitancex.append(float(data[3][0]))
        self.capacitancey.append(float(data[4][0]))
        
        if self.resistor=='Cernox':
            self.temp.append(self.Cernox(float(data[2][0])))
        
        self.counter += 1
        print(self.counter)
        if self.counter >= 60:
            self.counter = 0
            #writing to file
            self.write_to_file()
            #Changing voltage on heater
            if self.voltage_min<self.voltage_max:
                self.current_voltage+=self.voltage_incriment/10
            else:
                self.current_voltage-=self.voltage_incriment/10
            self.change_voltage_output()
            if self.current_voltage>=self.voltage_max and self.voltage_max>\
            self.voltage_min:
                self.current_voltage = 0.0
                self.change_voltage_output()
                sys.exit()
            elif self.current_voltage<=self.voltage_max and self.voltage_max<\
            self.voltage_min:
                self.current_voltage = 0.0
                self.change_voltage_output()
                sys.exit()

        for i in range(0,len(self.view)):
            #Which data are you plotting now?
            if self.view[i]=='Temp':
                x = None
                y = self.temp
                xlabel='Time'
                x_units='s'
                ylabel='Temperature'
                y_units='K'
            elif self.view[i]=='Signalx_Temp':
                x=self.temp
                y=self.signalx
                ylabel='Signalx'
                y_units='V'
                xlabel='Temperature'
                x_units='K'
            elif self.view[i]=='Signaly_Temp':
                x=self.temp
                y=self.signaly
                ylabel='Signaly'
                y_units='V'
                xlabel='Temperature'
                x_units='K'
            elif self.view[i]=='Signaly_Signalx':
                x=self.signalx
                y=self.signaly
                xlabel='Signalx'
                x_units='V'
                ylabel='Signaly'
                y_units='V'
            elif self.view[i]=='Capacitancey_Capacitancex':
                x=self.capacitancey
                y=self.capacitancex
                xlabel='Voltagex'
                x_units='V'
                ylabel='Voltagey'
                y_units='V'
                
            #Update the Data
            if x==None and i==0:
                self.data_line.setData(y)
                self.pg1.setLabel('left', ylabel, units=y_units)
                self.pg1.setLabel('bottom',xlabel, units=x_units)
            elif i==0:
                self.data_line.setData(x,y)
                self.pg1.setLabel('left', ylabel, units=y_units)
                self.pg1.setLabel('bottom',xlabel, units=x_units)
                
            if self.viewers>1 and i==1:
                self.data_line2.setData(x,y)
                self.pg2.setLabel('left', ylabel, units=y_units)
                self.pg2.setLabel('bottom',xlabel, units=x_units)
            elif self.viewers>2 and i==2:
                self.data_line3.setData(x,y)
                self.pg3.setLabel('left', ylabel, units=y_units)
                self.pg3.setLabel('bottom',xlabel, units=x_units)
            elif self.viewers>3 and i==3:
                self.data_line4.setData(x,y)
                self.pg4.setLabel('left', ylabel, units=y_units)
                self.pg4.setLabel('bottom',xlabel, units=x_units)
        
    def collect_from_LA(self):
        '''This function takes data from the Lock-in Amplifiers through the BNC-
        2120 and will be stored in a csv'''
        
        Samples_Per_Ch_To_Read = 1
        
        #Collects all values and they will be given to their resepective 
        #variables when this function is called
        collection_params = {'Signalx':'Dev1/ai2','Signaly':'Dev1/ai3',\
                             'Temp':'Dev1/ai4','Capacitancex':'Dev1/ai6',\
                             'Capacitancey':'Dev1/ai7'}
        
        data = []
        
        for key, value in collection_params.items():
            with nidaqmx.Task() as task:
                task.ai_channels.add_ai_voltage_chan("{}".format(value))     
                data.append(task.read(Samples_Per_Ch_To_Read ))
                    
        return data
    
    def write_to_file(self):
        '''Writes a file that will be read later on, but appends data every 10 
        samples'''
        #Creates file and directory if it's not already there
        Path(self.name).mkdir(parents=True,exist_ok=True)
        Path(self.filename).touch(exist_ok=True)
        
        hf = h5py.File(self.filename, 'w')

        hf.create_dataset('Temperature', data=self.temp, compression="gzip", compression_opts=9)
        hf.create_dataset('Signalx', data=self.signalx, compression="gzip", compression_opts=9)
        hf.create_dataset('Signaly', data=self.signaly, compression="gzip", compression_opts=9)
        hf.create_dataset('Capacitancex', data=self.capacitancex, compression="gzip", compression_opts=9)
        hf.create_dataset('Capacitancey', data=self.capacitancey, compression="gzip", compression_opts=9)
        
        hf.close()

            
    def change_voltage_output(self):
        '''Changes the heater voltage to some other value'''
        
        with nidaqmx.Task() as task:
            task.ao_channels.add_ao_voltage_chan('Dev1/ao1')
            task.write(self.current_voltage)
            task.stop()
    
        
    def Cernox(self,r):
        '''This is for if you want to find the temperature with the regular 
        setup that Di made with the resistors'''

        #print(r)
        r=np.abs(r)*500 #multiplied by 100*(multiplier in mV)
        if r>=677.5 and r<=11692.44:
            z=np.log10(r)
            l=2.79109337883
            u=4.06790523115
            k=((z-l)-(u-z))/(u-l)
            
            a0=5.531596*np.cos(0*np.arccos(k))
            a1=-6.358695*(np.cos(1*np.arccos(k))) 
            a2=+2.806398*(np.cos(2*np.arccos(k))) 
            a3=-1.027617*(np.cos(3*np.arccos(k))) 
            a4=+0.315889*(np.cos(4*np.arccos(k))) 
            a5=-0.077765*(np.cos(5*np.arccos(k))) 
            a6=+0.012103*(np.cos(6*np.arccos(k))) 
            a7=+0.000877*(np.cos(7*np.arccos(k))) 
            a8=-0.001935*(np.cos(8*np.arccos(k))) 
            a9=+0.000991*(np.cos(9*np.arccos(k))) 
            T=a0+a1+a2+a3+a4+a5+a6+a7+a8+a9
        elif r>=189.9 and r<677.5:
            z=np.log10(r)
            l=2.23708329199
            u=2.87845888952
            k=((z-l)-(u-z))/(u-l)
            
            a0=+42.764664*(np.cos(0*np.arccos(k))) 
            a1=-38.009825*(np.cos(1*np.arccos(k))) 
            a2=+8.2665490*(np.cos(2*np.arccos(k))) 
            a3=-0.9809110*(np.cos(3*np.arccos(k))) 
            a4=+0.1051020*(np.cos(4*np.arccos(k))) 
            a5=-0.0048220*(np.cos(5*np.arccos(k))) 
            a6=-0.0063310*(np.cos(6*np.arccos(k))) 
            T=a0+a1+a2+a3+a4+a5+a6
        elif r>=56.52 and r<189.9:
            z=np.log10(r)
            l=1.75219239023
            u=2.32448831166
            k=((z-l)-(u-z))/(u-l)
            
            a0=+176.848957*(np.cos(0*np.arccos(k))) 
            a1=-126.464217*(np.cos(1*np.arccos(k))) 
            a2=+22.5761410*(np.cos(2*np.arccos(k))) 
            a3=-3.35170800*(np.cos(3*np.arccos(k))) 
            a4=+0.66727900*(np.cos(4*np.arccos(k))) 
            a5=-0.13272400*(np.cos(5*np.arccos(k))) 
            a6=+0.02389800*(np.cos(6*np.arccos(k))) 
            a7=-0.00927800*(np.cos(7*np.arccos(k))) 
            T=a0+a1+a2+a3+a4+a5+a6+a7
        else:
            T=-1
        
        return T

def quitting():
    print(sys.argv[-1])
    with h5py.File('{}/Data.h5'.format(sys.argv[-1]), 'r') as d:
        T = d.get('Temperature')
        X = d.get('Signalx')
        Y = d.get('Signaly')
        CX = d.get('Capacitancex')
        CY = d.get('Capacitancey')
        df = pd.DataFrame(data={'Temperature':T,'Signalx':X,'Signaly':Y,\
                                'Capacitancex':CX,'Capacitancey':CY})
        df.to_csv('{}/Data.csv'.format(sys.argv[-1]))

app = QtWidgets.QApplication(sys.argv)
w = MainWindow()
w.show()
atexit.register(quitting)
sys.exit(app.exec_())