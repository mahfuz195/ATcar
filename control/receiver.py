import socket
import re

def ParseVehicleData(data):
    if data.find('$') != -1 and data.find('#') != -1:
        #vid , dtime , speed , angle , headway = data.split(' $#,')
        vid , dtime , speed , angle , headway = filter(None,re.split("[,\-!$#]",data))
        print 'vid=' + str(vid) + ' time=' + str(dtime) + ' speed' + str(speed)
        #print 'time='
        
def receiver():
    try:
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        my_socket.bind(('',8881))

        print ('start service ...')
        
        while True :
            message , address = my_socket.recvfrom(8192)
            ParseVehicleData
            print 'message:'+ str(message) + ' from :', address[0]
            
    except:
        print 'exception in comm::receiver()'
                
if __name__ == "__main__" :
    receiver()
    #data = "$1,20.3,24,90,61.2#"
    #ParseVehicleData(data)
