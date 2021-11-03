# -*- coding: utf-8 -*-
"""
Created on Tue Oct 19 15:12:16 2021

@author: Stephen Julian
"""

from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
import nidaqmx
import sys
import pandas as pd
import os
import itertools
import time
import pyautogui

'''I'll be honest, I don't know how this program actually works, but it does'''

platinum_resistance = np.array(np.loadtxt('pt_res.csv',delimiter=','))
platinum_temperature = np.array(np.loadtxt('pt_temp.csv',delimiter=','))

start_time = time.time()

def print_help_statement():
    '''Just to print the help prompt to the user'''
    
    print("The possible commands that can be used are as follows:\n\
          Temp: Temperature vs. Time\n\
          Signalx vs Temp: Self-explanitory\n\
          Signaly vs Signalx: Also Self-explanitory\n\
          Signaly vs Temp: Not gonna say it again\n\
          \n\
          The possible resistors to calibrate the given temperature\
          are platinum, RuO and Cernox(raw_temp) data")

def prompt_user():
    '''Takes the command line arguments and turns it into a string, which will
    be called to do specific tasks. This function doesn't actually prompt the 
    user, it takes the user's prompt, big difference'''
    connection = sys.argv
    connection.pop(0)
    magnetometer = sys.argv[-1]
    connection.pop(-1)
    voltage_incriment = sys.argv[-1]
    connection.pop(-1)
    voltage_max = sys.argv[-1]
    connection.pop(-1)
    voltage_min = sys.argv[-1]
    connection.pop(-1)
    resistor = sys.argv[-1]
    connection.pop(-1)
    bit_rate = sys.argv[-1]
    connection.pop(-1)
    name=sys.argv[-1]
    connection.pop(-1)
    spl = [list(y) for x, y in itertools.groupby(connection, lambda z: z == \
           ';') if not x]
    for i in range(0,len(spl)):
        spl[i] = ' '.join(spl[i])
    
    #Possible functionalities at the moment
    list_commands=['Temp','Signalx vs Temp','Signaly vs Signalx',\
                   'Signaly vs Temp']
    if type(spl)==list:
        for connection in spl:
            if connection not in list_commands:
                print_help_statement()
    else:
        if spl[0] not in list_commands:
            print_help_statement()
        sys.exit()
    
    return spl,name,bit_rate,resistor,voltage_min,voltage_max,voltage_incriment\
,magnetometer

connection,name,bit_rate,resistor,voltage_min,voltage_max,voltage_incriment,\
magnetometer = prompt_user()

voltage_min = float(voltage_min)
voltage_max = float(voltage_max)
voltage_incriment = float(voltage_incriment)/10
magnetometer = int(magnetometer)

if voltage_max==0:
    include_voltage=False
else:
    include_voltage=True

current_voltage = voltage_min
change_time = [time.time()-start_time][-1]*int(bit_rate)
#QtGui.QApplication.setGraphicsSystem('raster')
app = QtGui.QApplication([])
mw = QtGui.QMainWindow()
mw.setWindowTitle('Super Awesome Plotting Program Viewer')
mw.resize(800,800)
cw = QtGui.QWidget()
mw.setCentralWidget(cw)
l = QtGui.QVBoxLayout()
cw.setLayout(l)

# giving the plots names allows us to link
pw = pg.PlotWidget(name=connection[0]) 
#their axes together
l.addWidget(pw)
if len(connection)>1:
    pw2 = pg.PlotWidget(name=connection[1])
    l.addWidget(pw2)
if len(connection)>2:
    pw3 = pg.PlotWidget(name=connection[2])
    l.addWidget(pw3)
if len(connection)>3:
    pw4 = pg.PlotWidget(name=connection[3])
    l.addWidget(pw4)

mw.show()

## Create an empty plot curve to be filled later, set its pen
p1 = pw.plot()
p1.setPen((200,200,100))
if len(connection)>1:
    p2=pw2.plot()
    p2.setPen((200,200,100))
if len(connection)>2:
    p3=pw3.plot()
    p3.setPen((200,200,100))
if len(connection)>3:
    p4=pw4.plot()
    p4.setPen((200,200,100))

#Specifies what the axes will look like depending on the task
if connection[0]=='Temp':
    pw.setLabel('left', 'Temperature', units='K')
    pw.setLabel('bottom', 'Time', units='s')
