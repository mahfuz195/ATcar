import time
def calculateDir(prevDist , curDist, theta , desDist , dDist):
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
            theta = theta - 1
   
    elif (turn == -1):  #going in
        if( curDist > desDist) and (curDist < (desDist+dDist)):
            print 'in line: IN'
        elif (curDist < desDist):
            print 'increase theta'
            theta = theta + 1 
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
