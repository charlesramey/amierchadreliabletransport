import reliableRecvrTest, reliableSenderTest





class RXP:


	def __init__(self):
		self.sendPort
		self.receivePort
		self.type = ""


	def establish_client(port):
		self.type = "client"


	def establish_server(port):
		self.type = "server"


	def connect(ip, port):
		if (self.type != "client"):
			print "This is not a client. Cannot connect."
			return

		if (not reliableSenderTest.handshake()):
			print "Could Not Connect. Exiting"
			return
			


	def send(message):

		reliableSenderTest.send


	def receive():


	
