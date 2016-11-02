import serial
import time
ser = serial.Serial('/dev/ttyACM0',115200)
dir_count = 5 
def motor_dir(value):
	#start = time.time()
	#print 'writing value ' + str(value)
	ser.write(str(value))
	#end = time.time()
	#print 'writing time=' + str((end-start) * 1000) + ' ms'	
	return 
motor_dir(dir_count)

