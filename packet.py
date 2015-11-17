import header

class Packet:

	def __init__(self):
		self.sourceIP = "0.0.0.0"
		self.sourcePort = -1
		self.destIP = "0.0.0.0"
		self.destPort = -1
		self.seqNum = -1
		self.ackNum = -1
		self.payloadSize = -1
		self.SYN = 0
		self.ACK = 0
		self.FIN = 0
		self.LAST = 0
		self.FIRST = 0
		self.recvWindow = 0
		self.timeStamp = 0
		self.checksum = 0
		self.payload = "."
		
	def setPacketValues(self, sip, sp, dip, dp, sn, an, sop, S, A, FI, L, FIR, rw, ts, pl):
		self.sourceIP = sip
		self.sourcePort = sp
		self.destIP = dip
		self.destPort = dp
		self.seqNum = sn
		self.ackNum = an
		self.payloadSize = sop
		self.SYN = S
		self.ACK = A
		self.FIN = FI
		self.LAST = L
		self.FIRST = FIR
		self.recvWindow = rw
		self.timeStamp = ts
		self.checksum = 0
		self.payload = pl

	def makePacket(self, sourceIP, sourcePort, destIP, destPort, seqNum, ackNum, sizeOfPayload, SYN, ACK, FIN, LAST, FIRST, recvWindow, timeStamp, payload):
		return header.getPacket(sourceIP, sourcePort, destIP, destPort, seqNum, ackNum, sizeOfPayload, SYN, ACK, FIN, LAST, FIRST, recvWindow, timeStamp, payload)

	def createPacketFromString(self):
		packList = header.decodePacket(packet)
		self.sourceIP = packList[0]
		self.sourcePort = packList[1]
		self.destIP = packList[2]
		self.destPort = packList[3]
		self.seqNum = packList[4]
		self.ackNum = packList[5]
		self.payloadSize = packList[6]
		self.SYN = packList[7]
		self.ACK = packList[8]
		self.FIN = packList[9]
		self.LAST = packList[10]
		self.FIRST = packList[11]
		self.recvWindow = packList[12]
		self.timeStamp = packList[13]
		self.payload = packList[14]

	def getPacketAttribute(self, packList, attribute):

		if (attribute == "sourceIP"):
			return packList[0]
		if (attribute == "sourcePort"):
			return int(packList[1])
		if (attribute == "destIP"):
			return packList[2]
		if (attribute == "destPort"):
			return int(packList[3])
		if (attribute == "seqNum"):
			return int(packList[4])
		if (attribute == "ackNum"):
			return int(packList[5])
		if (attribute == "sizeOfPayload"):
			return int(packList[6])
		if (attribute == "SYN"):
			return int(packList[7])
		if (attribute == "ACK"):
			return int(packList[8])
		if (attribute == "FIN"):
			return int(packList[9])
		if (attribute == "LAST"):
			return int(packList[10])
		if (attribute == "FIRST"):
			return int(packList[11])
		if (attribute == "recvWindow"):
			return int(packList[12])
		if (attribute == "timeStamp"):
			return long(packList[13])
		if (attribute == "payload"):
			return packList[14]