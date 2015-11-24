class Connection:

	def __init__(self):
		self.ip = "127.0.0.1"
		self.my_sendPort = 0
		self.my_recvPort = 0
		self.sendSocket = None
		self.recvSocket = None

		self.peer_ip = "0.0.0.0"
		self.peer_sendPort = 0
		self.peer_recvPort = 0

		self.my_recvWindow = 5
		self.peer_recvWindow = 5
		self.status = False


	def printConnection(self):
		print "Connection Info:"
		print "MY IP:"+str(self.ip)
		print "MY SENDING PORT:"+str(self.my_sendPort)
		print "MY RECEIVING PORT:"+str(self.my_recvPort)

		print "MY PEER IP:"+str(self.peer_ip)
		print "MY PEER RECEIVING PORT:"+str(self.peer_recvPort)
		print "MY PEER SENDING PORT:"+str(self.peer_sendPort)

		print "MY SENDING RECEIVING WINDOW: "+str(self.my_recvWindow)
		print "MY PEER SENDING RECEIVING WINDOW: "+str(self.peer_recvWindow)
		print "CONNECTION STATUS: "+str(self.status)