#!/usr/bin/env python
import RPi.GPIO as GPIO
import video_dir
import car_dir
import motor
from socket import *
from time import ctime          # Import necessary modules   
from sonar_front import *
from sonar_side import *
import dir_control
import math
import updated_dir_control

dir_count = 5

HOST = ''           # The variable of HOST is null, so the function bind( ) can be bound to all valid addresses.
PORT = 21667
BUFSIZ = 1024       # Size of the buffer
ADDR = (HOST, PORT)

tcpSerSock = socket(AF_INET, SOCK_STREAM)    # Create a socket.
tcpSerSock.bind(ADDR)    # Bind the IP address and port number of the server. 
tcpSerSock.listen(5)     # The parameter of listen() defines the number of connections permitted at one time. Once the 
                         # connections are full, others will be rejected. 

frontSonar = SonarFront()
sideSonar = SonarSide()

def setup():
      global offset_x,  offset_y, offset, forward0, forward1
      offset_x = 0
      offset_y = 0
      offset = 0
      forward0 = 'True'
      forward1 = 'False'
      try:
              for line in open('config'):
                      if line[0:8] == 'offset_x':
                              offset_x = int(line[11:-1])
                              print 'offset_x =', offset_x
                      if line[0:8] == 'offset_y':
                              offset_y = int(line[11:-1])
                              print 'offset_y =', offset_y
                      if line[0:8] == 'offset =':
                              offset = int(line[9:-1])
                              print 'offset =', offset
                      if line[0:8] == "forward0":
                              forward0 = line[11:-1]
                              print 'turning0 =', forward0
                      if line[0:8] == "forward1":
                              forward1 = line[11:-1]
                              print 'turning1 =', forward1
      except:
              print 'no config file, set config to original'
      video_dir.setup()
      car_dir.setup()
      motor.setup() 
      video_dir.calibrate(offset_x, offset_y)
      car_dir.calibrate(offset)

def REVERSE(x):
      if x == 'True':
              return 'False'
      elif x == 'False':
              return 'True'
def dir_test():
      global frontSonar , sideSonar
      currDist = sideSonar.MeasureDistance()
      dDist = 5
      prevDist = currDist
      theta = 5
      desDist = 20

      dir_control.motor_dir(theta)
        
      motor.setSpeed(50)
      motor.motor0(forward0)
      motor.motor1(forward1)
      
      while True:
                      motor.setSpeed(50)
              motor.motor0(forward0)
              motor.motor1(forward1)
              time.sleep(0.5)
              motor.stop()
              curDist= sideSonar.MeasureDistance()
              prevDist , theta = updated_dir_control.calculateDir(prevDist,curDist,theta,desDist,dDist)
              dir_control.motor_dir(theta)
              print str(theta) 
              time.sleep(5)
                
