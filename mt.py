import threading
import socket

recvWindow = 5

def main():
	recvSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	recvSock.bind(("127.0.0.1", 5005))
	r = threading.Thread(target = receiver, args= recvSock, 1, 1, 10)
	r.start()

	sendSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	data = "TEST MESSAGE, THIS IS AN EXAMPLE OF DATA THAT CAN BE SENT"
	s = threading.Thread(target = sender, args= sendSock, data, 1, 1, 10, 5)
	s.start()

	print "yo"


def relReceiver(recvSocket, base, sequenceNumber, packetSize):
	global globalWindow
	while True:
		packet, addr = recvSocket.recvfrom(1024)
		ackPacket = makePacket(0, ACK)
		if not isCorrupt(packet) and expectedSeqNum(packet, sequenceNumber):
			header, data = extractData(packet)
			deliverData(data)
			ackPacket = makePacket(sequenceNumber, ACK)
			//send ackPacket
			expectedSeqNum += 1
		else:
			//send ackPacket


def relSender(sendSocket, data, base, nextSeqNumber, packetSize, timeout):
	global globalWindow
	sent = 0
	while sent < len(data):
		if nextSeqNumber < (base + 5):
			sendSocket.sendto(data, ("127.0.0.1", 5005))
			if base == nextSeqNumber
				//startTimer
			nextSeqNumber += 1

def unrelReceiver():
	
def unrelSender():

def isCorrupt(packet):
	return False


def expectedSeqNum(packet, sequenceNumber):
	return True


if __name__=="__main__":
    main()