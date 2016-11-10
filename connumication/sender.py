import socket
import sys

def main():
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        my_socket.bind(('',0))
        my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST,1)

        dest = ('<broadcast>',8881)
        while 1:
                data = raw_input('Enter data:')
                my_socket.sendto(data, dest)

        my_socket.close()
	
if __name__ == "__main__":
        main()