elif connection[0]=='Signalx vs Temp':
    pw.setLabel('left', 'Signalx', units='V')
    pw.setLabel('bottom', 'Temp', units='K')
elif connection[0]=='Signaly vs Signalx':
    pw.setLabel('left', 'Signaly', units='V')
    pw.setLabel('bottom', 'Signalx', units='V')
elif connection[0]=='Signaly vs Temp':
    pw.setLabel('left', 'Signaly', units='V')
    pw.setLabel('bottom', 'Temp', units='K')

if len(connection)>1:
    if connection[1]=='Temp':
        pw2.setLabel('left', 'Temperature', units='K')
        pw2.setLabel('bottom', 'Time', units='s')
    elif connection[1]=='Signalx vs Temp':
        pw2.setLabel('left', 'Signalx', units='V')
        pw2.setLabel('bottom', 'Temp', units='K')
    elif connection[1]=='Signaly vs Signalx':
        pw2.setLabel('left', 'Signaly', units='V')
        pw2.setLabel('bottom', 'Signalx', units='V')
    elif connection[1]=='Signaly vs Temp':
        pw2.setLabel('left', 'Signaly', units='V')
        pw2.setLabel('bottom', 'Temp', units='K')

if len(connection)>2:
    if connection[2]=='Temp':
        pw3.setLabel('left', 'Temperature', units='K')
        pw3.setLabel('bottom', 'Time', units='s')
    elif connection[2]=='Signalx vs Temp':
        pw3.setLabel('left', 'Signalx', units='V')
        pw3.setLabel('bottom', 'Temp', units='K')
    elif connection[2]=='Signaly vs Signalx':
        pw3.setLabel('left', 'Signaly', units='V')
        pw3.setLabel('bottom', 'Signalx', units='V')
    elif connection[2]=='Signaly vs Temp':
        pw3.setLabel('left', 'Signaly', units='V')
        pw3.setLabel('bottom', 'Temp', units='K')
        
if len(connection)>3:
    if connection[3]=='Temp':
        pw4.setLabel('left', 'Temperature', units='K')
        pw4.setLabel('bottom', 'Time', units='s')
    elif connection[3]=='Signalx vs Temp':
        pw4.setLabel('left', 'Signalx', units='V')
        pw4.setLabel('bottom', 'Temp', units='K')
    elif connection[3]=='Signaly vs Signalx':
        pw4.setLabel('left', 'Signaly', units='V')
        pw4.setLabel('bottom', 'Signalx', units='V')
    elif connection[3]=='Signaly vs Temp':
        pw4.setLabel('left', 'Signaly', units='V')
        pw4.setLabel('bottom', 'Temp', units='K')
#pw.setXRange(0, 2)
#pw.setYRange(0, 1e-10)

def write_to_file(temp=[],signaly=[],signalx=[],time=[],magnetic=[],\
                  capacitancex=[],capacitancey=[]):
    '''Writes a file that will be read later on, but appends data every 10
    samples'''
    
    if temp!=[]:
        with open('../{}/Temp.csv'.format(name),'a') as f:
            df = pd.DataFrame({'Temp':temp})
            df.to_csv(f,header=False,index=False)
            f.close()
        
    if signalx!=[]:
        with open('../{}/Signalx.csv'.format(name),'a') as f:
            df=pd.DataFrame({'Signalx':signalx})
            df.to_csv(f,header=False,index=False)
            f.close()
        
    if signaly!=[]:
        with open('../{}/Signaly.csv'.format(name),'a') as f:
            df=pd.DataFrame({'Signaly':signaly})
            df.to_csv(f,header=False,index=False)
            f.close()
        
    if time!=[]:
        with open('../{}/Time.csv'.format(name),'a') as f:
            df=pd.DataFrame({'Time':time})
            df.to_csv(f,header=False,index=False)
            f.close()
            
    if magnetic!=[]:
        with open('../{}/Magnetic.csv'.format(name),'a') as f:
            df=pd.DataFrame({'Magnetic':magnetic})
            df.to_csv(f,header=False,index=False)
            f.close()
            
    if resistor =='Capacitance' and capacitancex!=[] and capacitancey!=[]:
        with open('../{}/Capacitance_x.csv'.format(name),'a') as f:
            df=pd.DataFrame({'Capacitance_x':capacitancex})
            df.to_csv(f,header=False,index=False)
            f.close()
        with open('../{}/Capacitance_y.csv'.format(name),'a') as f:
            df=pd.DataFrame({'Capacitance_y':capacitancey})
            df.to_csv(f,header=False,index=False)
            f.close()
        
