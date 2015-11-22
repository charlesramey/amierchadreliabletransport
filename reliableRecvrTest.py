import threading, socket, header, time, Queue, random, packet, dataqueue, hashlib, string
globalWindow = 5
randomPacketDropping = True
flowControlCongestion = True
bufferSize = 5
mq = None
dq = None
host = "127.0.0.1"
port = 5007

def main():
	global mq, dq, host, port


	recvSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	recvSock.bind((host, port))
	print "Starting receiver"

	dq = dataqueue.DataQueue()
	mq = dataqueue.MessageQueue()


	r = threading.Thread(target=bufferWorker, args=(host, port, recvSock, 0, 0, 10))
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

def handshake(self_ip, self_port, client_ip, client_port, rcvr):
	challenge = random_string()
	hashed_challenge = hashlib.md5(challenge).hexdigest()
	syn_flag = 1
	ack_flag = 1
	send_packet = makePacket(
        self_ip, self_port, client_ip, client_port, 0, 0, 0, syn_flag, ack_flag,
        0, 0, 0, 0, 100000, challenge)
	sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sender.sendto(send_packet, (client_ip, client_port))
	challenge_rcvd = False
	attempts = 0
	while not challenge_rcvd and attempts < 3:
		rcvr.settimeout(5)
		try:
			ack_pack, address = rcvr.recvfrom(1024)
			print "recieved package"
			pack = packet.Packet()
			pack.createPacketFromString(ack_pack)
			print pack.packlist
			if pack.isACK():
				print "PACKET WAS ACK"
				print pack.payload
				print hashed_challenge
				if pack.payload == hashed_challenge:
					#authenticate
					send_packet = makePacket(
        				self_ip, self_port, client_ip, client_port, 0, 0, 0, 0, ack_flag,
        				0, 0, 0, 0, 100000, challenge)
					sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
					sender.sendto(send_packet, (client_ip, client_port))
					challenge_rcvd = True
					print "AUTHENTICATED, YAY"
					break
		except socket.timeout:
			sender.sendto(send_packet, (client_ip, client_port))
			attempts += 1
			continue
	return challenge_rcvd

def random_string():
	#creates a random string 10 characters long from a character set containing
	#upper case ascii, lower case ascii, and digits
	return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))	

def relReceiver(selfIP, selfPort, recvSocket, base, sequenceNumber, packetSize):
	global globalWindow, sendUp, dq, mq, host, port
	setFirst = False
	expectedSeqNum = 0
	ackPacket = None
	addr = None
	authenticated_clients = []
	i = 0
	while True:
		pack = packet.Packet()
		packet_data, address = recvSocket.recvfrom(1024)
		pack.createPacketFromString(packet_data)
		source_ip = pack.sourceIP
		source_port = pack.sourcePort
		#add check for authentication

		if pack.isSYN():
			print "HERE, RECEIVED SYN"
			authenticated = handshake(selfIP, selfPort, source_ip, source_port, recvSocket)
			if authenticated:
				#do stuff to record that client is authenticated
				authenticated_clients.append((source_ip, source_port))
				recvSocket.close()
				recvSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
				recvSocket.bind((host, port))
				i = 0
			print "AUTHENTICATED"
			continue		
		print "HERRO"
		packetIsFirst = pack.isFirst()
		packetIsLast = pack.isLast()


		if isCorrupt(packet):
			print "CORRUPT"
			continue

		if setFirst == False and packetIsFirst:
			setFirst = True
			#expectedSeqNum = pack.seqNum

		if pack.isExpectedSeqNum(expectedSeqNum):
			data = pack.payload
			print "DATA: %s" %(data)
			receivedSeqNum = pack.seqNum
			addr = (pack.sourceIP, pack.sourcePort)

			if (packetIsLast):
				
				currentMessage += str(pushAllData())
				currentMessage += data
				mq.enqueue(currentMessage)
				currentMessage = ""
				setFirst = False

			else:

				currentMessage += str(pushDataRandomly())
				if (not deliverData(data)):
					continue

			expectedSeqNum += 1
			ackPacket = makePacket(selfIP, selfPort, addr[0], addr[1], 0, expectedSeqNum, 10, 0, 1, 0, 0, 0, getReceiveWindow(), 100000, "xxx")

			recvSocket.sendto(ackPacket, addr)

			#print "We got SEQ:"+ str(pack.seqNum)
		if not pack.isExpectedSeqNum(expectedSeqNum):
			print "INCORRECT SEQ NUMBER"
			print "Pack seq num: %s" %(str(pack.seqNum))
			print "exptd seq num: %d" %(expectedSeqNum)
			continue

		else:
			if (setFirst) and addr:
				recvSocket.sendto(ackPacket, addr)


sendUp = False

dqLock = threading.Lock()
mqLock = threading.Lock()




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
	global dq, dqLock
	#print "RECEIVED:"+data
	out = dq.enqueue(data)
	return out


def pushAllData():
	global dq
	out = ""
	while (len(dq.queue) > 0):
		x = dq.dequeue()

		if (x is not None):
			out += str(x)

	return out

def pushDataRandomly():
	global dq
	numPush = int(random.random() * 3)
	out = ""
	for i in range (0, numPush):
		x = dq.dequeue()

		if (x is not None):
			out += str(x)
	return out

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


def bufferWorker(selfIP, selfPort, recvSocket, base, sequenceNumber, packetSize):

	r = threading.Thread(target = relReceiver, args= (selfIP, selfPort, recvSocket, base, sequenceNumber, packetSize))
	r.start()

	global sendUp, dq, mq, dqLock

	currentMessage = ""
	while (True):

		#dqLock.acquire()
		#try:
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
		#finally:
		#	dqLock.release()

		if (flowControlCongestion and random.random() > 0.95):
			time.sleep(1)



if __name__=="__main__":
    main()