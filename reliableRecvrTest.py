import threading, socket, header, time, Queue, random, packet, dataqueue, hashlib, string, sys
globalWindow = 5
bufferSize = 5
mq = None
dq = None
host = "127.0.0.1"
port = 5007
randomPacketDropping = True
flowControlCongestion = False
synced = False

start_time = 0
calculatedTimeout = 5

def main():
	global mq, dq, host, port, start_time


	recvSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	recvSock.bind((host, port))
	print "Starting receiver"

	dq = dataqueue.DataQueue()
	mq = dataqueue.MessageQueue()

	start_time = time.time()
	r = threading.Thread(target=relReceiver, args=(host, port, recvSock, 0, 0, 10))
	r.start()
	print relRecv()
	print relRecv()
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

	out = mq.dequeue()
	return out



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

def close(self_ip, self_port, client_ip, client_port, rcvr):
	ack_flag = 1
	fin_flag = 1
	sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	send_packet = makePacket(
        self_ip, self_port, client_ip, client_port, 0, 0, 0, 0, ack_flag,
        fin_flag, 0, 0, 0, 100000, 'FIN ACK')
	sender.sendto(send_packet, (client_ip, client_port))
	ack_rcvd = False
	attempts = 0
	while not ack_rcvd and attempts < 10:
		rcvr.settimeout(5)
		try:
			ack_pack, address = rcvr.recvfrom(1024)
			print "recieved packet"
			pack = packet.Packet()
			pack.createPacketFromString(ack_pack)
			print pack.packlist
			if pack.isACK():
				print "IM DONE, YO!"
				send_packet = makePacket(
        			self_ip, self_port, client_ip, client_port, 0, 0, 0, 0, ack_flag,
        			0, 0, 0, 0, 100000, 'ACK')
				sender.sendto(send_packet, (client_ip, client_port))
				ack_rcvd = True
		except socket.timeout:
			sender.sendto(send_packet, (client_ip, client_port))
			attempts += 1
			continue
	print "returning"
	return ack_rcvd

def random_string():
	#creates a random string 10 characters long from a character set containing
	#upper case ascii, lower case ascii, and digits
	return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))	

def relReceiver(selfIP, selfPort, recvSocket, base, sequenceNumber, packetSize):
	global globalWindow, sendUp, dq, mq, host, port, synced
	setFirst = False
	expectedSeqNum = 0
	ackPacket = None
	addr = None
	currentMessage = ""
	authenticated_clients = []
	i = 0
	while True:
		#print "waiting"
		pack = packet.Packet()
		packet_data, address = recvSocket.recvfrom(1024)
		pack.createPacketFromString(packet_data)
		source_ip = pack.sourceIP
		source_port = pack.sourcePort
		#print packet_data
		#add check for authentication

		if (synced is False):
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
				synced = True
				continue

		if pack.isFIN():
			print "CLOSING HANDSHAKE"
			if pack.isExpectedSeqNum(expectedSeqNum):
				exit = close(selfIP, selfPort, source_ip, source_port, recvSocket)
				if exit:
					print "EXITING?"
					sys.exit()


		packetIsFirst = pack.isFirst()
		packetIsLast = pack.isLast()

		#print "TIMESTAMP: "+str(pack.timeStamp)
		#print "129"
		if pack.isCorrupt() or packetDrop():
			continue

		if setFirst == False and packetIsFirst:
			setFirst = True
			currentMessage = ""
			expectedSeqNum = pack.seqNum

		if pack.isExpectedSeqNum(expectedSeqNum):
			data = pack.payload
			#print "DATA: %s" %(data) 
			#print "SEQ: "+str(pack.seqNum)
			receivedSeqNum = pack.seqNum
			addr = (pack.sourceIP, pack.sourcePort)
			if (setFirst and packetIsLast):
				currentMessage += str(pushData(0))
				currentMessage += data
				mq.enqueue(currentMessage)
				currentMessage = ""
				setFirst = False
			else:
				currentMessage += str(pushData(0))
				if (not dataDeliverable()):
					continue
				deliverData(data)
			expectedSeqNum += 1
			if (packetDrop()):#simulates packets dropped on the way back
				continue

			ackPacket = makePacket(selfIP, selfPort, addr[0], addr[1], 0, expectedSeqNum, 10, 0, 1, 0, 0, 0, getReceiveWindow(), getCurrentTime(), "xxx")


			recvSocket.sendto(ackPacket, addr)
			#print "We got SEQ:"+ str(pack.seqNum)
		elif not pack.isExpectedSeqNum(expectedSeqNum):
			#print "170"
			print "INCORRECT SEQ NUMBER"
			print "Pack seq num: %s" %(str(pack.seqNum))
			print "exptd seq num: %d" %(expectedSeqNum)
			#recvSocket.sendto(ackPacket, addr)
			continue
		else:
			#print "177"
			if (setFirst) and addr:
				recvSocket.sendto(ackPacket, addr)

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

def packetDrop():
	if (randomPacketDropping and random.random() > 0.97):
		return True
	return False

def isExpectedSeqNum(packetList, sequenceNumber):
	return (getPacketAttribute(packetList, "seqNum") == sequenceNumber)

def getReceiveWindow():
	global dq
	return dq.getFreeSpace()


def dataDeliverable():
	global dq
	return (len(dq.queue) < 5)

def deliverData(data):
	global dq, dqLock
	out = dq.enqueue(data)
	return True

def pushData(randomly):

	if (randomly == 0):
		return pushAllData()
	else:
		return pushDataRandomly()

def pushAllData():
	global dq
	out = ""
	sizeOfQueue = len(dq.queue)

	for i in range(0, sizeOfQueue):
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

def getCurrentTime():
    global start_time
    return 0
    return int((time.time() - start_time) * 1000)

def makePacket(sourceIP, sourcePort, destIP, destPort, seqNum, ackNum, sizeOfPayload, SYN, ACK, FIN, LAST, FIRST, recvWindow, timeStamp, payload):
	return header.getPacket(sourceIP, sourcePort, destIP, destPort, seqNum, ackNum, sizeOfPayload, SYN, ACK, FIN, LAST, FIRST, recvWindow, timeStamp, payload)

def getPacket(packet):
	return header.decodePacket(packet)



if __name__=="__main__":
    main()