def collect_time():
    '''This function takes time information from the start of the trial and is
    appended to a csv file'''
    
    cur_time = [time.time()-start_time]*int(bit_rate)
    
    global change_time
    global current_voltage
    #print(cur_time[-1]-change_time)
    if cur_time[-1]-change_time>60 and include_voltage:
        print("Changing voltage")
        change_time=cur_time[-1]
        if current_voltage<=voltage_max and voltage_min<voltage_max:
            current_voltage+=voltage_incriment
            incriment_voltages(current_voltage)
        elif current_voltage>=voltage_max and voltage_min>voltage_max:
            current_voltage-=voltage_incriment
            incriment_voltages(current_voltage)
        else:
            incriment_voltages('0')
            sys.exit()
    
    return cur_time

def incriment_voltages(level):
    '''This is function I made that incriments voltage using myDAQ troublshoot
    test panel, which has an analog output tab, which allows you to change the
    output voltage of a channel, which is what we do here to use as a heater'''
    pyautogui.moveTo(1461, 111)
    
    pyautogui.click()
    
    for i in range(0,10):
        pyautogui.press('delete')
    
    pyautogui.typewrite(str(level))
    
    pyautogui.press('enter')
    
    pyautogui.moveTo(1701, 434)
    
    pyautogui.click()

def rand(connection):
    '''Returns the required data by writing and reading from the respective
    file'''
    directory='../{}'.format(name)
    if not os.path.exists(directory):
        os.makedirs(directory)
        
    if resistor=='Thermocouple':
        temp = collect_from_LA('Thermocouple')
    else:
        temp = collect_from_LA('Temp')

    signalx = collect_from_LA('Signalx')
    signaly = collect_from_LA('Signaly')
    if magnetometer == 1:
        magnetic = collect_from_LA('Magnetometer')
    elif magnetometer == 2:
        magnetic = collect_from_LA('Thermocouple')
    else:
        magnetic=[]
    if resistor=='Capacitance':
        capacitance_x = collect_from_LA('capacitancex')
        capacitance_y = collect_from_LA('capacitancey')
    else:
        capacitance_x = []
        capacitance_y = []
    time = collect_time()
    
    write_to_file(temp=temp,signalx=signalx,signaly=signaly,time=time,magnetic\
                  =magnetic,capacitancex=capacitance_x,capacitancey=\
                  capacitance_y)
    
    temp = np.loadtxt('../{}/Temp.csv'.format(name))
    signalx = np.loadtxt('../{}/Signalx.csv'.format(name))
    signaly = np.loadtxt('../{}/Signaly.csv'.format(name))
    if magnetometer == 1:
        magnetic = np.loadtxt('../{}/Magnetic.csv'.format(name))
    time = np.loadtxt('../{}/Time.csv'.format(name))
    #specifies what needs to be returned, but collects data on everything
    if resistor=='Capacitance':
        
        capacitance_x = np.loadtxt('../{}/Capacitance_x.csv'.format(name))
        capacitance_y = np.loadtxt('../{}/Capacitance_y.csv'.format(name))
        
        return capacitance_y,capacitance_x
    
    if connection=='Temp':
        
        if resistor=='Platinum':
            temp = platinum_resistor(temp)
        elif resistor=='Raw_Temp.':
            temp = raw_temp(temp)
        elif resistor=='RuO':
            temp = ruthenium_oxide(temp)
        elif resistor=='resistance':
            pass
        elif resistor=='Thermocouple':
            for i in np.arange(0,len(temp)):
                temp[i]+=273.15
            
        return temp,time
    
    if connection=='Signalx vs Temp':
        
        if resistor=='Platinum':
            temp = platinum_resistor(temp)
        elif resistor=='Raw_Temp.':
            temp = raw_temp(temp)
        elif resistor=='RuO':
            temp = ruthenium_oxide(temp)
        elif resistor=='resistance':
            pass
        elif resistor=='Thermocouple':
            for i in np.arange(0,len(temp)):
                temp[i]+=273.15
            
        return signalx,temp
    
    if connection=='Signaly vs Signalx':
        
        return signaly,signalx
    
    if connection=='Signaly vs Temp':
        
        if resistor=='Platinum':
            temp = platinum_resistor(temp)
        elif resistor=='Raw_Temp.':
            temp = raw_temp(temp)
        elif resistor=='RuO':
            temp = ruthenium_oxide(temp)
        elif resistor=='resistance':
            pass
        elif resistor=='Thermocouple':
            for i in np.arange(0,len(temp)):
                temp[i]+=273.15
            
        return signaly,temp

