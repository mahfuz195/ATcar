import time
import math

def thetaInc(prevDist, curDist , delT):
    deg = (math.degrees(math.atan((curDist-prevDist)/5.0)))
    print 'acutal deg = ' + str(deg)
    deg = int(((deg/90) * 5 ))
    print 'caluclated degree=' + str(abs(deg))
    return abs(deg)  
def calculateDir(prevDist , curDist, theta , desDist , dDist):
    if abs(curDist-prevDist) > 50 : 
	return curDist, theta
    turn = 0 
    if curDist > prevDist:
        turn = 1 
    elif curDist < prevDist:
        turn = -1
    else :
        print 'no change'
        return

    print 'turn:' + str(turn) + ', curDist=' + str(curDist) + ', desDist = ' + str(desDist) + ', maxDist:' + str(desDist+dDist)
    
    if( turn == 1): # going out
        if( curDist > desDist) and (curDist < (desDist+dDist)):
            print 'in line: OUT'
        elif (curDist < desDist):
            print 'keep going out'
        elif (curDist > (desDist+dDist)):
            print 'reduce theta'
	    prevTheta = theta
            theta = theta - thetaInc(curDist,prevDist,0) - 1
	    if theta > 0 : 
		theta = prevTheta
   
    elif (turn == -1):  #going in
        if( curDist > desDist) and (curDist < (desDist+dDist)):
            print 'in line: IN'
        elif (curDist < desDist):
            print 'increase theta'
            theta = theta + thetaInc(curDist,prevDist,0) + 1
	    if theta > 9 :
		theta = 9
        elif (curDist > (desDist+dDist)):
            print 'keep going in'

    return curDist, theta


if __name__ == '__main__':
    dDist = 10
    desDist = 30
    theta = 5
    prevDist = 30
    while True:
        curDist = input('Enter dist: ')
        #print('Hello', curDist)
        prevDist , theta = calculateDir(prevDist,curDist,theta,desDist,dDist)
        print 'Theta:' + str(theta)
