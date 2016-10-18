#!/usr/bin/python 
#ultrasonic sonar module

import time
import RPi.GPIO as GPIO
# class for measuring the distance using ultrasonic  sonar module
# PIN Configurations
# GPIO 23 (pin 16) --> Trigger 
# GPIO 24 (pin 28) --> Echo
# VDD and GND 

class SonarSide:
	def __init__(self):
		self.distanec = 0
		self.GPIO_TRIGGER = 5
		self.GPIO_ECHO = 6
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(self.GPIO_TRIGGER,GPIO.OUT)
		GPIO.setup(self.GPIO_ECHO,GPIO.IN)
	def MeasureDistance(self):
		GPIO.output(self.GPIO_TRIGGER,False)
		time.sleep(0.5)
		GPIO.output(self.GPIO_TRIGGER, True)
		time.sleep(0.00001)
		GPIO.output(self.GPIO_TRIGGER,False)
		start = time.time()
		while GPIO.input(self.GPIO_ECHO)==0:
			start = time.time()
		while GPIO.input(self.GPIO_ECHO)==1:
			stop = time.time()
		elapsed = stop - start
		self.distance = elapsed * 34000
		self.distance = self.distance / 2
		print str(self.distance)
		GPIO.cleanup()
		return self.distance

if __name__ == '__main__':
	mSonar = SonarSide()
	mSonar.MeasureDistance()
