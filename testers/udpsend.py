import socket
import sys


def main():

	ipAddress = sys.argv[1]
	portNumber = int(sys.argv[2])
	message = sys.argv[3]


	serversocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	serversocket.sendto(message, (ipAddress, portNumber))


if __name__ == "__main__":
	main()