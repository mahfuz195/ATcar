import serial
import threading
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
        ser.write(str(value))
        
def CollectSpeed():
      global real_speed
      while True:
        read_serial = ser.readline()
        #s[0] = str(float(ser.readline()))
        #print read_serial
        #print s[0]
	#print s[1]
        if "P" in read_serial :
                print 'spp'
        else:
               if isfloat(read_serial) :
                       speed = float(read_serial)# speed = float(read_serial.rstrip())
                       if (speed< 90.0) :
                               #print 'real_speed == ' + str(speed)
                               real_speed = speed
                               
#serial_read_thread = []
#ser_thread = threading.Thread(target = CollectSpeed)
#serial_read_thread.append(ser_thread)
#ser_thread.start()




		
