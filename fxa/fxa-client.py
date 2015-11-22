import socket, threading, fileHandler

commSock = None


def main():

	if (not verifyCommand):
		print "Invalid Input. Exiting"
		return

	host = '127.0.0.1'
	port = 56000

	global commSock
	setupClient(host, port)

	selfThread = threading.Thread(target = runSelfCommands)
	selfThread.start()


def runSelfCommands():

	global commSock

	while 1:
		cmd = raw_input("Next Command Request:")
		handleInput(cmd)

def handleInput(string):

	if (string == "disconnect"):
		print "Disconnecting"
		return

	if (string == "connect"):
		print "Connecting"
		return

	try:
		splitString = string.split(" ")

		cmd = splitString[0]
		arg = splitString[1]

		if (cmd == "get"):
			downloadFile(arg)
			return

		if (cmd == "post"):
			sendFile(arg)
			return
	except:
		print "ERROR."



def downloadFile(filename):

	print "Downloading File"
	global commSock

	rxpSend("get")

	gotRequest = rxpRecv()
	rxpSend(filename)

	packetExists = rxpRecv()

	if (packetExists == "bad"):
		print "Error Retrieving File!"
		sendBad()
		return

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

	#print out
	fileHandler.writeFile("clientFiles/"+filename, out)
	print "File Successfully Downloaded!"
	return out

def sendFile(fileName):


	print "Posting File"
	fileString = fileHandler.getFile("clientFiles/"+fileName)

	if (fileString is None):
		print "Could Not Load File. Exiting"
		return

	global commSock

	rxpSend("put")

	if (rxpRecv() == "bad"):
		print "Error On Receiving End."
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


	rxpSend(fileName)
	if (rxpRecv() == "bad"):
		return

	rxpSend(str(len(sendList)))
	if (rxpRecv() == "bad"):
		return
	for p in sendList:
		rxpSend(p)
		if (rxpRecv() == "bad"):
			return

	print "Successfully Posted File"

def runServer():
	return


def verifyCommand():
	return True

def setupClient(host, port):

	global commSock
	commSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	commSock.connect((host, port))


def setWindow():
	print "Setting Window Size"


def terminate():
	global commSock

	commSock.close()
	print "Terminated Connection. Exiting."

	sys.exit(0)


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