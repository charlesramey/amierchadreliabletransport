import socket, header



def main():
	toSend = header.getPacket('127.0.0.1', 50, '127.0.0.1', 5007, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, "I'm a hacker. You should drop this!")
	sendSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sendSock.bind(('127.0.0.1', 0))

	sendSock.sendto(toSend, ('127.0.0.1', 5007))
	print "ROGUE PACKET SENT!"
	sendSock.close()



if __name__=="__main__":
    main()