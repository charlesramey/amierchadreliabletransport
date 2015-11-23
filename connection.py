class Connection:

	def __init__(self):
		self.ip = "127.0.0.1"
		self.my_sendPort = 0
		self.my_recvPort = 0

		self.peer_ip = "0.0.0.0"
		self.peer_sendPort = 0
		self.peer_recvPort = 0

		self.my_recvWindow = 5
		self.peer_recvWindow = 5
		self.status = False

