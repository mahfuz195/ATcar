import serial
ser = serial.Serial('/dev/ttyACM0',115200)
count = 5 
def motor_dir(value):
	ser.write(str(value))
	return 
motor_dir(5)

