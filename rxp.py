import receiverAPI, senderAPI, connection, sys, socket, threading


def main():
	print "Hello"

	x = int(sys.argv[1])

	if (x == 0):
		rxpObj = RXP()
		rxpObj.establish_server()
		rxpObj.listen("127.0.0.1", 5007)
		print rxpObj.receive()
		print rxpObj.receive()

	else:
		rxpClient = RXP()
		rxpClient.establish_client()
		rxpClient.connect("127.0.0.1", 5007)
		rxpClient.send("WE DID IT BOYS!!!!!!!!! AYY LMAO")
		rxpClient.send("FUCK TO THE YEAH :D")
		rxpClient.close()



class RXP:


	def __init__(self):
		self.type = None
		self.conn = None

		self.receiver = None
		self.sender = None

		self.receiveThread = None


	def establish_client(self):

		if (self.type != None):
			return
		self.type = "client"


	def establish_server(self):

		if (self.type != None):
			return

		self.type = "server"


	def listen(self, ip, port):

		if (self.type != "server"):
			print "This is not a client. Cannot connect."
			return

		try:
			recvSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			recvSock.bind((ip, port))

			self.sendSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			self.sendSock.bind((ip, 0))
		except:
			print "Could Not Bind! Exiting."
			sys.exit(0)


		self.receiver = receiverAPI.ReceiverAPI(ip, port)

		self.conn = self.receiver.listen(recvSock)
		if (self.conn == None):
			print "Listen Timed Out. Exiting."
			sys.exit(0)

		self.conn.printConnection()

		r = threading.Thread(target=self.runReceiveThread)
		r.start()
		self.receiveThread = r

		#self.sender = senderAPI.SenderAPI(ip, port)


		#self.recvSock = other[2]
		#self.partner = [other[0], other[1]]

	def runReceiveThread(self):
		self.receiver.relReceiver(self.conn)


	def connect(self, ip, port):
		if (self.type != "client"):
			print "This is not a client. Cannot connect."
			sys.exit(0)

		try:
			sendSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			sendSock.bind(('0.0.0.0', 0))

			recvSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			recvSock.bind(('0.0.0.0', 0))
		except:
			print "Could Not Bind! Exiting."
			sys.exit(0)


		self.sender = senderAPI.SenderAPI(ip, port)
		self.conn = self.sender.handshake(sendSock)

		if (self.conn == None):
			print "Could Not Connect. Exiting"
			sys.exit(0)

	def send(self, message):

		self.sender.relSender(self.conn, message)

	def receive(self):
		return self.receiver.relRecv()

	def close(self):
		self.sender.close(self.conn)


if __name__=="__main__":
    main()	
