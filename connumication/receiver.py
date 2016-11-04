import socket

def receiver():
    try:
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        my_socket.bind(('',8881))

        print ('start service ...')

        while True :
            message , address = my_socket.recvfrom(8192)
            print 'message:'+ str(message) + ' from :', address[0]
            #print ('message from :'+ str(address[0]) , message)
    except:
        print 'exception in comm::receiver()'
                
if __name__ == "__main__" :
    receiver()
