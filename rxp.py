import receiverAPI, senderAPI, connection


def main():
	print "Hello"



class RXP:


	def __init__(self):
		self.recvSock = None
		self.sendSock = None
		
		self.conn = None
		self.partner = []


	def establish_client(port):
		self.type = "client"


	def establish_server(port):
		self.type = "server"


	def listen(ip, port):
		if (self.type != "client"):
			print "This is not a client. Cannot connect."
			return


		try:
			self.recvSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			self.recvSock.bind((host, port))

			self.sendSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			self.sendSock.bind(0)
		except:
			print "Could Not Bind! Exiting."
			sys.exit(0)

		other = receiverAPI.listen(ip, port, recvSock)
		self.recvSock = other[2]
		self.partner = [other[0], other[1]]



	def connect(ip, port):
		if (self.type != "client"):
			print "This is not a client. Cannot connect."
			sys.exit(0)

		try:
			self.sendSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			self.sendSock.bind(0)

			self.recvSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			self.recvSock.bind(0)
		except:
			print "Could Not Bind! Exiting."
			sys.exit(0)


		if (not senderAPI.handshake(ip, port, sendSock)):
			print "Could Not Connect. Exiting"
			sys.exit(0)

		self.partner = [ip, port]

			


	def send(message):

		senderAPI.send()


	def receive():

		return receiverAPI.relRecv()


	
