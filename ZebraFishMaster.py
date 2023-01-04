#!/usr/bin/python3

import os
import tkinter
from numpy import *
from matplotlib.pyplot import *
from tkinter import filedialog
from serial import Serial
from serial.tools import list_ports
#from scipy.interpolate import interp1d
from threading import Thread
from time import *

#+++++++++++++++++++++++++++++++
#
# DEVICE VCP COMMUNICATION CLASS
#
#+++++++++++++++++++++++++++++++
class STM:
    s = None
    def __init__(self, tty, tm):
        self.tty = tty
        self.init(tm)

    def init(self, tm):
        if self.s:
            self.s.close()
        self.s = Serial(port=self.tty, timeout=tm)

    def hello(self, tty):
        self.s.write('\r'.encode())
        rpl = self.s.readline()        
        rpl = self.s.readline()        
        self.s.write('hello\r'.encode())
        rpl = self.s.readline()
        rpl = self.s.readline()
        if rpl == b'':
            print(' - '+tty+' did not respond!!!')
            return 0
        try:
            rpl = int(rpl.strip().decode())
        except:
            print(' - converting to int FAILED. '+tty+' responded: '+rpl)
            return 0

        if rpl == 167321907:
            return 1
        else:
            return 0

    def GetTemperature(self, unit):
        try: 
            self.s.write('\r'.encode())
            rpl = self.s.readline()       
            rpl = self.s.readline()        
            self.s.write(('temp %d\r' % unit).encode())
            rpl = self.s.readline()
            rpl = int(self.s.readline().strip().decode())
            return (rpl / 1000.0) + CAL[unit - 1]
        except:
            print('   temperature data read failed: unit #%d' % unit + ' - '+ ctime())
            return 7777777

    def GetIllumination(self, unit):
        try:
            unit += 128
            self.s.write(('light %d\r' % unit).encode())
            rpl = self.s.readline()
            rpl = int(self.s.readline().strip().decode())
            return rpl
        except:
            print('   illumination data read failed: unit #%d' % unit + ' - '+ ctime())
            return 7777777

    def SwithcPowerOn(self, pwrtime):
        try:
            self.s.write(('heat %d\r' % pwrtime).encode())
            rpl = self.s.readline()
            rpl = self.s.readline()
        except:
            print('   power switch failed - ' + ctime())
            return 7777777
# This one creates a list of the COM ports and ties to communicate with them.
# In case if the device responds correctly, it creates a serial STM class device
# Be careful, as the function will recognize and return the first appropriate device, which is an occasional choise!
def Device():
    success = 0
    CPlist = list_ports.comports()
    for p in range(len(CPlist)):
        dev = CPlist[p].device
        try:
            tmp   = STM(tty = dev, tm = 0.5)
            reply = tmp.hello(dev)
            print(reply)
            if reply:
                print(' - '+dev+' device is a valid VCP ERG-device and now connected!!!')
                return STM(tty = dev, tm = 3)
            else:
                print(' - '+dev+' device is not a valid VCP ERG-device!!!')
        except:
            pass

        return 0

def MakeMeasurement():
    TLOG     = []
    MAXPOWER = 300 # Watts. Heater nominal power
    POWER    = 200 # Initial guess. Should be corrected according to the experimental data.

    while 1:
        stm32 = Device()
        tmp = []
        if stm32:
            tm = time()
            # TEMPERATURE
            W.write(ctime() + '\t')
            for p in range(26):
            #for p in range(5):
                success = 0
                while not success:
                    temp = stm32.GetTemperature(p + 1)
                    if temp != 7777777:
                        print("temp", p+1, temp)
                        tmp.append(temp)
                        success = 1
                    else:
                        stm32 = 0
                        while not stm32:
                            tm = time()
                            stm32 = Device()
                            sleep(1.0)
                # write the data
                W.write('%7.2f' % temp)
                # update the monitor
                tBT[p]['text'] = '%5.2f' % temp
                if abs(temp - refT) > alarmT:
                    tBT[p]['bg'] = 'red'
                else:
                    tBT[p]['bg'] = 'green'
            W.write('\n')
            W.flush()
            # ILLUMINATION
            for p in range(4):
            #for p in range(1):
                success = 0
                while not success:
                    #ilum = stm32.GetIllumination(p + 1)
                    ilum = alarmL + 10 
                    if ilum != 7777777:
                        print("ilum", p+1, ilum)
                        success = 1
                    else:
                        stm32 = 0
                        while not stm32:
                            tm = time()
                            stm32 = Device()
                            sleep(1.0)
                # update the monitor
                if ilum < alarmL:
                    iBT[p]['bg'] = 'red'
                else:
                    iBT[p]['bg'] = 'green'

            #meanT = mean(tmp)
            sleep(mfreq - (time() - tm))
        else:
            print(' - device connection failed, retrying. ' + ctime())
            sleep(1.0)

        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # heating part of the deamon!!!
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        TLOG.append(mean(tmp))
        if len(TLOG) > 30:
            TLOG = TLOG[-30:]
            # reat angle
            angR = polyfit(linspace(0,30*mfreq,30), TLOG ,1)[0]
            # real delta
            dltT = refT - mean(TLOG)
            # desired ange, to reach the reference after an hour
            angD = arctan(dltT / 1.125*3600)
            # coef, heat capacity and the mass of water
            coef = 4200 * waterMass
            # desired power
            #print(POWER, angD, angR, coef)
            POWER = POWER + (angD - angR) * coef
            if POWER < 0:
                POWER = 0
            elif POWER > MAXPOWER:
                POWER = MAXPOWER
            print('POWER: %dW' % POWER)
            # switch power on. 29800 - is a bit less than 30 seconds
            stm32.SwithcPowerOn(round(29800 * POWER / MAXPOWER))
        # disconnect the device
        stm32 = 0
    
