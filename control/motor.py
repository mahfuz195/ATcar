#!/usr/bin/env python
import RPi.GPIO as GPIO
import PCA9685 as pwm
import serial 
import time    # Import necessary modules

# ===========================================================================
# Raspberry Pi pin11, 12, 13 and 15 to realize the clockwise/counterclockwise
# rotation and forward and backward movements
# ===========================================================================
Motor0_A = 11  # pin11
Motor0_B = 12  # pin12
Motor1_A = 13  # pin13
Motor1_B = 15  # pin15

# ===========================================================================
# Set channel 4 and 5 of the servo driver IC to generate PWM, thus 
# controlling the speed of the car
# ===========================================================================
EN_M0    = 4  # servo driver IC CH4
EN_M1    = 5  # servo driver IC CH5

pins = [Motor0_A, Motor0_B, Motor1_A, Motor1_B]

p = pwm.PWM()
ser = serial.Serial('/dev/ttyACM0',9600)
        
# ===========================================================================
# Adjust the duty cycle of the square waves output from channel 4 and 5 of
# the servo driver IC, so as to control the speed of the car.
# ===========================================================================

def setSpeed(speed):
	speed *= 40
	#print 'speed is: ', speed
	p.set_value(EN_M0, 0, speed)
	p.set_value(EN_M1, 0, speed)

def setup():
	global forward0, forward1, backward1, backward0
	forward0 = 'True'
	forward1 = 'True'
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BOARD)        # Number GPIOs by its physical location
	try:
		for line in open("config"):
			if line[0:8] == "forward0":
				forward0 = line[11:-1]
			if line[0:8] == "forward1":
				forward1 = line[11:-1]
	except:
		pass
	if forward0 == 'True':
		backward0 = 'False'
	elif forward0 == 'False':
		backward0 = 'True'
	if forward1 == 'True':
		backward1 = 'False'
	elif forward1 == 'False':
		backward1 = 'True'
	for pin in pins:
		GPIO.setup(pin, GPIO.OUT)   # Set all pins' mode as output

# ===========================================================================
# Control the DC motor to make it rotate clockwise, so the car will 
# move forward.
# ===========================================================================

def motor0(x):
	GPIO.setmode(GPIO.BOARD)
	if x == 'True':
		GPIO.output(Motor0_A, GPIO.LOW)
		GPIO.output(Motor0_B, GPIO.HIGH)
	elif x == 'False':
		GPIO.output(Motor0_A, GPIO.HIGH)
		GPIO.output(Motor0_B, GPIO.LOW)
	else:
		print 'Config Error'

def motor1(x):
	GPIO.setmode(GPIO.BOARD)
	if x == 'True':
		GPIO.output(Motor1_A, GPIO.LOW)
		GPIO.output(Motor1_B, GPIO.HIGH)
	elif x == 'False':
		GPIO.output(Motor1_A, GPIO.HIGH)
		GPIO.output(Motor1_B, GPIO.LOW)

def forward():
	motor0(forward0)
	motor1(forward1)

def backward():
	motor0(backward0)
	motor1(backward1)

def forwardWithSpeed(spd = 50):
	setSpeed(spd)
	motor0(forward0)
	motor1(forward1)

def backwardWithSpeed(spd = 50):
	setSpeed(spd)
	motor0(backward0)
	motor1(backward1)

def stop():
	GPIO.setmode(GPIO.BOARD)
	for pin in pins:
		GPIO.setup(pin, GPIO.OUT) 
		GPIO.output(pin, GPIO.LOW)
	#GPIO.setmode(GPIO.BOARD)
# ===========================================================================
# The first parameter(status) is to control the state of the car, to make it 
# stop or run. The parameter(direction) is to control the car's direction 
# (move forward or backward).
# ===========================================================================
def ctrl(status, direction=1):
	if status == 1:   # Run
		if direction == 1:     # Forward
			forward()
		elif direction == -1:  # Backward
			backward()
		else:
			print 'Argument error! direction must be 1 or -1.'
	elif status == 0: # Stop
		stop()
	else:
		print 'Argument error! status must be 0 or 1.'

def test():
	while True:
		setup()
		ctrl(1)
		time.sleep(3)
		setSpeed(10)
		getSpeed()
		time.sleep(3)
		setSpeed(100)
		time.sleep(3)
		getSpeed()

		ctrl(0)
def isfloat(value):
	try :
		float(value)
		return True
	except :
		return False 
		
def getSpeed():
        global ser
        read_serial = ser.readline()
        if "P" in read_serial :
                print 'text data'
        else :
                if isfloat(read_serial) :
                        real_spd = float(read_serial)
                        if(real_spd < 90.0):
                                print 'read+speed = ' + str(real_spd)
                                return real_spd
def pid_speed():
        return 
	
if __name__ == '__main__':
	setup()
	#test()
	setSpeed(60)
	#getSpeed()
	#getSpeed()
	#getSpeed()
	forward()
	time.sleep(3)
	#backward()
	time.sleep(2)
	stop()
	setSpeed(40)
	#forward()
	#getSpeed()
	#getSpeed()
	#getSpeed()
