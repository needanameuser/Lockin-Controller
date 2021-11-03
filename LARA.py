'''
LARA:
    Lockin Automated Requisition Apparatus (LARA). Yes I know it doesn't make
    sense, but I made this program and I can call it whatever I want
    
    Anyway, This is the main class that is used to control the lockin. To use,
    you simply need to type python ./LARA.py <Communication Port (COM4)>
    
    This class can do voltage and frequency sweeps and change certain values
    on the lockin itself. If you want to see the progress of the sweep, simply
    look at the terminal window you used to initialize this program.
'''

from PyQt5.QtWidgets import QMainWindow, QCheckBox,  QApplication, QWidget, \
QSizePolicy, QPushButton, QAction, QLineEdit, QMessageBox, QInputDialog, \
QLabel, QComboBox, QGridLayout
from PyQt5.QtGui import *  
from PyQt5 import QtWidgets, QtCore
import sys
import time
import pyvisa

from interface import write,ask

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        
        self.title = 'Lockin Automated Requisition Apparatus (LARA)'
        self.left = 0
        self.top = 50
        self.width = 480
        self.height = 220
        
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        Connection = sys.argv[-1]
        
        rm = pyvisa.ResourceManager()
        self.inst = rm.open_resource(Connection)
        self.inst.read_termination = '\r'
        self.inst.write_termination = '\r'
        self.inst.timeout = 100
        
        #Defining all variables as 0 at the start
        self.freq = '0'
        self.volt = '0'
        self.phas = '0'
        self.sens = '0'
        self.tcon = '0'
        
        self.fsweep_start_indicator = False
        self.vsweep_start_indicator = False
        
        self.ask_all_values()
        
        #Quit Button
        self.button = QPushButton('Quit',self)
        self.button.move(10,10)
        self.button.clicked.connect(self.exiting)
        
        self.settings = QPushButton('Set Values',self)
        self.settings.move(110,10)
        self.settings.clicked.connect(self.set_values)
        
        self.fsweep_press = QPushButton('F Sweep Start',self)
        self.fsweep_press.move(210,10)
        self.fsweep_press.clicked.connect(self.fsweep_starter)
        
        self.vsweep_press = QPushButton('V Sweep Start',self)
        self.vsweep_press.move(310,10)
        self.vsweep_press.clicked.connect(self.vsweep_starter)
        
        label=QLabel('Frequency:',self)
        label.move(10,50)
        
        self.frequency = QLineEdit(self.freq,self)
        self.frequency.move(85,55)
        self.frequency.resize(100,25)
        
        label=QLabel('Frequency Sweep:',self)
        label.move(195,50)
        
        label=QLabel('Start',self)
        label.move(305,30)
        
        label=QLabel('End',self)
        label.move(370,30)
        
        label=QLabel('Step/min',self)
        label.move(420,30)
        
        self.fsweep_start = QLineEdit('0',self)
        self.fsweep_start.move(295,55)
        self.fsweep_start.resize(50,25)
        
        self.fsweep_end = QLineEdit('0',self)
        self.fsweep_end.move(355,55)
        self.fsweep_end.resize(50,25)
        
        self.fsweep_inc = QLineEdit('0',self)
        self.fsweep_inc.move(415,55)
        self.fsweep_inc.resize(50,25)
        
        
        label=QLabel('Voltage:',self)
        label.move(10,80)
        
        self.voltage = QLineEdit(self.volt,self)
        self.voltage.move(85,85)
        self.voltage.resize(100,25)
        
        label=QLabel('Voltage Sweep:',self)
        label.move(195,80)
        
        self.vsweep_start = QLineEdit('0',self)
        self.vsweep_start.move(295,85)
        self.vsweep_start.resize(50,25)
        
        self.vsweep_end = QLineEdit('0',self)
        self.vsweep_end.move(355,85)
        self.vsweep_end.resize(50,25)
        
        self.vsweep_inc = QLineEdit('0',self)
        self.vsweep_inc.move(415,85)
        self.vsweep_inc.resize(50,25)
        
        
        label=QLabel('Phase:',self)
        label.move(10,110)
        
        self.phase = QLineEdit(self.phas,self)
        self.phase.move(85,115)
        self.phase.resize(100,25)
        
        
        label=QLabel('Sensitivity:',self)
        label.move(10,140)
        
        self.sensitivity = QLineEdit(self.sens,self)
        self.sensitivity.move(85,145)
        self.sensitivity.resize(100,25)
        
        
        label=QLabel('Time Constant:',self)
        label.move(10,170)
        
        self.time_constant = QLineEdit(self.tcon,self)
        self.time_constant.move(85,175)
        self.time_constant.resize(100,25)
        
        
        self.timer = QtCore.QTimer()
        self.timer.setInterval(15000)
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()


    def update_plot_data(self):
        '''Updates plot, collects all the data from the lockin, writes the info
        and changes voltage'''
        
        self.ask_all_values()
        
        if self.fsweep_start_indicator and float(self.freq)>=float(self.fsweep_end.text())\
        and float(self.fsweep_start.text())>float(self.fsweep_end.text()):
            write('Frequency',self.inst,float(self.freq)-float(self.fsweep_inc.text())/4)
        elif self.fsweep_start_indicator and float(self.freq)<=float(self.fsweep_end.text())\
        and float(self.fsweep_start.text())<float(self.fsweep_end.text()):
            write('Frequency',self.inst,float(self.freq)+float(self.fsweep_inc.text())/4)
        else:
            self.fsweep_start_indicator=False
            
        if self.vsweep_start_indicator and float(self.volt)>=float(self.vsweep_end.text())\
        and float(self.vsweep_start.text())>float(self.vsweep_end.text()):
            write('Voltage',self.inst,float(self.volt)-float(self.vsweep_inc.text())/4)
        elif self.vsweep_start_indicator and float(self.volt)<=float(self.vsweep_end.text())\
        and float(self.vsweep_start.text())<float(self.vsweep_end.text()):
            write('Voltage',self.inst,float(self.volt)+float(self.vsweep_inc.text())/4)
        else:
            self.vsweep_start_indicator=False
          
    
    
    def ask_all_values(self):
        '''If you supply a list of commands the ask function in interface.py 
        can understand, this funtion iterates over that and updates the 
        relevant values'''
        
        self.freq = ask('Frequency',self.inst)
        self.volt = ask('Voltage',self.inst)
        self.phas = ask('Phase',self.inst)
        self.sens = ask('Sensitivity',self.inst)
        self.tcon = ask('Time Constant',self.inst)
        
        
    def set_values(self):
        '''Write values to the lockin as they are given by the user'''
        
        write('Frequency',self.inst,float(self.frequency.text()))
        write('Voltage',self.inst,float(self.voltage.text()))
        write('Phase',self.inst,float(self.phase.text()))
        write('Sensitivity',self.inst,float(self.sensitivity.text()))
        write('Time Constant',self.inst,float(self.time_constant.text()))
        
    
    def exiting(self):
        self.inst.close()
        sys.exit()
        
        
    def fsweep_starter(self):
        self.fsweep_start_indicator = True
        write('Frequency',self.inst,float(self.fsweep_start.text()))
        
    
    def vsweep_starter(self):
        self.vsweep_start_indicator = True
        write('Voltage',self.inst,float(self.vsweep_start.text()))


app = QtWidgets.QApplication(sys.argv)
w = MainWindow()
w.show()
sys.exit(app.exec_())