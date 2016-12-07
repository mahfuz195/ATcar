#!/usr/bin/env python
import socket
import re
import RPi.GPIO as GPIO
import car_dir
import video_dir
import motor
from time import ctime          # Import necessary modules
import time
import select
import threading
from sonar_front import *
import motor
import sys

motor.setup() 
frontSonar = SonarFront()

motor.forward()
motor.stop()


#init classes
video_dir.setup()
car_dir.setup()
motor.setup()     # Initialize the Raspberry Pi GPIO connected to the DC motor. 
video_dir.home_x_y()
car_dir.home()

speed = 0
speed_max = 60
speed_min = 0
vid = 3
dist_desire  = 50
dist_actual  = frontSonar.MeasureDistance()

vid_leader = 1
dtime = 0
speed_leader = 0
speed  = 0
angle_leader = 0
headway_leader = 0
acc_leader = 0


	

def SafeDistance(speed):
	safe_dist  = 10 
	if speed < 20 :
		safe_dist = 10
	elif speed > 20 and speed < 30 :
		safe_dist = 15
	elif speed > 30 and speed < 40 :
		safe_dist = 25
	elif speed > 40 :
		safe_dist = 25
		
	return safe_dist

def AdaptiveCC():
	global frontSonar , dist_actual , dist_desire , motor , acc_leader , speed , speed_leader
	dist_desire  = 30
	time_current = time.time()
	time_prev = time_current
	error_prev = 0
	error_current = 0
	dist_actual = frontSonar.MeasureDistance()
	dist_prev = dist_actual
	speed = 0
	while True:
		time_current = time.time()
		dist_actual = frontSonar.MeasureDistance()
		#distance boundary checking
		if (dist_actual >= (dist_prev + 20)) or (dist_actual <= (dist_prev-20)):
			continue
		
		#dist collision checking
		if dist_actual <= dist_desire :
			sum_dist = 0
			for i in range(0,3):
				dist_temp = frontSonar.MeasureDistance()
				sum_dist = sum_dist + dist_temp
			sum_avg = sum_dist / 3.0

			if sum_avg <= dist_desire:
				speed = 0 
				motor.stop()
				
		# dist checing ends
			
		delta_dist = dist_actual - dist_prev
		#delta_dist = error_current
		delta_time = time_current - time_prev
		speed = speed + 2 *(delta_dist / delta_time)

		#speed limit checking
		if speed >= speed_max :
			speed = speed_max
		elif speed <= speed_min:
			speed = speed_min

		#set motor speed
		motor.forward()
		motor.setSpeed(int(speed))
		
		time_prev = time_current
		dist_prev = dist_actual

		print 'dist:' + str(dist_actual) + ' speed:' + str(speed)
		
		
def ModifiedPID():
	global frontSonar , dist_actual , dist_desire , motor , acc_leader , speed , speed_leader 
	Eprev = 0
	Vprev = speed
	al = 0
	C = 0.5
	Kp = 0.1
	Kd = 0.01
	Ki = 0.0
	error_prev = 0
	error_current = 0
	time_current = time.time()
	time_prev = time_current
	dist_actual = frontSonar.MeasureDistance()
	while True :
		dist_actual = frontSonar.MeasureDistance()
		
		#checking for safe dist
		if dist_actual < 30 :
			speed  = speed_min
			motor.forward()
			motor.setSpeed(int(speed))
			continue
		
		error_current = dist_actual -  dist_desire
		af = Kp * error_current + Kd * (error_current- error_prev) + C * float(acc_leader)
		speed_temp = af + speed

		#limit checking
		if speed_temp >= speed_max :
			speed = speed_max
		elif speed_temp <= speed_min :
			speed = speed_min
		else :
			speed = speed_temp


                        
		#change the motor
		motor.forward()
		motor.setSpeed(int(speed)-5 )

		print 'pid speed:' + str(speed)  + ' dist:' + str(dist_actual)
		#reinitialize
		speed_prev = speed
		error_prev = error_current
		


def PIDController():
	error_current = 0
	error_prev  = 0
	al = 0.0
	C = 5.95
	Kp = 1.505 #(105/1000.0)
	Kd = 2.0
	Ki = 0.0
	h = 0.95
	
	print 'in call pid controller function'
	global frontSonar , dist_actual , dist_desire , motor , acc_leader , speed_leader
	time_current  = time.time()
	time_prev = time_current
	speed_prev = 0
	speed = 0
	dist_prev = frontSonar.MeasureDistance()
	dist_actual = dist_prev
	
	dist_desire = 40 #SafeDistance(Vprev)
	print 'dist:' + str(dist_actual) + '\tspeed:' + str(speed_prev) + '\t\t time:' + str(time_current)
	sumError = 0 
	while True:
		time_current = time.time()
		temp_actual = frontSonar.MeasureDistance()

		if temp_actual > 100 :
			speed = speed_max
			speed_prev = speed
			motor.setSpeed(speed)
			continue
		if temp_actual < 5 :
			continue

		print 'dist:' + str(temp_actual)
		#continue
		
		
		if (temp_actual < 30):
			print 'need to stop:'
			if speed >= 30 :
				speed = speed / 3
			
			speed_prev = speed
			motor.forward()
			motor.setSpeed(int(speed))

			sum_dist = 0
			for i in range(0,1):
				temp = frontSonar.MeasureDistance()
				sum_dist = sum_dist + temp
			sum_avg = sum_dist / 1.0

			
			
			if sum_avg <= 30 :
				speed=0
				speed_prev = speed
				motor.forward()
				motor.setSpeed(int(speed))
				continue
		#if temp_actual > (dist_prev + 150):
		#	continue
		#if temp_actual > 300 :
		#	speed = speed_max
		#	motor.setSpeed(int(speed))
		#	continue
		
