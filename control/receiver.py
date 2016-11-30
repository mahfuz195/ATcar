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
vid = 3
dist_desire  = frontSonar.MeasureDistance()
dist_actual  = 10
    
def PIDController():
    Eprev = 0
    Vprev = 0
    al = 0
    C = 0.5
    Kp = 0.8
    Kd = 0.2
    print 'in call pid controller function'
    global frontSonar , dist_actual , dist_desire , motor
    
    while True:
        dist_actual = frontSonar.MeasureDistance()
        print 'current dist:' + str(dist_actual)
        Ecurrent = dist_actual - dist_desire
        af = Kp * Ecurrent + Kd * (Ecurrent - Eprev) + C * al
        Vcurrent = af + Vprev
        Vprev = Vcurrent
        Eprev = Ecurrent
        if int(Vcurrent) > 40 :
            #Vcurrent = 40 
            motor.setSpeed(40)
        elif int(Vcurrent)< 0:
            #Vcurrent = 0 
            motor.setSpeed(0)
        else :
            motor.setSpeed(int(Vcurrent))
            
        motor.forward()
        #time.sleep()
        
        print 'speed:' + str(Vcurrent)

        #if dist_actual < 5 :
        #    motor.stop()
        #    return
        
        
threads = []       
def CallPID():
    print 'in call pid function'
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
        return [0,0,0,0,0]
        
def receiver():
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
            vid , dtime , speed , angle , headway = ParseVehicleData(message)
            print 'vid=' + str(vid) + ' time=' + str(dtime) + ' speed=' + str(speed)
            if int(vid) == 1 :
                print 'data from leader!'
                if float(dtime) != 0 :
                    print 'set speed = ' + str(speed)
                    motor.setSpeed(int(speed))
                    motor.forward()
                   
    except:
        print 'exception in comm::receiver()'
                
if __name__ == "__main__" :
    CallPID()
    receiver()
    #data = "$1,20.3,24,90,61.2#"
    #ParseVehicleData(data)
