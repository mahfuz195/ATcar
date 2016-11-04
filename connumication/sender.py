import socket
import sys
def main():
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST,1)
        while 1:
                data = raw_input('Enter data:')
                my_socket.sendto(data, ('255.255.255.255' ,8881))

        my_socket.close()
	
if __name__ == "__main__":
        main()
