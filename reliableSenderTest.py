import threading, socket, header, time, Queue, packet
 
globalWindow = 5
ackQueue = Queue.Queue()
 
def main():
        sendSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        data = "TEST MESSAGE, THIS IS AN EXAMPLE OF DATA THAT CAN BE SENT"
        s = threading.Thread(target = relSender, args= (sendSock, data, 0, 0, 10, 5) )
        s.start()
 
def relSender(sendSocket, data, base, nextSeqNumber, packetSize, timeout):
        global globalWindow, ackQueue
        selfIP = '127.0.0.1'
        selfPort = 6050
        timer = False
        ackNum = -1
        sent = 0
        lastPrinted = -1
        baseSeqNum = nextSeqNumber
        baseBase = base
        recvSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        dataList = messageSplit(data, 5)
        print dataList
        t = threading.Thread(target=unrelReceiver, args=(recvSocket, selfIP, selfPort))
        t.start()
        firstsent = 1
        unAckedPackets = []
        while ackNum < len(dataList):
                if nextSeqNumber < (base + 5) and sent < len(dataList):
                        packetNumber = nextSeqNumber-baseSeqNum
                        print "Sending: %s" %(dataList[packetNumber])
                        sendPacket = makePacket(
                                        selfIP, selfPort, '127.0.0.1', 5005, packetNumber, packetNumber,
                                        5, 0, 0, 0, 0, firstsent, getReceiveWindow(), 100000, dataList[packetNumber]
                                )
                        sendSocket.sendto(sendPacket, ("127.0.0.1", 5005))
                        unAckedPackets.append(packetNumber)
                        firstsent = 0
                        sent += 1
                        if base == nextSeqNumber:
                                #startTimer
                                timerStart = time.time()
                                timer = True
                                print "base == nextSeqNumber, timer started"
                        nextSeqNumber += 1
               
                else:
                        currentTime = time.time()
                        seconds = int(currentTime-timerStart)
                        if seconds != lastPrinted:
                            print seconds
                            lastPrinted = seconds
                        if timer and int(currentTime-timerStart) > 5:
                                print "Timer timed out"
                                for packetNum in unAckedPackets:
                                        print "RE_Sending seqNum = %d" %(packetNum)
                                        print "RE-Sending: %s" %(dataList[packetNum])
                                        sendPacket = makePacket(
                                                        selfIP, selfPort, '127.0.0.1', 5005, packetNum,
                                                        packetNum, 5, 0, 0, 0, 0, firstsent, getReceiveWindow(),
                                                        100000, dataList[packetNum]
                                                )
                                        sendSocket.sendto(sendPacket, ('127.0.0.1', 5005))
                                        firstsent = 0
                                #after resend, restart unrelReceiver and timer
                                print "TIMER RESTARTED AFTER RESEND"
                                timerStart = time.time()
                                timer = True
                        else:
                                if not ackQueue.empty():

                                        ackPacket = ackQueue.get()
                                        pack = packet.Packet()
                                        pack.createPacketFromString(ackPacket)

                                        if not isCorrupt(ackPacket):
                                                print "got ack! %d" %(pack.ackNum)
                                                ackNum =  pack.ackNum
                                                base = ackNum + 1
                                                if ackNum in unAckedPackets:
                                                    if unAckedPackets.index(ackNum) == (len(unAckedPackets) - 1):
                                                        unAckedPackets.remove(ackNum)
                                                    else:
                                                        unAckedPackets = unAckedPackets[unAckedPackets.index(ackNum):]
                                                print "base = %d" %(base)
                                                print "nextSeqNumber: %d" %(nextSeqNumber)
                                        if base == nextSeqNumber and ackNum >= len(dataList):
                                                print "ACK base == nextSeqNumber, timer stoping"
                                                timer = False
                                        else:
                                                print "restarting timer"
                                                timer = True
                                                timerStart = time.time()
 
def unrelReceiver(sock, IP, PORT):
        global ackQueue
        sock.bind((IP, PORT))
        while True:
                data, addr = sock.recvfrom(1024)
                ackQueue.put(data)
 
def unrelSender():
        return
 
def messageSplit(message, size):
 
        out = []
        i = 0
        while(i < len(message)):
                out.append(message[i:i + size])
                i += size
 
        return out
 
def isCorrupt(packet):
        return False
 
def isFirst(packList):
        return getPacketAttribute(packList, "FIRST") == 1
 
def isLast(packList):
        return getPacketAttribute(packList, "LAST") == 1
 
def isExpectedSeqNum(packetList, sequenceNumber):
        return (getPacketAttribute(packetList, "seqNum") == sequenceNumber)
 
def getReceiveWindow():
        return 10
 
def deliverData(data):
        print "RECEIVED:"+data
 
def makePacket(sourceIP, sourcePort, destIP, destPort, seqNum, ackNum, sizeOfPayload, SYN, ACK, FIN, LAST, FIRST, recvWindow, timeStamp, payload):
        return header.getPacket(sourceIP, sourcePort, destIP, destPort, seqNum, ackNum, sizeOfPayload, SYN, ACK, FIN, LAST, FIRST, recvWindow, timeStamp, payload)
 
def getPacket(packet):
        return header.decodePacket(packet)
 
def getPacketAttribute(packList, attribute):
 
        if (attribute == "sourceIP"):
                print packList[0]
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
 
 
 
 
if __name__=="__main__":
    main()