import threading, socket, header, time, Queue, random, packet, dataqueue

globalWindow = 5
randomPacketDropping = False
flowControlCongestion = False
bufferSize = 5
mq = None
dq = None

def main():
	global mq, dq

	host = "127.0.0.1"
	port = 5005
	recvSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	recvSock.bind((host, port))
	print "Starting receiver"

	dq = dataqueue.DataQueue()
	mq = dataqueue.MessageQueue()

	r = threading.Thread(target = bufferWorker, args= (host, port, recvSock, 1, 1, 10))
	r.start()

	print relRecv()
	#print relRecv()
	#print relRecv()

	#print relRecv()
	#print relRecv()
	#print relRecv()
	#print relRecv()

def relRecv():
	global mq
	i = 0
	while(mq.getSize() == 0):
		i = 0

	return mq.dequeue()


def relReceiver(selfIP, selfPort, recvSocket, base, sequenceNumber, packetSize):
	global globalWindow, sendUp, dq, mq
	setFirst = False
	expectedSeqNum = 0
	ackPacket = None
	addr = None


	while True:
		pack = packet.Packet()
		pack.createPacketFromString(recvSocket.recvfrom(1024)[0])

		packetIsFirst = pack.isFirst()
		packetIsLast = pack.isLast()


		if isCorrupt(packet):
			continue

		if setFirst == False and packetIsFirst:
			setFirst = True
			#expectedSeqNum = pack.seqNum

		if pack.isExpectedSeqNum(expectedSeqNum):
			data = pack.payload
			receivedSeqNum = pack.seqNum
			addr = (pack.sourceIP, pack.sourcePort)

			if (packetIsLast):
				
				if (not deliverData(data)):
					continue

				sendUp = True
				setFirst = False
			else:
				if (not deliverData(data)):
					continue

			expectedSeqNum += 1
			ackPacket = makePacket(selfIP, selfPort, addr[0], addr[1], 0, expectedSeqNum, 10, 0, 1, 0, 0, 0, getReceiveWindow(), 100000, "xxx")

			recvSocket.sendto(ackPacket, addr)
			#print "We got SEQ:"+ str(pack.seqNum)
		if not pack.isExpectedSeqNum(expectedSeqNum):
			continue
			print "We got SEQ:"+ str(pack.seqNum)
		#if not pack.isExpectedSeqNum(expectedSeqNum):

			#print "Expected SeqNum: %d" %(expectedSeqNum)
			#print "Got SeqNum: %d" %(pack.seqNum)
		else:
			if (setFirst) and addr:
				recvSocket.sendto(ackPacket, addr)


sendUp = False

def bufferWorker(selfIP, selfPort, recvSocket, base, sequenceNumber, packetSize):

	r = threading.Thread(target = relReceiver, args= (selfIP, selfPort, recvSocket, base, sequenceNumber, packetSize))
	r.start()

	global sendUp, dq, mq

	currentMessage = ""
	while (True):
		x = dq.dequeue()
		if (x is not None):
			currentMessage += str(x)

		if (sendUp):
			x = dq.dequeue()
			if (x is not None):
				currentMessage += str(x)

			mq.enqueue(currentMessage)
			currentMessage = ""
			sendUp = False

		if (flowControlCongestion and random.random() > 0.95):
			time.sleep(1)



def unrelReceiver(sock):
	global ackQueue
	data = sock.recv(1024)
	ackQueue.put(data)
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
	if (randomPacketDropping and random.random() > 0.97):
		return True
	return False

def isExpectedSeqNum(packetList, sequenceNumber):
	return (getPacketAttribute(packetList, "seqNum") == sequenceNumber)

def getReceiveWindow():
	global dq
	return dq.getFreeSpace()

def deliverData(data):
	global dq
	#print "RECEIVED:"+data
	return dq.enqueue(data)
	
	#if (len(dataQueue) >)

def makePacket(sourceIP, sourcePort, destIP, destPort, seqNum, ackNum, sizeOfPayload, SYN, ACK, FIN, LAST, FIRST, recvWindow, timeStamp, payload):
	return header.getPacket(sourceIP, sourcePort, destIP, destPort, seqNum, ackNum, sizeOfPayload, SYN, ACK, FIN, LAST, FIRST, recvWindow, timeStamp, payload)

def getPacket(packet):
	return header.decodePacket(packet)


def relReceiverOld(selfIP, selfPort, recvSocket, base, sequenceNumber, packetSize):
	global globalWindow
	setFirst = False
	expectedSeqNum = 0
	ackPacket = None
	addr = None

	while True:
		pack = packet.Packet()
		pack.createPacketFromString(recvSocket.recvfrom(1024)[0])
		packetIsFirst = pack.isFirst()
		packetIsLast = pack.isLast()

		if (isCorrupt(packet)):
			continue

		if setFirst == False and packetIsFirst:
			setFirst = True
			expectedSeqNum = pack.seqNum
		if setFirst and pack.isExpectedSeqNum(expectedSeqNum):
			data = pack.payload
			receivedSeqNum = pack.seqNum
			addr = (pack.sourceIP, pack.sourcePort)
			deliverData(data)
			expectedSeqNum += 1
			ackPacket = makePacket(selfIP, selfPort, addr[0], addr[1], 0, expectedSeqNum, 10, 0, 1, 0, 0, 0, getReceiveWindow(), 100000, "xxx")

			recvSocket.sendto(ackPacket, addr)
			#print "We got SEQ:"+ str(pack.seqNum)

		if not pack.isExpectedSeqNum(expectedSeqNum):
			continue
			#print "Expected SeqNum: %d" %(expectedSeqNum)
			#print "Got SeqNum: %d" %(pack.seqNum)
		else:
			if (setFirst) and addr:
				recvSocket.sendto(ackPacket, addr)


if __name__=="__main__":
    main()