import socket
import sys
import time

def main():
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        my_socket.bind(('',0))
        my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST,1)
        count = 0 
        dest = ('<broadcast>',8881)
        while 1:
                #data = raw_input('Enter data:')
                data = 'hello' + str(count)
                my_socket.sendto(data, dest)
                time.sleep(.1)
                count = count + 1 

        my_socket.close()
	
if __name__ == "__main__":
        main()
