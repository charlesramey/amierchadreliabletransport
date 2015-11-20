import threading, socket, header, time, Queue, packet
 
globalWindow = 5
ackQueue = Queue.Queue()
 
def main():
    sendSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data = "TEST MESSAGE, THIS IS AN EXAMPLE OF DATA THAT CAN BE SENT AMONG OTHER THINGS THAT CAN BE SENT!!!!!"
    data2 = "A wonderful fact to reflect upon, that every human creature is constituted to be that profound secret and mystery to every other. A solemn consideration, when I enter a great city by night, that every one of those darkly clustered houses encloses its own secret; that every room in every one of them encloses its own secret; that every beating heart in the hundreds of thousands of breasts there, is, in some of its imaginings, a secret to the heart nearest it! Something of the awfulness, even of Death itself, is referable to this. No more can I turn the leaves of this dear book that I loved, and vainly hope in time to read it all. No more can I look into the depths of this unfathomable water, wherein, as momentary lights glanced into it, I have had glimpses of buried treasure and other things submerged. It was appointed that the book should shut with a spring, for ever and for ever, when I had read but a page. It was appointed that the water should be locked in an eternal frost, when the light was playing on its surface, and I stood in ignorance on the shore. My friend is dead, my neighbour is dead, my love, the darling of my soul, is dead; it is the inexorable consolidation and perpetuation of the secret that was always in that individuality, and which I shall carry in mine to my life's end. In any of the burial-places of this city through which I pass, is there a sleeper more inscrutable than its busy inhabitants are, in their innermost personality, to me, or than I am to them?"
    s = threading.Thread(target = relSender, args= (sendSock, data2, 0, 0, 5, 5) )
    s.start()
 
def relSender(sendSocket, data, base, nextSeqNumber, packetSize, timeout):
    global globalWindow, ackQueue
    flowWindow = 5
    selfIP = '127.0.0.1'
    selfPort = 6050
    timer = False
    ackNum = -1
    sent = 0
    lastPrinted = -1
    baseSeqNum = nextSeqNumber
    baseBase = base
    recvSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    dataList = messageSplit(data, packetSize)
    t = threading.Thread(target=unrelReceiver, args=(recvSocket, selfIP, selfPort))
    t.start()
    firstsent = 1
    unAckedPackets = []
    while ackNum < len(dataList):
        if nextSeqNumber < (base + flowWindow) and sent < len(dataList):
            packetNumber = nextSeqNumber-baseSeqNum
            print "Sending: %s" %(dataList[packetNumber])
            if sent + 1 == len(dataList):
                last_packet = 1
                sendPacket = makePacket(
                    selfIP, selfPort, '127.0.0.1', 5005, packetNumber, packetNumber,
                    5, 0, 0, 0, last_packet, firstsent, getReceiveWindow(), 100000, dataList[packetNumber]
                    )
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
                        flowWindow = 5 #max(pack.recvWindow/packetSize, 1)
                        print "FLOW WINDOW:"+str(flowWindow)
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