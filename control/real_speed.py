import serial
import threading
import time
import re
import time
import sys
ser = serial.Serial('/dev/ttyACM0',9600)
s = [0,1]
real_speed = 0.0

def isfloat(value):
        try:
                float(value)
                return True
        except:
                return False
def getSpeed():
        global real_speed
        return real_speed

def setSpeed(value):
        print 'setting speed ' + str(value)
        ser.write(str(int(value)))
def setup():
        serial_read_thread = []
        ser_thread = threading.Thread(target = CollectSpeed)
        serial_read_thread.append(ser_thread)
        ser_thread.start()        
def CollectSpeed():
      global real_speed
      while True:
        read_serial = ser.readline()
        #s[0] = str(float(ser.readline()))
        print read_serial
        if "P" in read_serial :
                print 'spp'
        elif "," in read_serial:
                try:
                        real_speed , real_time = filter(None,re.split("[,\!$#]",read_serial))
                        if isfloat(real_speed):
                                print ' real_speed = ' + str(float(real_speed)) + " time=" + str(real_time)
                except :
                        print 'error'
 
                #if isfloat(read_serial) :
                #       speed = float(read_serial)# speed = float(read_serial.rstrip())
                #       print 'real_speed == ' + str(speed)
                #       if (speed< 90.0) :
                #               #print 'real_speed == ' + str(speed)
                #               real_speed = speed
                               
#setup()
#setSpeed(60)
#time.sleep(5)
#getSpeed()
#setSpeed(50)
#time.sleep(5)
#getSpeed()

