import threading, socket, header, time, Queue, random

globalWindow = 5
randomPacketDropping = False

def main():
	host = "127.0.0.1"
	port = 5005

	recvSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	recvSock.bind((host, port))
	print "Starting receiver"
	r = threading.Thread(target = relReceiver, args= (host, port, recvSock, 1, 1, 10) )
	r.start()

def relReceiver(selfIP, selfPort, recvSocket, base, sequenceNumber, packetSize):
	global globalWindow

	setFirst = False
	expectedSeqNum = 0
	ackPacket = None

	while True:
		packet = recvSocket.recvfrom(1024)[0]
		packList = getPacket(packet)

		packetIsFirst = isFirst(packList)
		packetIsLast = isLast(packList)
		print "HERRO"
		print packetIsFirst

		if not isCorrupt(packet) and setFirst == False and packetIsFirst:
			setFirst = True
			expectedSeqNum = getPacketAttribute(packList, "seqNum")

		if setFirst and not isCorrupt(packet) and isExpectedSeqNum(packList, expectedSeqNum):

			print "hi"
			data = getPacketAttribute(packList, "payload")
			receivedSeqNum = getPacketAttribute(packList, "seqNum")
			addr = (getPacketAttribute(packList, "sourceIP"), getPacketAttribute(packList, "sourcePort"))
			print 
			deliverData(data)

			expectedSeqNum += 1
			ackPacket = makePacket(selfIP, selfPort, addr[0], addr[1], 0, expectedSeqNum, 10, 0, 1, 0, 0, 0, getReceiveWindow(), 100000, "xxx")
			recvSocket.sendto(ackPacket, addr)
			print "expectedSeqNum: %d" %(expectedSeqNum)
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
	for i in range(0, len(message)):
		out.append(message[i:i + size])
		i += size

	return out

def isCorrupt(packet):
	if (randomPacketDropping and random.random() > 0.8):
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

def makePacket(sourceIP, sourcePort, destIP, destPort, seqNum, ackNum, sizeOfPayload, SYN, ACK, FIN, LAST, FIRST, recvWindow, timeStamp, payload):
	return header.getPacket(sourceIP, sourcePort, destIP, destPort, seqNum, ackNum, sizeOfPayload, SYN, ACK, FIN, LAST, FIRST, recvWindow, timeStamp, payload)

def getPacket(packet):
	return header.decodePacket(packet)

def getPacketAttribute(packList, attribute):

	if (attribute == "sourceIP"):
		print packList[0]
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
	if (attribute == "FIRST"):
		return int(packList[11])
	if (attribute == "recvWindow"):
		return int(packList[12])
	if (attribute == "timeStamp"):
		return long(packList[13])
	if (attribute == "payload"):
		return packList[14]




if __name__=="__main__":
    main()