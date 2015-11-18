import threading, socket, header, time, Queue, random, packet, dataqueue

globalWindow = 5
randomPacketDropping = True

bufferSize = 5

def main():
	host = "127.0.0.1"
	port = 5005


	recvSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	recvSock.bind((host, port))
	print "Starting receiver"
	dq = dataqueue.DataQueue()

	r = threading.Thread(target = relReceiver, args= (host, port, recvSock, 1, 1, 10, dq) )
	r.start()

def relReceiver(selfIP, selfPort, recvSocket, base, sequenceNumber, packetSize, dataQueue):
	global globalWindow

	setFirst = False
	expectedSeqNum = 0
	ackPacket = None

	while True:
		pack = packet.Packet()
		pack.createPacketFromString(recvSocket.recvfrom(1024)[0])

		packetIsFirst = pack.isFirst()
		packetIsLast = pack.isLast()

		print packetIsFirst

		if not isCorrupt(packet) and setFirst == False and packetIsFirst:
			setFirst = True
			expectedSeqNum = pack.seqNum

		if setFirst and not isCorrupt(packet) and pack.isExpectedSeqNum(expectedSeqNum):

			print "hi"
			data = pack.payload
			receivedSeqNum = pack.seqNum
			addr = (pack.sourceIP, pack.sourcePort)

			deliverData(data)

			expectedSeqNum += 1
			ackPacket = makePacket(selfIP, selfPort, addr[0], addr[1], 0, expectedSeqNum, 10, 0, 1, 0, 0, 0, getReceiveWindow(), 100000, "xxx")
			recvSocket.sendto(ackPacket, addr)
			print "We got SEQ:"+str(expectedSeqNum)
			
		else:
			if (setFirst):
				recvSocket.sendto(ackPacket, addr)

def unrelReceiver(sock):
	global ackQueue
	data = sock.recv(1024)
	ackQueue.put(ackQueue)
	return 

def unrelSender():
	return

def messageSplit(message, size):

	out = []
	i = 0
	while (i < len(message)):
		out.append(message[i:i + size])
		i += size

	return out

def isCorrupt(packet):
	if (randomPacketDropping and random.random() > 0.9):
		return True
	return False

def isFirst(packList):
	return getPacketAttribute(packList, "FIRST") == 1

def isLast(packList):
	return getPacketAttribute(packList, "LAST") == 1

def isExpectedSeqNum(packetList, sequenceNumber):
	return (getPacketAttribute(packetList, "seqNum") == sequenceNumber)

def getReceiveWindow():
	return 10

def deliverData(data):
	print "RECEIVED:"+data
	#if (len(dataQueue) >)

def makePacket(sourceIP, sourcePort, destIP, destPort, seqNum, ackNum, sizeOfPayload, SYN, ACK, FIN, LAST, FIRST, recvWindow, timeStamp, payload):
	return header.getPacket(sourceIP, sourcePort, destIP, destPort, seqNum, ackNum, sizeOfPayload, SYN, ACK, FIN, LAST, FIRST, recvWindow, timeStamp, payload)

def getPacket(packet):
	return header.decodePacket(packet)




if __name__=="__main__":
    main()