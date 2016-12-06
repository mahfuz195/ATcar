#!/usr/bin/env python
import RPi.GPIO as GPIO
import video_dir
import car_dir
import motor
from socket import *
from time import ctime          # Import necessary modules
import time
import select
import threading
from sonar_front import *

frontSonar = SonarFront()

ctrl_cmd = ['forward', 'backward', 'left', 'right', 'stop', 'read cpu_temp', 'home', 'distance', 'x+', 'x-', 'y+', 'y-', 'xy_home']

HOST = ''           # The variable of HOST is null, so the function bind( ) can be bound to all valid addresses.
PORT = 21567
BUFSIZ = 1024       # Size of the buffer
ADDR = (HOST, PORT)

tcpSerSock = socket(AF_INET, SOCK_STREAM)    # Create a socket.
tcpSerSock.bind(ADDR)    # Bind the IP address and port number of the server. 
tcpSerSock.listen(5)     # The parameter of listen() defines the number of connections permitted at one time. Once the 
			 # connections are full, others will be rejected. 
#tcpSerSock.setblocking(0)

video_dir.setup()
car_dir.setup()
motor.setup()     # Initialize the Raspberry Pi GPIO connected to the DC motor. 
video_dir.home_x_y()
car_dir.home()

speed_max = 60.0
speed_min = 0.0
speed_target = -1.0
car_acceleration = 0.0

threads = []     
	
for i in range(0,5):
	video_dir.move_increase_y()
	time.sleep(0.5)
	

broadcast_socket = socket(AF_INET, SOCK_DGRAM)
broadcast_socket.bind(('',0))
broadcast_socket.setsockopt(SOL_SOCKET, SO_BROADCAST,1)
broadcast_dest = ('<broadcast>',8881)

vid             = 1
speed           = 0
angle           = 0
headway         = 0
running         = False 
spd             = 0
isObstacle      = False

#car dir test
#car_dir.turn(0)
#while True:
#        print 'hello'
#        time.sleep(1)
def CalculateCarSpeedPID():
	global speed , speed_target , motor , car_acceleration

	#inti speed checking
	if(speed_target == -1.0):
		return

	#print 'target speed:' + str(speed_target) + ' current speed:' + str(speed)
	
	error_current  = 0.0
	error_prev = 0.0
	time_current = time.time()
	time_prev = time_current
	temp_speed = speed
	speed_prev = speed

	# PID coefficients
	Kp = 0.03
	Kd = 0.0
	
	while True :
		time_current = time.time()
		if (speed_target < speed +1) and (speed_target > speed-1):
			return
		error_current = speed_target - speed
		delta_error = error_current - error_prev
		delta_time  = (time_current - time_prev)

		term_d = (delta_error) / (delta_time)
		term_p = error_current
		
		speed_temp = speed + (Kp * error_current + Kd * term_d)

		#print 'motor pid speed:' + str(speed_temp)
		
		#limit checking
		if speed_temp >= speed_max :
			speed_temp = speed_max
		elif speed_temp <= speed_min:
			speed_temp = speed_min

		#run motor        
		speed = speed_temp
		motor.forward()
		motor.setSpeed(int(speed))
		
		#print 'motor pid speed:' + str(speed)

		#init pid vaiables
		error_current = error_prev
		time_prev = time_current  

		#calculate car_acceleration
		delta_speed = speed - speed_prev
		car_acceleration = (delta_speed) / delta_time
		speed_prev = speed

		print '\n' + str(time_current) + ',' + str(speed)
		
		#if (car_acceleration < 1000) and (car_acceleration>-1000):
			#print 'acc:' + str(car_acceleration)
                
		
		
		
def SetPIDSpeed():
	#start the thread here.
	thread_3 = threading.Thread(target=CalculateCarSpeedPID)
	threads.append(thread_3)
	thread_3.start()
	return 0

