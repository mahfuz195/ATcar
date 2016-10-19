import time
import numpy as np
Kp = .27
Ki = .05
Kd = .01
prev_error = 0
Hd = 3.0 # desired headway
currentTime = 0
prevTime = 0
ival = 0
pval = 0
dval = 0

def InitPid():
    currentTime = time.time()
    prevTime = currentTime
    prev_error = 0
def bound(output):
    return 0
def update(value):
    global prevTime , Hd , Kp , Kd , Ki , prev_error , ival , pval , dval
    error = Hd - value              #merror
    currentTime = time.time()       #get t  
    dt = currentTime - prevTime     #get delta t
    de = error - prev_error         #get delta error 

    pval = Kp * error               #proportional term
    ival = ival + error * dt        #integral term

    dval = 0
    if dt > 0:
        dval = de/dt                #derivative term

    prevTime = currentTime
    prev_error = error

    #debug
    print error , pval ,  ival , dval   
    updated = pval + (Ki * ival) + (Kd * dval)  
    return updated

if __name__ == '__main__':
    InitPid()
    for i in range(100):
        value = input('Enter updated value:')
        val  =  update(value)
        print val
