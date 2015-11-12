import socket
import sys
import header


def main():

	ipAddress = "0.0.0.0" #sys.argv[1]
	portNumber = 5005 #int(sys.argv[2])
	seqNum = int(sys.argv[1])
	message = header.getPacket("127.0.0.1", 50000, "192.68.1.7", 50000, seqNum, 393, 90, 0, 0, 0, 0, 1, 34, 3847392, "helloworld!!!!!!!!!how'sitgoing")

	print header.decodePacket(message)
	serversocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	serversocket.sendto(message, (ipAddress, portNumber))


if __name__ == "__main__":
	main()