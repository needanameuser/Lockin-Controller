#try it nowAsk again laterDon't show again
from pymeasure.instruments.srs import SR830
from pymeasure.adapters import SerialAdapter, PrologixAdapter, VISAAdapter

import time
import serial
import pyvisa

def other():
    
    rm = pyvisa.ResourceManager()
    print(rm.list_opened_resources())
    inst = rm.open_resource('COM4')
    inst.read_termination = '\r'
    inst.write_termination = '\r'
    inst.timeout = 2000
    
    tick = time.time()
    print(inst.query('SLVL?\n'))
    tock = time.time()
    print(tock-tick)
    inst.close()
    
    #print(deviceID)

def main():
    ser = serial.Serial(
        port='COM4',
        baudrate=19200,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        dsrdtr=True)
    print(ser.isOpen())
    ser.timeout=1
    ser.write("FREQ? \r\n".encode()) #Asks the Lock-in for x-value
    ser.write("++read\r\n".encode())
    x=ser.readline()
    print(x)
if __name__ == '__main__': other()

def test():
    # configure the serial connections (the parameters differs on the device you are connecting to)
    ser = serial.Serial(
        port='COM4',
        baudrate=9600,
        parity=serial.PARITY_NONE,
        #stopbits=serial.STOPBITS_TWO,
        bytesize=serial.EIGHTBITS
    )
    
    print(ser.isOpen())
    ser.write('OUTX0\r'.encode('utf-8'))
    #adapter = SerialAdapter(ser)
    #lockin = SR830(adapter)
    #print(lockin)
    #print(lockin.frequency)
    
    print ('Enter your commands below.\r\nInsert "exit" to leave the application.')
    #input=1
    while 1 :
        # get keyboard input
        #input = raw_input(">> ")
        # Python 3 users
        message = input(">> ")
        message = message.strip('\n')
        if message  == 'exit':
            ser.close()
            exit()
        else:
            # send the character to the device
            # (note that I happend a \r\n carriage return and line feed to the characters - this is requested by my device)
            #message = message + '\r'
            ser.write(message.encode('utf-8'))
            out = ''
            # let's wait one second before reading output (let's give device time to answer)
            time.sleep(1)
            while ser.inWaiting() > 0:
                out += ser.read(1)
    
            if out != '':
                print(">>" + out)
    #beep
    #Shaun Froude-Powers
    #Tue 10/12/2021 2:43 PM
    #boop