def loop():
      global offset_x, offset_y, offset, forward0, forward1
      global frontSonar , sideSonar
      global dir_count
      motor.setup()

      
      #while True:
      #       motor.stop()
      dir_test()
      
      while True:
              print 'Waiting for connection...'
              # Waiting for connection. Once receiving a connection, the function accept() returns a separate 
              # client socket for the subsequent communication. By default, the function accept() is a blocking 
              # one, which means it is suspended before the connection comes.
              #tcpCliSock, addr = tcpSerSock.accept() 
              #print '...connected from :', addr     # Print the IP address of the client connected with the server.
              # this part is for testing 
              while False:
                      motor.stop()
              current_t2 = time.time()
              old_t1 = current_t2
              y2 = 0 
              y1 = y2
              angel = 5
              turn = 0 

              while True:
                      #sideDist = sideSonar.MeasureDistance()
                        frontDist= frontSonar.MeasureDistance()
                        print 'front dist' + str(frontDist)
                                      

                      if turn  == -1 :
                              if sideDist < 10 : 
                                      dir_count = 5 ; 
                                      dir_control.motor_dir(dir_count)
                              
                      y2 = int(sideDist)
                      current_t2 = time.time()                        
                      if y2 != y1:
                              if current_t2 != old_t1 :
                                      angel = math.degrees(math.atan((y2-y1)/(current_t2-old_t1)))
                                      if (angel) >10 or (angel)<-10: 
                                              dir_count = 5 - int(angel / 10)
                                              print 'angel = ' + str(angel) + ' motor dir = ' + str(dir_count)
                                              dir_control.motor_dir(dir_count)
                                              if dir_control == 5 :
                                                      turn  = 0 
                                              elif dir_count < 5 : 
                                                      trun = -1 
                                              else :
                                                      turn  = 1
                                              old_t2 = current_t2
                                              y1 = y2 
                      #print 'Distance=' + str(frontDist)
                      if frontDist<20:                        
                              #print 'motor shuloud stop'                     
                              motor.stop()
                      else :
                              motor.stop()
                              #motor.setSpeed(50)
                              #motor.motor0(forward0)
                              #motor.motor1(forward1)
                      if sideDist == 0 :
                              print 'wrong value'
                              dir_control.motor_dir(5)                        
                      elif sideDist > 15:
                              if dir_count > 2:
                                      print 'a'                                       
                                      #dir_count = dir_count  - 1
                                      #dir_control.motor_dir(dir_count)
                                      #dir_count = 5 
                                      #dir_control.motor_dir(dir_count)
                      elif sideDist < 8:
                              if dir_count < 9 :
                                      print 'b'
                                      #dir_count = dir_count + 1
                                      #dir_control.motor_dir(dir_count)
                                      #dir_count = 5 
                                      #dir_control.motor_dir(dir_count)
                      elif sideDist > 40:
                              motor.stop()
                      else :
                              print 'c'
                              #dir_count = 5;
                              #dir_control.motor_dir(dir_count)

                      #print 'Side Dist=' + str(sideDist) + " = " + str(dir_count)
                      print 'Side Dist = '  + str(int(sideDist))                      
                                                      
                      
              while True:
                      data = tcpCliSock.recv(BUFSIZ)    # Receive data sent from the client. 
                      # Analyze the command received and control the car accordingly.
                      if not data:
                              break
                      #--------Motor calibration----------
                      if data == 'motor_run':
                              print 'motor moving forward'
                              motor.setSpeed(50)
                              motor.motor0(forward0)
                              motor.motor1(forward1)
                      elif data[0:9] == 'leftmotor':
                              forward0 = data[9:]
                              motor.motor0(forward0)
                      elif data[0:10] == 'rightmotor':
                              forward1 = data[10:]
                              motor.motor1(forward1)

                      # -------------Added--------------
                      elif data == 'leftreverse':
                              if forward0 == "True":
                                      forward0 = "False"
                              else:
                                      forward0 = "True"
                              print "left motor reversed to", forward0
                              motor.motor0(forward0)
                      elif data == 'rightreverse':
                              if forward1 == "True":
                                      forward1 = "False"
                              else:
                                      forward1 = "True"
                              print "right motor reversed to", forward1
                              motor.motor1(forward1)
                      elif data == 'motor_stop':
                              print 'motor stop'
                              motor.stop()
                      #---------------------------------

                      #-------Turing calibration------
                      elif data[0:7] == 'offset=':
                              offset = int(data[7:])
                              car_dir.calibrate(offset)
                      #--------------------------------

                      #----------Mount calibration---------
                      elif data[0:8] == 'offsetx=':
                              offset_x = int(data[8:])
                              print 'Mount offset x', offset_x
                              video_dir.calibrate(offset_x, offset_y)
                      elif data[0:8] == 'offsety=':
                              offset_y = int(data[8:])
                              print 'Mount offset y', offset_y
                              video_dir.calibrate(offset_x, offset_y)
                      #----------------------------------------

                      #-------Turing calibration 2------
                      elif data[0:7] == 'offset+':
                              offset = offset + int(data[7:])
                              print 'Turning offset', offset
                              car_dir.calibrate(offset)
                      elif data[0:7] == 'offset-':
                              offset = offset - int(data[7:])
                              print 'Turning offset', offset
                              car_dir.calibrate(offset)
                      #--------------------------------

                      #----------Mount calibration 2---------
                      elif data[0:8] == 'offsetx+':
                              offset_x = offset_x + int(data[8:])
                              print 'Mount offset x', offset_x
                              video_dir.calibrate(offset_x, offset_y)
                      elif data[0:8] == 'offsetx-':
                              offset_x = offset_x - int(data[8:])
                              print 'Mount offset x', offset_x
                              video_dir.calibrate(offset_x, offset_y)
                      elif data[0:8] == 'offsety+':
                              offset_y = offset_y + int(data[8:])
                              print 'Mount offset y', offset_y
                              video_dir.calibrate(offset_x, offset_y)
                      elif data[0:8] == 'offsety-':
                              offset_y = offset_y - int(data[8:])
                              print 'Mount offset y', offset_y
                              video_dir.calibrate(offset_x, offset_y)
                      #----------------------------------------

                      #----------Confirm--------------------
                      elif data == 'confirm':
                              config = 'offset_x = %s\noffset_y = %s\noffset = %s\nforward0 = %s\nforward1 = %s\n ' % (offset_x, offset_y, offset, forward0, forward1)
                              print ''
                              print '*********************************'
                              print ' You are setting config file to:'
                              print '*********************************'
                              print config
                              print '*********************************'
                              print ''
                              fd = open('config', 'w')
                              fd.write(config)
                              fd.close()

                              motor.stop()
                              tcpCliSock.close()
                              quit()
                      else:
                              print 'Command Error! Cannot recognize command: ' + data

if __name__ == "__main__":
      try:
              setup()
              loop()
      except KeyboardInterrupt:
              tcpSerSock.close()

