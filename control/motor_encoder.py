#!/user/bin/env python
import RPi.GPIO as GPIO
import time

#pin configurations
GPIO.setmode(GPIO.BCM)

GPIO.setup(25,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(12,GPIO.IN,pull_up_down=GPIO.PUD_UP)

right_rotation = 0 
def right_motor_rotation(channel):
    global right_rotation
    right_rotation = right_rotation + 1
    print 'right_rotation = ' + str(right_rotation)
    if(right_rotation % 4 == 0 ):
        print '+1 rev ' 
        
    
left_rotation = 0 
def left_motor_rotation(channel):
    global left_rotation
    left_rotation = left_rotation + 1
    print 'left_rotation = ' + str(left_rotation)
    
print 'started'

#GPIO.add_event_detect(16, GPIO.FALLING ,callback=right_motor_rotation)
#GPIO.add_event_detect(12, GPIO.BOTH ,callback=left_motor_rotation)


try:
    #global rotation
    print 'waiting for event'

    
    
    while True:
        channel = GPIO.wait_for_edge(25,GPIO.BOTH)
        if channel is None :
            print 'time out'
        else:
            print 'edge detected!'
            right_rotation = right_rotation + 1
            print 'right_rotation = ' + str(right_rotation)
        rev = 1
        rev = rev + 1
        #prev_rotation = rotation
        #time.sleep(1)
        #print 'rotation:' + str(rotation) + '\t delta: ' + str(rotation - prev_rotation)
        #prev_rotation = rotation
        
    print 'rising event detection'
except KeyboardInterrupt:
    GPIO.cleanup()
GPIO.cleanup()
