def main():
	print "Hello"
	x = convertIPToString("192.168.1.1")
	print x
	print convertIPToInt("192.168.1.1")
	print convertStringToInt(x)

	a = 2304
	s = convert16BitToString(a)
	print s

	print convertStringTo16Bit(s)
	#h = encodeHeader("192.168.1.1", 45,"192.168.1.2", 46, 18383847, 38382938, 920, 0, 0, 0, 1, 34, 3847392)

	packet = getPacket("0.0.0.0", 50000, "192.68.1.7", 50000, 837, 393, 90, 0, 0, 0, 1, 34, 3847392, "helloworld!!!!!!!!!how'sitgoing")
	packetX = getPacket("192.168.1.1", 45,"192.168.1.2", 46, 18383847, 38382928, 920, 0, 0, 0, 1, 34, 3847392, "helloworld!!!!!!!!!how.sitgoing")
	print packet
	print verifyCheckSum(packet, packetX)



def getPacket(sourceIP, sourcePort, destIP, destPort, seqNum, ackNum, sizeOfPayload, SYN, ACK, FIN, LAST, FIRST, recvWindow, timeStamp, payload):

	h = encodeHeader(sourceIP, sourcePort, destIP, destPort, seqNum, ackNum, sizeOfPayload, SYN, ACK, FIN, LAST, FIRST, recvWindow, timeStamp)
	checkSum = calculateCheckSum(h, payload)
	p = h+str(checkSum)+payload
	return p

def encodeHeader(sourceIP, sourcePort, destIP, destPort, seqNum, ackNum, sizeOfPayload, SYN, ACK, FIN, LAST, FIRST, recvWindow, timeStamp):
	
	header = convertIPToString(sourceIP)
	header += convert16BitToString(sourcePort)
	header += convertIPToString(destIP)
	header += convert16BitToString(destPort)

	header += convert32BitToString(seqNum)
	header += convert32BitToString(ackNum)
	header += packFlagsAndSize(sizeOfPayload, SYN, ACK, FIN, LAST, FIRST)

	header += convert16BitToString(recvWindow)
	header += convert32BitToString(timeStamp)

	return header


def decodePacket(packet):

	out = decodeHeader(packet[0:28])
	out.append(packet[31:])
	return out


def decodeHeader(string):

	sourceIP = convertIntToIP(convertStringToInt(string[0:4]))
	sourcePort = convertStringTo16Bit(string[4:6])
	destIP = convertIntToIP(convertStringToInt(string[6:10]))
	destPort = convertStringTo16Bit(string[10:12])
	seqNum = convertStringToInt(string[12:16])
	ackNum = convertStringToInt(string[16:20])

	flagsAndSize = unpackFlagsAndSize(string[20:22])

	sizeOfPayload = flagsAndSize[0]
	SYN = flagsAndSize[1]
	ACK = flagsAndSize[2]
	FIN = flagsAndSize[3]
	LAST = flagsAndSize[4]
	FIRST = flagsAndSize[5]

	recvWindow = convertStringTo16Bit(string[22:24])
	timeStamp = convertStringToInt(string[24:28])

	out = [sourceIP, sourcePort, destIP, destPort, seqNum, ackNum, sizeOfPayload, SYN, ACK, FIN, LAST, FIRST, recvWindow, timeStamp]
	return out

def verifyCheckSum(packetA, packetB):

	return (packetA[28:32] == packetB[28:32])


def convertIPToInt(ipAddress):

	if (not isValidIP(ipAddress)):
		return None
	splitString = ipAddress.split(".")
	out = (int(splitString[0]) << 24) | (int(splitString[1]) << 16) | (int(splitString[2]) << 8) | int(splitString[3])
	return out

def convertIPToString(ipAddress):

	if (not isValidIP(ipAddress)):
		return None

	splitString = ipAddress.split(".")

	b1 = int(splitString[0])
	b2 = int(splitString[1])
	b3 = int(splitString[2])
	b4 = int(splitString[3]) 
	out = chr(b1) + chr(b2) + chr(b3) + chr(b4)
	return out

def convertIntToIP(n):
	b1 = int(n >> 24)
	b2 = int((n >> 16) & 0xFF)
	b3 = int((n >> 8) & 0xFF)
	b4 = int(n & 0xFF)

	return str(b1)+"."+str(b2)+"."+str(b3)+"."+str(b4)


def convertStringToInt(string):
	out = (ord(string[0]) << 24) | (ord(string[1]) << 16) | (ord(string[2]) << 8) | ord(string[3])
	return out


def convert16BitToString(port):
	b1 = int((port >> 8) & 0xFF)
	b2 = int(port & 0xFF)

	out = chr(b1) + chr(b2)
	return out

def convertStringTo16Bit(string):
	out = (ord(string[0]) << 8) | ord(string[1])
	return out


def convert32BitToString(port):
	b1 = int(port >> 24)
	b2 = int((port >> 16) & 0xFF)
	b3 = int((port >> 8) & 0xFF)
	b4 = int(port & 0xFF)

	out = chr(b1) + chr(b2) + chr(b3) + chr(b4)
	return out

def convertStringTo32Bit(string):
	out = (ord(string[0]) << 8) | ord(string[1])
	return out

def packFlagsAndSize(sizeOfPayload, SYN, ACK, FIN, LAST, FIRST):

	num = sizeOfPayload << 6
	num |= SYN << 5
	num |= ACK << 4
	num |= FIN << 3
	num |= LAST << 2 
	num |= FIRST << 1

	return convert16BitToString(num)

def unpackFlagsAndSize(string):

	num = convertStringTo16Bit(string)

	sizeOfPayload = (num >> 6) & 0x3FF
	SYN = (num >> 5) & 1
	ACK = (num >> 4) & 1
	FIN = (num >> 3) & 1
	LAST = (num >> 2) & 1 
	FIRST = (num >> 1) & 1 

	return [sizeOfPayload, SYN, ACK, FIN, LAST, FIRST]

def isValidIP(ipAddress):
	return True


def convertIntToBinary():
	return False

def calculateCheckSum(a, b):

	sumA = 0
	sumB = 0

	for i in range(0, len(a)):
		sumA += ord(a[i])

	for i in range(0, len(b)):
		sumB += ord(b[i])

	return sumA ^ sumB


if __name__=="__main__":
    main()