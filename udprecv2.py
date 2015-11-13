import socket
import header


def main():

	host = '0.0.0.0'
	port = 50000

	serversocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	server_address = (host, port)
	serversocket.bind(server_address)

	while (True):
		print header.decodePacket(serversocket.recvfrom(100)[0])


if __name__ == "__main__":
	main()