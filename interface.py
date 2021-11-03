'''
Interface:
    
    These functions are designed to take queries given by the user and turn 
    that into commands the SR830 lockin can understand. It then returns a 
    single value. This query process takes ~15-45ms and it only does one 
    operation at a time, so go easy on it if you don't want errors. All of them
    require you to define an instrument to be queried
    
'''
import pyvisa
import time

import pyvisa.errors as errors

#This is a master command list of all the functions the program will handle
command_list = {"Voltage":"SLVL","Frequency":"FREQ","Phase":"PHAS",
                "Input":"ISRC","Ground":"IGND","Couple":"ICPL","Filter":"ILIN",
                "Sensitivity":"SENS","Reserve":"RMOD","Time Constant":"OFLT",
                "Slope":"OFLT","Output":"OUTP","Offset":"OEXP",
                "Auto Offset":"AOFF","Output Multiple":"SNAP"}

def ask(command,instrument,number=''):
    '''Takes a command, like 'Voltage' and turns that into something the lockin
    will respond to, like "SLVL?' and return the value of that query. 
    ONLY FOR READING, NOT WRITING'''
    
    if not command in ['Output','Offset','Output Multiple']:
        number=''
    if command == 'Auto Offset':#Error handling
        print("This command cannot be queried because it is not askable")
        return 0
    
    return instrument.query('{}? {}\n'.format(command_list[command],str(number)))


def write(command,instrument,number):
    '''The one should only be used to write a command to the SR830. It should
    be noted that for some reason, the output of the query command to change
    a value does not return an EOL character, so you rely on timing out to end
    the process, which returns an error. So when you get a timeout error, that
    is how you know the process is done. But that also makes this function the
    most likely place for an unknown error to be if there is one.
    
    Offset:
        Requires commas between values, so Output 1,10,0
        '''
    
    #The error handling might be fixed by reading the output byte by byte, but
    #I don't want to bother with that just yet
    try:
        instrument.query('{} {}\n'.format(command_list[command],str(number)))
    except errors.VisaIOError as e:
        print(e)
        print("Changed {} to {}".format(command,number))
    

def test():
    '''This is for testing, imagine this is the main program calling each 
    function'''
    rm = pyvisa.ResourceManager()
    inst = rm.open_resource('COM4')
    inst.read_termination = '\r'
    inst.write_termination = '\r'
    inst.timeout = 100
    
    tick = time.time()
    V = ask('Output',inst,1)
    print(V)
    inst.close()
    
    tock = time.time()
    print(tock-tick)
    
if __name__ == '__main__': test()