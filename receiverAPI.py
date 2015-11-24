import threading, socket, header, time, Queue, random, packet, dataqueue, hashlib, string, sys, connection


def main():
	print "TEST"
	# global mq, dq, host, port, start_time

	rapi = ReceiverAPI("127.0.0.1", 5007)

	recvSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	recvSock.bind((host, port))

	r = threading.Thread(target=startReceiveThread, args=(rapi, recvSock))
	r.start()

	#print "LEGGO"
	print rapi.relRecv()
	print rapi.relRecv()

	# print "Starting receiver"

	# dq = dataqueue.DataQueue()
	# mq = dataqueue.MessageQueue()

	# start_time = time.time()
	# r = threading.Thread(target=relReceiver, args=(host, port, recvSock, 0, 0, 10))
	# r.start()
	# print relRecv()
	# print relRecv()

def startReceiveThread(rapi, recvSock):
	out = rapi.listen(recvSock)
	out.printConnection()
	rapi.relReceiver(out)

class ReceiverAPI:

	def __init__(self):
		self.dq = dataqueue.DataQueue()
		self.mq = dataqueue.MessageQueue()
		self.randomPacketDropping = False
		self.randomWindowChange = True
		self.start_time = 0
		self.conn = None

	def listen(self, recvSocket, conn):
		selfIP = conn.ip
		selfPort = conn.my_recvPort
		print "Waiting on SYN"
		while True:
		
			pack = packet.Packet()
			packet_data, address = recvSocket.recvfrom(1024)
			pack.createPacketFromString(packet_data)
			source_ip = pack.sourceIP
			source_port = pack.sourcePort


			#print packet_data
			#add check for authentication


			if pack.isSYN():
				print "HERE, RECEIVED SYN"
				authenticated = self.handshake(selfIP, selfPort, source_ip, source_port, recvSocket, conn)
				if authenticated:
					#do stuff to record that client is authenticated

					recvSocket.close()
					recvSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
					recvSocket.bind((selfIP, selfPort))

					print "AUTHENTICATED"

					##############################
					conn.peer_ip = source_ip
					conn.peer_sendPort = address[1]
					conn.recvSocket = recvSocket

					conn.status = True
					##############################

					return conn
				else:
					return None
				continue

	def handshake(self, self_ip, self_port, client_ip, client_port, rcvr, conn):
		challenge = self.random_string()
		hashed_challenge = hashlib.md5(challenge).hexdigest()
		syn_flag = 1
		ack_flag = 1
		send_packet = self.makePacket(
	        self_ip, self_port, client_ip, client_port, 0, 0, 0, syn_flag, ack_flag,
	        0, 0, 0, 5, conn.my_sendPort , challenge)


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

					conn.peer_recvPort = pack.timeStamp


					if pack.payload == hashed_challenge:
						#authenticate
						send_packet = self.makePacket(
	        				self_ip, self_port, client_ip, client_port, 0, 0, 0, 0, ack_flag,
	        				0, 0, 0, 5, conn.my_sendPort, challenge)

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



	def packetDrop(self):
		if (self.randomPacketDropping and random.random() > 0.95):
			return True
		return False

	def windowChange(self, conn):

		if (self.randomWindowChange and random.random() > 0.1):
			conn.my_recvWindow = int(random.random() * 10) + 1
			#print "YUH"
			#print conn.my_recvWindow

	def filterPacket(self, pack, conn):
		return False


	def relRecv(self):
		mq = self.mq

		i = 0
		while(mq.getSize() == 0):
			i = 0

		out = mq.dequeue()
		return out

	def pushData(self, randomly):

		if (randomly == 0):
			return self.pushAllData(self.dq)
		else:
			return self.pushDataRandomly(self.dq)

	def pushAllData(self, dq):
		out = ""
		sizeOfQueue = len(dq.queue)

		for i in range(0, sizeOfQueue):
			x = dq.dequeue()

			if (x is not None):
				out += str(x)

		return out

	def pushDataRandomly(self, dq):
		numPush = int(random.random() * 3)
		out = ""
		for i in range (0, numPush):
			x = dq.dequeue()

			if (x is not None):
				out += str(x)
		return out

	def getReceiveWindow(self, conn):
		return conn.my_recvWindow


	def dataDeliverable(self):
		dq = self.dq
		return (len(dq.queue) < 5)

	def deliverData(self, data):
		dq = self.dq
		out = dq.enqueue(data)
		return True


	def getCurrentTime(self):
	    start_time = self.start_time
	    return 0
	    return int((time.time() - start_time) * 1000)

	def makePacket(self, sourceIP, sourcePort, destIP, destPort, seqNum, ackNum, sizeOfPayload, SYN, ACK, FIN, LAST, FIRST, recvWindow, timeStamp, payload):
		return header.getPacket(sourceIP, sourcePort, destIP, destPort, seqNum, ackNum, sizeOfPayload, SYN, ACK, FIN, LAST, FIRST, recvWindow, timeStamp, payload)

	def getPacket(self, packet):
		return header.decodePacket(packet)


	def close(self, self_ip, self_port, client_ip, client_port, rcvr):
		ack_flag = 1
		fin_flag = 1
		sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		send_packet = self.makePacket(
	        self_ip, self_port, client_ip, client_port, 0, 0, 0, 0, ack_flag,
	        fin_flag, 0, 0, 5, 100000, 'FIN ACK')
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
					send_packet = self.makePacket(
	        			self_ip, self_port, client_ip, client_port, 0, 0, 0, 0, ack_flag,
	        			0, 0, 0, 5, 100000, 'ACK')
					sender.sendto(send_packet, (client_ip, client_port))
					ack_rcvd = True
			except socket.timeout:
				sender.sendto(send_packet, (client_ip, client_port))
				attempts += 1
				continue
		print "returning"
		return ack_rcvd

	def random_string(self):
		#creates a random string 10 characters long from a character set containing
		#upper case ascii, lower case ascii, and digits
		return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))	

	def relReceiver(self, conn):

		self.start_time = time.time()
		dq = self.dq
		mq = self.mq
		selfIP = conn.ip
		selfPort = conn.my_recvPort
		recvSocket = conn.recvSocket



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
			conn.peer_recvWindow = pack.recvWindow
			#print packet_data
			#add check for authentication

			self.windowChange(conn)

			if pack.isFIN():
				print "CLOSING HANDSHAKE"
				expectedSeqNum = 0
				if pack.isExpectedSeqNum(expectedSeqNum):
					exit = self.close(selfIP, selfPort, source_ip, source_port, recvSocket)
					if exit:
						print "EXITING?"
						sys.exit()


			packetIsFirst = pack.isFirst()
			packetIsLast = pack.isLast()

			#print "GOT DATA: %s" %(pack.payload) 
			#print "SEQ: "+str(pack.seqNum)
			#print "TIMESTAMP: "+str(pack.timeStamp)
			#print "129"
			if pack.isCorrupt() or self.filterPacket(pack, conn) or self.packetDrop():
				continue

			addr = (pack.sourceIP, pack.sourcePort)

			if setFirst == False and packetIsFirst:
				setFirst = True
				currentMessage = ""
				expectedSeqNum = pack.seqNum

			if pack.isExpectedSeqNum(expectedSeqNum):
				data = pack.payload

				#print "DATA: %s" %(data) 
				#print "SEQ: "+str(pack.seqNum)
				receivedSeqNum = pack.seqNum
				

				if (setFirst and packetIsLast):
					pushedData = self.pushData(0)
					currentMessage += str(pushedData)
					currentMessage += data

					mq.enqueue(currentMessage)
					currentMessage = ""
					#expectedSeqNum = 0
					setFirst = False
				else:
					pushedData = self.pushData(0)
					currentMessage += str(pushedData)
					if (not self.dataDeliverable()):
						continue
					self.deliverData(data)
				expectedSeqNum += 1
				if (self.packetDrop()):#simulates packets dropped on the way back
					continue

				ackPacket = self.makePacket(selfIP, selfPort, addr[0], addr[1], 0, expectedSeqNum, 10, 0, 1, 0, 0, 0, self.getReceiveWindow(conn), self.getCurrentTime(), "xxx")
				recvSocket.sendto(ackPacket, addr)
				#print "We got SEQ:"+ str(pack.seqNum)
			elif not pack.isExpectedSeqNum(expectedSeqNum):
				#print "170"
				print "INCORRECT SEQ NUMBER"
				print "Pack seq num: %s" %(str(pack.seqNum))
				print "exptd seq num: %d" %(expectedSeqNum)

				if (ackPacket == None):
					continue	
				recvSocket.sendto(ackPacket, addr)
			else:
				#print "177"
				if (setFirst) and addr:
					recvSocket.sendto(ackPacket, addr)






if __name__=="__main__":
    main()