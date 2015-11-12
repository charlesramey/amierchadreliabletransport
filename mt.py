import threading
import socket
import header
import time

recvWindow = 5

def main():

	host = "127.0.0.1"
	port = 5005

	recvSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	recvSock.bind((host, port))

	r = threading.Thread(target = relReceiver, args= (host, port, recvSock, 1, 1, 10) )
	r.start()

	#sendSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	#data = "TEST MESSAGE, THIS IS AN EXAMPLE OF DATA THAT CAN BE SENT"
	#s = threading.Thread(target = relSender, args= (sendSock, data, 1, 1, 10, 5) )
	#s.start()

	#print "yo"


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

		print packetIsFirst

		if not isCorrupt(packet) and setFirst == False and packetIsFirst:
			setFirst = True
			expectedSeqNum = getPacketAttribute(packList, "seqNum")

		if setFirst and not isCorrupt(packet) and isExpectedSeqNum(packList, expectedSeqNum):

			print "hi"
			data = getPacketAttribute(packList, "payload")
			receivedSeqNum = getPacketAttribute(packList, "seqNum")
			addr = (getPacketAttribute(packList, "sourceIP"), getPacketAttribute(packList, "sourcePort"))

			deliverData(data)

			expectedSeqNum += 1
			ackPacket = makePacket(selfIP, selfPort, addr[0], addr[1], 0, expectedSeqNum, 10, 0, 1, 0, 0, 0, getReceiveWindow(), 100000, "xxx")
			recvSocket.sendto(ackPacket, addr)

			print "We got SEQ:"+str(expectedSeqNum)
			
		else:
			recvSocket.sendto(ackPacket, addr)


def relSender(sendSocket, data, base, nextSeqNumber, packetSize, timeout):
	global globalWindow
	sent = 0
	while sent < len(data):
		if nextSeqNumber < (base + 5):
			sendSocket.sendto(data, ("127.0.0.1", 5005))
			if base == nextSeqNumber:
				return
				#//startTimer
			nextSeqNumber += 1

def unrelReceiver():
	return
	
def unrelSender():
	return


def isCorrupt(packet):
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