def collect_from_LA(connection):
    '''This function takes data from the Lock-in Amplifiers through the BNC-
    2120 and will be stored in a csv'''
    Samples_Per_Ch_To_Read = int(bit_rate)
    
    #The different devices to connect to depending on what exactly
    #we are looking to measure
    if connection=='Signaly':
        connection = 'Dev1/ai3'
    elif connection=='Signalx':
        connection='Dev1/ai2'
    elif connection=='Temp':
        connection = 'Dev1/ai4'
    elif connection=='Thermocouple':
        connection = 'Dev1/ai1'
    elif connection=='Magnetometer':
        connection = 'Dev1/ai5'
    elif connection=='capacitancex':
        connection = 'Dev1/ai6'
    elif connection=='capacitancey':
        connection = 'Dev1/ai7'
    
    #Interacts with the BNC-2120 board and takes information
    with nidaqmx.Task() as task:
        if connection=='Dev1/ai1':
            task.ai_channels.add_ai_thrmcpl_chan("Dev1/ai1",name_to_assign_to_channel="",\
                                                 units=nidaqmx.constants.TemperatureUnits.DEG_C,
                                     cjc_source=nidaqmx.constants.CJCSource.CONSTANT_USER_VALUE, cjc_val=20.0,
                                     cjc_channel="",thermocouple_type=nidaqmx.constants.ThermocoupleType.T)
        else:
            task.ai_channels.add_ai_voltage_chan("{}".format(connection))     
        data = task.read(Samples_Per_Ch_To_Read )
        
    return data

def raw_temp(R):
    '''This is for if you want to find the temperature with the regular setup
    that Di made with the resistors'''
    
    temp=[]

    for r in R:
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
        temp.append(T)
    return temp
	
def ruthenium_oxide(resistance):
    temp = []
    for r in resistance:
        #print(r)
        R0=np.abs(r)*10-5.06383
        #print(R0)
        a0 = -2.73909
        a1 = .908928*np.log(R0)
        a2 = .0305836*(np.log(R0))**2
        a3 = .0193592*(np.log(R0))**3
        X = a0+a1+a2+a3
        C = np.exp(-X)
        temp.append(C)
    
    return temp


def platinum_resistor(resistance):
    '''This is only for the platinum resistor, where you have to interpolate
    the temperature given the resistance'''
    temp = []
    resistance=abs(resistance)
    
    if resistance.size==1:
        idx = (np.abs(platinum_resistance - float(resistance))).argmin()
        temp.append(platinum_temperature[idx])
        return temp
    
    for i in range(0,len(resistance)):
        idx = (np.abs(platinum_resistance - resistance[i])).argmin()
        temp.append(platinum_temperature[idx])
        
    
    return temp
    

def updateData():
    '''This function does the updating, where it will take the data stored in
    the csvs and plot it, so it will continue from the last run aswell if given
    the same project name'''
    yd, xd = rand(connection[0])
    p1.setData(y=yd, x=xd)
    p1.show()
    if len(connection)>1:
        yd, xd = rand(connection[1])
        p2.setData(y=yd, x=xd)
        p2.show()
    if len(connection)>2:
        yd, xd = rand(connection[2])
        p3.setData(y=yd, x=xd)
        p3.show()
    if len(connection)>3:
        yd, xd = rand(connection[3])
        p4.setData(y=yd, x=xd)
        p4.show()
        
    time.sleep(.85)

## Start a timer to rapidly update the plot in pw
t = QtCore.QTimer()
t.timeout.connect(updateData)
t.start(50)
#updateData()

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()