def ObstacleDetection():
	global isObstacle, frontSonar , speed , speed_target;
	dist = frontSonar.MeasureDistance()
	dist_prev = dist
	time_current = time.time()
	time_prev = time_current
	speed_current = 0
	speed_prev = 0
	limit = 4
	count = limit
	speed_before_stop = speed
	isCarStoped = False
	
	while True:
		time_current = time.time()
		dist_current = frontSonar.MeasureDistance()

		#print 'current_dist:' + str(dist_current)
		
		#brute forse stop
		if dist_current < 30 :
			#make sure if this is correct result or not
			dist_sum = 0
			for i in range(0,3):
				dist_temp = frontSonar.MeasureDistance()
				dist_sum = dist_sum + dist_temp
				
			dist_avg = dist_sum / 3.0
			
			#if this is below 30 then assumed to be correct data.
			if dist_avg < 30 :
				speed_before_stop = speed
				speed = 0
				spd = 0
				isCarStoped = True
				motor.setSpeed(0)

		#slow stop 
		if dist_current < 120 and (dist_current < dist_prev) :
			count = count - 1
			#if count == 2 :
				#speed_target = 30
				#SetPIDSpeed()
			
		else :
			count = limit

		if count == 0 :
			#print 'need to stop!'
			speed_before_stop = speed
			speed_target = 0
			isCarStoped = True
			SetPIDSpeed()
			count = limit
		if isCarStoped == True :
			# MAKE SURE THAT READING IS CORRECT
			while isCarStoped:
				#wait until the obstacle is gone!
				dist_sum = 0
				for i in range(0,3):
					dist_temp = frontSonar.MeasureDistance()
					dist_sum = dist_sum + dist_temp
				dist_avg = dist_sum / 3.0
				if dist_avg > 100 :
					time.sleep(2)
					isCarStoped = False
					speed_target = speed_before_stop
					#print 'target speed:' + str(speed_before_stop)
					SetPIDSpeed()
		#calculate the velocity
##                delta_dist = dist_prev - dist_current
##                delta_time = time_current - time_prev
##
##                speed_current = delta_dist / delta_time
##
##                if (speed_current <= speed_prev + limit) and (speed_current>= speed_prev-limit):
##                        count = count - 1
##                else :
##                        count = 3
 
		#print 'cur speed:' + str(speed_current) + " prev:" + str(speed_prev) + " count:" + str(count)
		time_prev = time_current
		dist_prev = dist_current
		speed_prev = speed_current
		
		print '\n' + str(time_current) + ',' + str(speed)
		
		time.sleep(0.1)
			   
	
	while True:
		prev_speed = speed
		if dist < 60 :
			isObstacle = True
			print 'obstacle detected! dist=' + str(dist)
			speed = 0
			speed_target = 0
			SetPIDSpeed()
			
			#motor.stop()
			#motor.stop()

			while isObstacle:
				sum_dist = 0
				for i in range(0,3):
					dist = frontSonar.MeasureDistance()
					if dist < 60 :
						if i==0 :
							prev_speed = speed
						speed = 40
						spd = speed
						speed_target = 30 
						SetPIDSpeed()
						#motor.setSpeed(40)
					sum_dist =  sum_dist + dist
				dist = sum_dist / 3
				
				if dist > 60 :
					isObstacle = False
					print 'no obstacle! dist=' + str(dist)
					speed = prev_speed
				else :
					isObstacle = True
					print 'obstacle detected! dist=' + str(dist)
			
			
		else :
			isObstacle  = False
			motor.forward()
			print 'no obstacle..moving forward with speed:' + str(prev_speed)
			speed_target = prev_speed 
			SetPIDSpeed()
			#motor.setSpeed(prev_speed)
			speed = prev_speed
			
		#time.sleep(.1)
		sum_dist = 0
		for i in range(0,3):
			dist = frontSonar.MeasureDistance()
			if dist < 60 :
				if(i==0):
					prev_speed = speed
				speed = 40
				spd = speed
				speed_target = 30
				SetPIDSpeed()
				#motor.setSpeed(40)
			sum_dist =  sum_dist + dist
		dist = sum_dist / 3.0
						
		#dist = frontSonar.MeasureDistance()
		print 'front dist :' + str(dist)

