import socket, threading, fileHandler, time, sys



serversocket = None
commSock = None


def main():

	if (not verifyCommand):
		print "Invalid Input. Exiting"
		return

	host = '127.0.0.1' #'0.0.0.0'
	port = 56000

	selfThread = threading.Thread(target = runSelfCommands)
	selfThread.start()

	connThread = threading.Thread(target = runServer, args =(host, port))
	connThread.start()


def runSelfCommands():

	print "Welcome to FXP Server."
	while 1:
		cmd = raw_input("Next Command Request:")

		if (cmd == "W"):
			setWindow()

		if (cmd == "terminate"):
			terminate()

def runServer(host, port):
	global commSock
	(clientsocket, address) = setupServer(host, port)
	commSock = clientsocket

	while 1:
		c = rxpRecv()

		if (c == "get"):
			sendFile()

		if (c == "put"):
			putFileHere()



#########################
#########################
#########################
#########################
#########################
#########################
#########################


def putFileHere():
	global commSock

	sendGood()
	filename = rxpRecv()
	sendGood()
	numPacks = int(rxpRecv())
	sendGood()

	out = ""
	i = 0

	while i < numPacks:
		c = rxpRecv()
		sendGood()
		out += str(c)
		i += 1
	fileHandler.writeFile("serverFiles/"+filename, out)

def sendFile():

	global commSock

	rxpSend("good")

	filedir = "serverFiles/"+rxpRecv()
	fileString = fileHandler.getFile(filedir)

	if (fileString is None):
		sendBad()
		return
	else:
		sendGood()

	if (rxpRecv() == "bad"):
		return

	sendList = []

	packSize = 1024
	filesize = len(fileString)
	toAdd = 0
	i = 0

	while i < filesize:
		toAdd = min(packSize, filesize - i)
		toSend = fileString[i : i + toAdd]
		sendList.append(toSend)
		i += toAdd

	rxpSend(str(len(sendList)))
	if (rxpRecv() == "bad"):
		return

	for p in sendList:
		rxpSend(p)
		if (rxpRecv() == "bad"):
			return


def verifyCommand():
	return True


def setWindow():
	print "Setting Window Size"


def terminate():
	global commSock

	try:
		commSock.close()
	except:
		print "Terminated Connection. Exiting."
		sys.exit(0)
	sys.exit(0)


def setupServer(host, port):

	global serversocket
	serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	serversocket.bind((host, port))
	serversocket.listen(5)
	return serversocket.accept()

def rxpRecv():
	global commSock
	return commSock.recv(1024)

def rxpSend(data):
	global commSock
	return commSock.send(data)

def sendGood():
	rxpSend("good")

def sendBad():
	rxpSend("bad")

if __name__=="__main__":
    main()