##		if (temp_actual >= (dist_prev + 100)):
##			dist_sum = 0 
##			for i in range(0,3):
##				temp = frontSonar.MeasureDistance()
##				dist_sum = dist_sum + temp
##			dist_avg = dist_sum / 3
##			if dist_avg <= dist_prev + 40 :
##				temp_actual = dist_avg
##			
##			else :
##				continue

				
		dist_actual = temp_actual
		error_current =  dist_actual - dist_desire
		dError = error_current - error_prev
		sumError = sumError + dError
		dTime  = time_current - time_prev

		#for simulation results
		#dTime = 1.0
		al = float(acc_leader)
		Td = Kd * (dError/dTime)
		Tp = Kp * error_current
		Tc = C * al
		af =  Tp + Td + Tc + (Ki * sumError)
		
		
		speed = af * 1 + speed_prev

		print 'dtime:'+str(dTime)+' __dist: '+str(dist_actual)+' af: ' + str(af) + ' error: ' +str(error_current) + ' Tp: ' + str(Tp) +  ' Td: ' + str(Td) + ' Ct: ' + str(Tc) 

		if (speed) >= speed_max :
			speed = speed_max
		elif (speed)<= speed_min:
			speed = speed_min
			
		if speed > speed_leader:
			speed = speed_leader
			
		motor.forward()
		motor.setSpeed(int(speed)-5)

		speed_prev = speed
		error_prev  = error_current
		time_prev = time_current
		#dist_desire = h * speed
		dist_prev = dist_actual
		
		#print 'c_dist:' + str(dist_actual) + '\tdDist:'+str(dist_desire)+ '\tspeed:' + str(speed_prev) + '\tdError:' + str(dError) + '\t dTime:' + str(dTime)

		print 'speed__________ ' + str(speed) + ' ___________'
		
		#dist_desire = (1.0/3.0) * speed + 30
		#if dist_desire < 30 :
		#	dist_desire = 30
                        
		#time.sleep()

		#if dist_actual < 5 :
		#    motor.stop()
		#    return
		
		
threads = []       
def CallPID():
	print 'in call pid function' 
	#thread_1 = threading.Thread(target=ModifiedPID)
	#thread_1 = threading.Thread(target=AdaptiveCC)
	thread_1 = threading.Thread(target=PIDController)
	threads.append(thread_1)
	thread_1.start()



for i in range(0,5):
	video_dir.move_increase_y()
	time.sleep(.5)
	print 'increasing'
	
#motor.setSpeed(0)
#while True:
#    print 'hello'
#    time.sleep(1)

def ParseVehicleData(data):
	if data.find('$') != -1 and data.find('#') != -1:
		#vid , dtime , speed , angle , headway = data.split(' $#,')
		return filter(None,re.split("[,\-!$#]",data))
		#print 'time='
	else :
		return [0,0,0,0,0,0]
		
def receiver():
	global motor , vid , dtime , speed_leader,speed , angle, headway_leader ,acc_leader
	try:
		my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
		my_socket.bind(('',8881))

		print ('start service ...')
		
		while True :
			message , address = my_socket.recvfrom(8192)
			#this is for testing
			#message = "$1,20.3,24,90,61.2#"
			vid , dtime , speed_temp , angle , headway , acc_temp = ParseVehicleData(message)
			#print 'vid=' + str(vid) + ' time=' + str(dtime) + ' speed=' + str(speed) + ' acc=' + str(acc)
			if int(vid) == vid_leader :
				#print 'data from leader!'
				if float(dtime) != 0 :
					acc_leader = acc_temp
					speed_leader = speed_temp
					#print '\n leader acc:' + str(acc_leader)
					#print 'set speed = ' + str(speed)
					#motor.forward()
					#motor.setSpeed(int(float(speed.strip())))
					
				   
	except ValueError:
		print 'exception in comm::receiver() value error'
	except :
		print 'exception in comm::receiver()' + str(sys.exc_info()[0])
		
				
if __name__ == "__main__" :
	CallPID()
	receiver()
	#motor.forward()
	#motor.setSpeed(0)
	
	#data = "$1,20.3,24,90,61.2#"
	#ParseVehicleData(data)
