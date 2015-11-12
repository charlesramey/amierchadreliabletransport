import threading, socket, header, time, Queue

recvWindow = 5
ackQueue = Queue.Queue()

def main():
	recvSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	recvSock.bind(("127.0.0.1", 5005))
	r = threading.Thread(target = relReceiver, args= (recvSock, 1, 1, 10) )
	r.start()

	#sendSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	#data = "TEST MESSAGE, THIS IS AN EXAMPLE OF DATA THAT CAN BE SENT"
	#s = threading.Thread(target = relSender, args= (sendSock, data, 1, 1, 10, 5) )
	#s.start()

	#print "yo"


def relReceiver(recvSocket, base, sequenceNumber, packetSize):
	global globalWindow

	while True:
		packet, addr = recvSocket.recvfrom(1024)
		ackPacket = ackPacket = makePacket("127.0.0.1", 5005, addr[0], addr[1], 0, 0, 0, 0, 1, 0, 0, getReceiveWindow(), 100000, "xxx")

		if not isCorrupt(packet) and isExpectedSeqNum(packet, sequenceNumber):

			packList = getPacket(packet)
			data = getPacketAttribute(packList, "payload")
			receivedSeqNum = getPacketAttribute(packList, "seqNum")
			addr = (addr[0], getPacketAttribute(packList, "sourcePort"))

			deliverData(data)

			expectedSeqNum = receivedSeqNum + 1

			ackPacket = makePacket("127.0.0.1", 5005, addr[0], addr[1], 0, expectedSeqNum, 10, 0, 1, 0, 0, getReceiveWindow(), 100000, "xxx")
			recvSocket.sendto(ackPacket, addr)

			print "We got SEQ:"+str(expectedSeqNum)
			
		else:
			recvSocket.sendto(ackPacket, addr)


def relSender(sendSocket, data, base, nextSeqNumber, packetSize, timeout):
	global globalWindow, ackQueue
	timer = False
	sent = 0
	while sent < len(data):
		if nextSeqNumber < (base + 5):
			sendSocket.sendto(data, ("127.0.0.1", 5005))
			if base == nextSeqNumber:
				#startTimer
				t = threading.Thread(target=unrelReceiver)
				t.start()
				timerStart = time.time()
				timer = True
			nextSeqNumber += 1
		
		else:
			currentTime = time.time()
			if timer and int(currentTime-timerStart) > 5:
				#resend
				sendSocket.sendto(data, ('127.0.0.1', 5005))
				#after resend, restart unrelReceiver and timer
				t = threading.Thread(target=unrelReceiver)
				t.start()
				timerStart = time.time()
			else:
				ackPacket = recvData
				if not isCorrupt(ackPacket):
					base = getAckNumber(ackPacket)+1
				if base == nextSeqNumber:
					timer = False
				else:
					timer = True
					timerStart = time.time()

def unrelReceiver(time):
	global ackQueue
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.bind('127.0.0.1', 6005)
	data = sock.recv(1024)
	ackQueue.put(ackQueue)
	
def unrelSender():
	return


def isCorrupt(packet):
	return False


def isExpectedSeqNum(packet, sequenceNumber):
	return True

def getReceiveWindow():
	return 10

def deliverData(data):
	print "RECEIVED:"+data

def makePacket(sourceIP, sourcePort, destIP, destPort, seqNum, ackNum, sizeOfPayload, SYN, ACK, FIN, LAST, recvWindow, timeStamp, payload):
	return header.getPacket(sourceIP, sourcePort, destIP, destPort, seqNum, ackNum, sizeOfPayload, SYN, ACK, FIN, LAST, recvWindow, timeStamp, payload)

def getPacket(packet):
	return header.decodePacket(packet)

def getPacketAttribute(packList, attribute):

	if (attribute == "sourceIP"):
		return packList[0]
	if (attribute == "sourcePort"):
		return int(packList[1])
	if (attribute == "destIP"):
		return packList[2]
	if (attribute == "destPort"):
		return int(packList[3])
	if (attribute == "seqNum"):
		return int(packList[4])
	if (attribute == "ackNum"):
		return int(packList[5])
	if (attribute == "sizeOfPayload"):
		return int(packList[6])
	if (attribute == "SYN"):
		return int(packList[7])
	if (attribute == "ACK"):
		return int(packList[8])
	if (attribute == "FIN"):
		return int(packList[9])
	if (attribute == "LAST"):
		return int(packList[10])
	if (attribute == "recvWindow"):
		return int(packList[11])
	if (attribute == "timeStamp"):
		return long(packList[12])
	if (attribute == "payload"):
		return packList[13]




if __name__=="__main__":
    main()