def plotGraph(unit):
    F = open(fname, 'r')
    lines = F.readlines()
    F.close()
    D = []
    for line in lines:
        D.append([mktime(strptime(line[:24])), float(line[24:].split()[unit])])
    D = array(D)
    plot(D[:,0] - D[0,0], D[:,1], color = cmap(unit / 25.0), lw = 2, label = 'unit %d' % (unit + 1))
    title('Temperature for the last day')
    xlabel('time, sec')
    ylabel('temperature, $^\circ$C')
    legend()
    show()


def QUIT():
    exit()


###########################################################################################
# VC and STM class creation

mfreq  = 30     # seconds between the measurements
alarmT = 0.5    # degrees of the deviation to color the button in red
alarmL = 1000   # arbitrary units of illumination
refT   = 25     # reference temperature
waterMass = 500 # total mass of water in fish factory

CAL    = [ 0.01, -0.26, -0.09, -0.12,  0.18,
          -0.07, -0.05,  0.20, -0.03, -0.06,
          -0.01, -0.02, -0.09, -0.02,  0.04,
           0.00,  0.18,  0.02, -0.49, -0.04,
           0.03, -0.05,  0.16,  0.02,  0.05,
           0.18]


cmap   = get_cmap('rainbow')

# OUTPUT LOG-FILE
dt = strptime(ctime())
fname = 'ErgZebraTemp-%04d.%02d.%02d-%02d:%02d.log' % (dt.tm_year, dt.tm_mon, dt.tm_mday, dt.tm_hour, dt.tm_min)
W = open(fname, 'w')

# WINDOW STUFF
root = tkinter.Tk()
root.title('ERG-ZEBRAFISH, v 1.01')
root.protocol('WM_DELETE_WINDOW', QUIT)
root.geometry('1060x600')
label = tkinter.Label(root, text='TEMERATURE', fg = '#0099ff')
label.config(font=("Times",22))
label.place(x = 310, y = 30)
label = tkinter.Label(root, text='LIGHT', fg = '#0099ff')
label.config(font=("Times",22))
label.place(x = 885, y = 30)
# temperature buttons
tBT = []
for q in range(3):
    for p in range(8):
        if q % 2:
            bt = tkinter.Button(root, text = " 0.00", height = 3, width = 4, command = lambda unit = 8*q + p: plotGraph(unit))
            bt.place(x = 30 + 100 * p, y = 90 + 100 * q)
            tBT.append(bt)
        else:
            pp = 7 - p
            bt = tkinter.Button(root, text = " 0.00", height = 3, width = 4, command = lambda unit = 8*q + pp: plotGraph(unit))
            bt.place(x = 30 + 100 * pp, y = 90 + 100 * q)
            tBT.append(bt)
        
for p in range(2):
    bt = tkinter.Button(root, text = " 0.00", height = 3, width = 4, command = lambda unit = 24 + p: plotGraph(unit))
    bt.place(x = 230 + 300 * p, y = 90 + 300)
    tBT.append(bt)
    
# illumination buttons
iBT = []
for p in range(4):
    bt = tkinter.Button(root, height = 3, width = 4)
    bt.place(x = 900, y = 90 + 100 * p)
    iBT.append(bt)

# measuring deamon
mThread = Thread(target = MakeMeasurement, daemon = True)
mThread.start()

root.mainloop()


