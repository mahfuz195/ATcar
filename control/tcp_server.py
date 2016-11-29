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
        
def ObstacleDetection():
        global isObstacle, frontSonar , speed ;
        dist = frontSonar.MeasureDistance()
        while True:
                prev_speed = speed
                if dist < 60 :
                        isObstacle = True
                        print 'obstacle detected! dist=' + str(dist)
                        speed = 0
                        motor.stop()
                        motor.stop()

                        while isObstacle:
                                sum_dist = 0
                                for i in range(0,3):
                                        dist = frontSonar.MeasureDistance()
                                        if dist < 60 :
                                                if i==0 :
                                                        prev_speed = speed
                                                speed = 40
                                                spd = speed
                                                motor.setSpeed(40)
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
                        motor.setSpeed(prev_speed)
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
                                motor.setSpeed(40)
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
                        data = '$' + str(vid) + ',' + str(time.time()) +','+ str(speed) +','+ str(angle) +',' + str(headway) +'#'
                        broadcast_socket.sendto(data, broadcast_dest)
                time.sleep(0.2)

#start broadcasting thread
threads = []
thread_1 = threading.Thread(target=BroadcastData)
threads.append(thread_1)
thread_2 = threading.Thread(target=ObstacleDetection)
threads.append(thread_2)

thread_1.start()
thread_2.start()


while True:
        print 'Waiting for connection...'
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
                        motor.ctrl(0)
                        speed = 0
                        spd = 0
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
                                print 'tmp(str) = %s' % tmp
                                spd = int(tmp)
                                print 'spd(int) = %d' % spd
                                if spd < 24:
                                        spd = 24
                                motor.setSpeed(spd)
                                speed = spd
                                
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
                                                        
                speed  = spd
                
                
running = False
tcpSerSock.close()
broadcast_socket.close()



