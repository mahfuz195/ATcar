import serial
ser = serial.Serial('/dev/ttyACM0',115200)
dir_count = 5 
def motor_dir(value):
	ser.write(str(value))
	return 
motor_dir(dir_count)

