import socket
import sys
import header


def main():

	ipAddress = "0.0.0.0" #sys.argv[1]
	portNumber = 5005 #int(sys.argv[2])
	message = header.getPacket("0.0.0.0", 50000, "192.68.1.7", 50000, 837, 393, 90, 0, 0, 0, 1, 34, 3847392, "helloworld!!!!!!!!!how'sitgoing")


	serversocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	serversocket.sendto(message, (ipAddress, portNumber))


if __name__ == "__main__":
	main()