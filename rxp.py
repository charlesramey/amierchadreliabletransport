
import receiverAPI, senderAPI, connection, sys, socket, threading, time, os


def main():
	print "Hello"
	x = int(sys.argv[1])
	if (x == 0):
		rxpObj = RXP()
		rxpObj.establish_server()
		rxpObj.listen("127.0.0.1", 5007)
		print rxpObj.receive()
		print rxpObj.receive()
		rxpObj.send("HOLY BOYS")
		print rxpObj.receive()
		
		time.sleep(5)
		print "lets have another go!"

		rxpObj = RXP()
		rxpObj.establish_server()
		rxpObj.listen("127.0.0.1", 5007)
		print rxpObj.receive()
		print rxpObj.receive()
		rxpObj.send("HOLY BOYS")
		print rxpObj.receive()
		sys.exit(0)

	else:
		rxpClient = RXP()
		rxpClient.establish_client()
		rxpClient.connect("127.0.0.1", 5007)
		rxpClient.send("WE DID IT BOYS!!!!!!!!! AYY LMAO")
		rxpClient.send("FUCK TO THE YEAH :D")
		print rxpClient.receive()
		rxpClient.send("FUCK TO THE YEAH AGAIN!")
		rxpClient.close()
		del rxpClient.sender
		del rxpClient

		return
		time.sleep(10)

		rxpClient = RXP()
		rxpClient.establish_client()
		rxpClient.connect("127.0.0.1", 5007)
		rxpClient.send("it is made by babies who've been captured")
		rxpClient.send("and welcome to this world, have as much fun as you'd like, while helping others have as much fun as your having")
		print rxpClient.receive()
		rxpClient.send("MEEEEEEEEEEEEEEEEEHHHHHHHHHHHHH")
		rxpClient.close()
		del rxpClient.sender
		del rxpClient
		print "herro"
		os._exit(0)


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
		except:
			print "Could Not Bind! Exiting."
			sys.exit(0)

		potentialConnection = connection.Connection()
		potentialConnection.ip = ip
		potentialConnection.my_recvPort = port
		potentialConnection.recvSocket = recvSock

		self.receiver = receiverAPI.ReceiverAPI()
		self.receiver.listen(recvSock, potentialConnection)

		if (potentialConnection.status == False):
			print "Listen Timed Out. Exiting."
			sys.exit(0)
		self.conn = potentialConnection
		self.conn.printConnection()
		r = threading.Thread(target=self.runReceiveThread)
		r.start()
		self.receiveThread = r
		self.sender = senderAPI.SenderAPI()

	def runReceiveThread(self):
		self.receiver.relReceiver(self.conn)

	def connect(self, ip, port):
		if (self.type != "client"):
			print "This is not a client. Cannot connect."
			sys.exit(0)
		try:
			sendSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			sendSock.bind(('0.0.0.0', port-1))
		except:
			print "Could Not Bind! Exiting."
			sys.exit(0)

		potentialConnection = connection.Connection()
		potentialConnection.ip = '127.0.0.1' ##THIS CAUSES PROBLEMS WHEN TRYING TO CONNECT TO LOCALHOST

		potentialConnection.my_sendPort = sendSock.getsockname()[1]
		potentialConnection.sendSocket = sendSock

		potentialConnection.peer_ip = ip
		potentialConnection.peer_recvPort = port

		self.sender = senderAPI.SenderAPI()
		self.conn = self.sender.handshake(potentialConnection)
		if (self.conn == None):
			print "Could Not Connect. Exiting"
			sys.exit(0)

		self.receiver = receiverAPI.ReceiverAPI()
		r = threading.Thread(target=self.runReceiveThread)
		r.start()

	def send(self, message):
		self.sender.relSender(self.conn, message)

	def receive(self):
		return self.receiver.relRecv()

	def close(self):
		self.sender.close(self.conn)




if __name__=="__main__":
    main()	