def BroadcastData():
	print 'in Broadcast thread'
	global broadcast_socket , broadcast_dest , running
	global vid, speed, angle , headway
	while True:
		if running == True:
			time_current = time.time()
			#print str(time_current) + ',' + str(speed)
			data = '$' + str(vid) + ',' + str(time.time()) +','+ str(speed) +','+ str(angle) +',' + str(headway) +','+str(car_acceleration)+'#'
			broadcast_socket.sendto(data, broadcast_dest)
			#print time.time()
		time.sleep(0.2)

#start broadcasting thread
thread_1 = threading.Thread(target=BroadcastData)
threads.append(thread_1)
thread_2 = threading.Thread(target=ObstacleDetection)
threads.append(thread_2)

thread_1.start()
thread_2.start()


while True:
	#print 'Waiting for connection...'
	# Waiting for connection. Once receiving a connection, the function accept() returns a separate 
	# client socket for the subsequent communication. By default, the function accept() is a blocking 
	# one, which means it is suspended before the connection comes.
	tcpCliSock, addr = tcpSerSock.accept() 
	print '...connected from :', addr     # Print the IP address of the client connected with the server.
	running = True         #now start broadcast the current status
	angle   = 0
	headway = 0
	while True:
		# data initalization
		data = ''
		tcpCliSock.settimeout(None)
		tcpCliSock.setblocking(0)
		data = tcpCliSock.recv(BUFSIZ)    # Receive data sent from the client. 
		# Analyze the command received and control the car accordingly.
		if not data:
			break
		if data == ctrl_cmd[0]:
			print 'motor moving forward'
			motor.forward()
		elif data == ctrl_cmd[1]:
			print 'recv backward cmd'
			motor.backward()
		elif data == ctrl_cmd[2]:
			print 'recv left cmd'
			car_dir.turn_left()
		elif data == ctrl_cmd[3]:
			print 'recv right cmd'
			car_dir.turn_right()
		elif data == ctrl_cmd[6]:
			print 'recv home cmd'
			car_dir.home()
		elif data == ctrl_cmd[4]:
			print 'recv stop cmd'
			#motor.ctrl(0)
			spd = 0
			speed_target = spd
			SetPIDSpeed()
			#speed = 0
			#spd = 0
		elif data == ctrl_cmd[5]:
			print 'read cpu temp...'
			temp = cpu_temp.read()
			tcpCliSock.send('[%s] %0.2f' % (ctime(), temp))
		elif data == ctrl_cmd[8]:
			print 'recv x+ cmd'
			video_dir.move_increase_x()
		elif data == ctrl_cmd[9]:
			print 'recv x- cmd'
			video_dir.move_decrease_x()
		elif data == ctrl_cmd[10]:
			print 'recv y+ cmd'
			video_dir.move_increase_y()
		elif data == ctrl_cmd[11]:
			print 'recv y- cmd'
			video_dir.move_decrease_y()
		elif data == ctrl_cmd[12]:
			print 'home_x_y'
			video_dir.home_x_y()
		elif data[0:5] == 'speed':     # Change the speed
			print data
			numLen = len(data) - len('speed')
			if numLen == 1 or numLen == 2 or numLen == 3:
				tmp = data[-numLen:]
				#print 'tmp(str) = %s' % tmp
				spd = int(tmp)
				#print 'spd(int) = %d' % spd
				if spd < 24:
					spd = 24
					motor.setSpeed(spd)
					speed = spd

				else :
					speed_target = spd
					SetPIDSpeed()
				#motor.setSpeed(spd)
				#speed = spd
				
		elif data[0:5] == 'turn=':      #Turning Angle
			print 'data =', data
			angle = data.split('=')[1]
			try:
				angle = int(angle)
				car_dir.turn(angle)
			except:
				print 'Error: angle =', angle
		elif data[0:8] == 'forward=':
			print 'data =', data
			spd = data[8:]
			try:
				spd = int(spd)
				motor.forward(spd)
			except:
				print 'Error speed =', spd
		elif data[0:9] == 'backward=':
			print 'data =', data
			spd = data.split('=')[1]
			try:
				spd = int(spd)
				motor.backward(spd)
				speed = spd 
			except:
				print 'ERROR, speed =', spd

		else:
			print 'Command Error! Cannot recognize command: ' + data

		#global variables 
							
		#speed  = spd
		
		
running = False
tcpSerSock.close()
broadcast_socket.close()



