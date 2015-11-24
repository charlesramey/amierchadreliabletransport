import threading, socket, header, time, Queue, packet, hashlib, sys 
globalWindow = 5
ackQueue = Queue.Queue()
server_ip = '127.0.0.1'
server_port = 5007
self_ip = '127.0.0.1'
self_port = 6005
unrel_rcvr_stop = False
start_time = 0
calculatedTimeout = 0

def main():
    global start_time, unrel_rcvr_stop, unrel_rcv
    send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    unrel_rcv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data = "TEST MESSAGE, THIS IS AN EXAMPLE OF DATA THAT CAN BE SENT AMONG OTHER THINGS THAT CAN BE SENT!!!!!"
    data2 = "A wonderful fact to reflect upon, that every human creature is constituted to be that profound secret and mystery to every other. A solemn consideration, when I enter a great city by night, that every one of those darkly clustered houses encloses its own secret; that every room in every one of them encloses its own secret; that every beating heart in the hundreds of thousands of breasts there, is, in some of its imaginings, a secret to the heart nearest it! Something of the awfulness, even of Death itself, is referable to this. No more can I turn the leaves of this dear book that I loved, and vainly hope in time to read it all. No more can I look into the depths of this unfathomable water, wherein, as momentary lights glanced into it, I have had glimpses of buried treasure and other things submerged. It was appointed that the book should shut with a spring, for ever and for ever, when I had read but a page. It was appointed that the water should be locked in an eternal frost, when the light was playing on its surface, and I stood in ignorance on the shore. My friend is dead, my neighbour is dead, my love, the darling of my soul, is dead; it is the inexorable consolidation and perpetuation of the secret that was always in that individuality, and which I shall carry in mine to my life's end. In any of the burial-places of this city through which I pass, is there a sleeper more inscrutable than its busy inhabitants are, in their innermost personality, to me, or than I am to them?"
    rcvr = threading.Thread(target=unrelReceiver, args=(unrel_rcv, '127.0.0.1', 6005))
    rcvr.daemon = True
    rcvr.start()
    authenticated = False
    while not authenticated:
        authenticated = handshake(server_ip, server_port, send_sock)
        time.sleep(1)
    relSender(send_sock, data2, 0, 0, 5, 5)
    relSender(send_sock, data, 0, 0, 5, 5)    
    sys.exit(0)


def handshake(server_ip, server_port, send_socket):
    global self_ip, self_port
    syn_flag = 1
    send_packet = makePacket(
        self_ip, self_port, server_ip, server_port, 0, 0, 0, syn_flag, 0,
        0, 0, 0, 0, 100000, '')
    syn_ack_rcvd = False
    challenge_resp = ''
    while not syn_ack_rcvd:
        send_socket.sendto(send_packet, (server_ip, server_port))
        send_time = time.time()
        #print "Sent SYN"
        while int(send_time - time.time()) < 5:
            if not ackQueue.empty():
                print "recved something"
                rcvd_packet = ackQueue.get()
                pack = packet.Packet()
                pack.createPacketFromString(rcvd_packet)
                print pack.packlist
                if pack.isSYNACK():
                    print "Got challenge"
                    challenge_resp = hashlib.md5(pack.payload).hexdigest()
                    syn_ack_rcvd = True
                    break
    ack_rcvd = False
    attempts = 0
    while not ack_rcvd and attempts < 10:
        ack_flag = 1
        send_packet = makePacket(
            server_ip, self_port, server_ip, server_port, 0, 0, 0, 0, ack_flag,
            0, 0, 0, 0, 100000, challenge_resp)
        send_socket.sendto(send_packet, (server_ip, server_port))
        send_time = time.time()
        print "Sent challenge_resp"
        while int(send_time - time.time()) < 10:
            if not ackQueue.empty():
                print "HERE"
                rcvd_packet = ackQueue.get()
                pack = packet.Packet()
                pack.createPacketFromString(rcvd_packet)
                print "ACK packet", 
                print pack.packlist
                if pack.isACK():
                    ack_rcvd = True
                    print "Got ACK"
                    return True
                else: 
                    attempts += 1
    #send_socket.sendto("CLOSEDOWNNPLZKTHXBYE", (self_ip, self_port))
    return ack_rcvd

def close(server_ip, server_port, seq_num, send_socket):
    global self_ip, self_port
    fin_flag = 1
    send_packet = makePacket(
        self_ip, self_port, server_ip, server_port, seq_num, seq_num, 0, 0, 0,
        fin_flag, 0, 0, 0, 100000, '')
    ack_rcvd = False
    tries = 0
    while not ack_rcvd and tries < 10:
        send_socket.sendto(send_packet, (server_ip, server_port))
        send_time = time.time()
        print "Sent FIN"
        tries += 1
        while int(send_time - time.time()) < 2:
            if not ackQueue.empty():
                print "recved something"
                rcvd_packet = ackQueue.get()
                pack = packet.Packet()
                pack.createPacketFromString(rcvd_packet)
                print pack.packlist
                if pack.isACK() and pack.isFIN():
                    print "Got FIN ACK"
                    ack_rcvd = True
                    seq_num += 1
                    break
    if ack_rcvd:
        ack_flag = 1
        send_packet = makePacket(
            self_ip, self_port, server_ip, server_port, seq_num, seq_num, 0, 0, ack_flag,
            0, 0, 0, 0, 100000, '')
        send_socket.sendto(send_packet, (server_ip, server_port))
        print "RETURN TRUE"
        return True
    else: 
        return False

def relSender(sendSocket, data, base, nextSeqNumber, packetSize, timeout):
    timeTracker = {}
    global globalWindow, ackQueue, server_ip, server_port, unrel_rcvr_stop
    unrel_rcvr_stop = False
    flowWindow = 5
    selfIP = '127.0.0.1'
    selfPort = 6050
    timer = False
    ackNum = -1
    sent = 0
    lastPrinted = -1
    last_packet = 0
    baseSeqNum = nextSeqNumber
    baseBase = base
    recvSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    dataList = messageSplit(data, packetSize)

    firstsent = 1
    unAckedPackets = []
    while ackNum < len(dataList):
        if nextSeqNumber < (base + flowWindow) and sent < len(dataList):
            packetNumber = nextSeqNumber-baseSeqNum
            #print "Sending: %s" %(dataList[packetNumber])
            #print "SEQ NUM: %s" %(packetNumber)
            if sent + 1 == len(dataList):
                #print "LAST PACKET"+str(dataList[packetNumber])
                last_packet = 1
            sendPacket = makePacket(
                selfIP, selfPort, '127.0.0.1', 5007, packetNumber, packetNumber,
                5, 0, 0, 0, last_packet, firstsent, getReceiveWindow(), getCurrentTime(), dataList[packetNumber]
                )
            sendSocket.sendto(sendPacket, ("127.0.0.1", 5007))

            timeTracker[packetNumber] = getCurrentTime()
            #print "TIME TRACKER:"+str(timeTracker[packetNumber])
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
                #print seconds
                lastPrinted = seconds
            if timer and int(currentTime-timerStart) > 5:
                #print "Timer timed out"
                for packetNum in unAckedPackets:
                    #print "RE_Sending seqNum = %d" %(packetNum)
                    #print "RE-Sending: %s" %(dataList[packetNum])
                    if packetNum == 0:
                        firstsent = 1

                    if packetNum + 1 == len(dataList):
                        #print "LAST PACKET"+str(dataList[packetNumber])
                        last_packet = 1
                    sendPacket = makePacket(
                        selfIP, selfPort, server_ip, server_port, packetNum,
                        packetNum, 5, 0, 0, 0, last_packet, firstsent, getReceiveWindow(),
                        getCurrentTime(), dataList[packetNum]
                        )

                    firstsent = 0
                    last_packet = 0
                    sendSocket.sendto(sendPacket, ('127.0.0.1', 5007))
                    timeTracker[packetNumber] = getCurrentTime()
                    firstsent = 0
                #after resend, restart unrelReceiver and timer
                #print "TIMER RESTARTED AFTER RESEND"
                timerStart = time.time()
                timer = True
            else:
                if not ackQueue.empty():
                    ackPacket = ackQueue.get()
                    pack = packet.Packet()
                    pack.createPacketFromString(ackPacket)
                    if not isCorrupt(ackPacket):
                        #print "got ack! %d" %(pack.ackNum)
                        ackNum =  pack.ackNum
                        flowWindow = 5 #max(pack.recvWindow/packetSize, 1)
                        #print "FLOW WINDOW:"+str(flowWindow)
                        #print timeTracker[ackNum - 1]
                        updateTimeout(timeTracker[ackNum - 1])


                        base = ackNum + 1
                        if ackNum in unAckedPackets:
                            if unAckedPackets.index(ackNum) == (len(unAckedPackets) - 1):
                                unAckedPackets.remove(ackNum)
                            else:
                                unAckedPackets = unAckedPackets[unAckedPackets.index(ackNum):]
                        #print "base = %d" %(base)
                        #print "nextSeqNumber: %d" %(nextSeqNumber)
                    if base >= nextSeqNumber and ackNum >= len(dataList):
                        #print "ACK base == nextSeqNumber, timer stoping"
                        continue
                        timer = False
                        ackQueue.queue.clear()
                        send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        exit = close(server_ip, server_port, nextSeqNumber, send_sock)
                        print "attempting to kill unrel_rcv"
                        unrel_rcvr_stop = True
                        time.sleep(1)
                        print "killed!?"
                        if exit:
                            print "exiting"
                    else:
                        print "restarting timer"
                        timer = True
                        timerStart = time.time()
                        #print ackNum
                        #print len(dataList)

def unrelReceiver(sock, IP, PORT):
    global ackQueue
    try:
        sock.bind((IP, PORT))
    except socket.error:
        pass
    while True:
        data, addr = sock.recvfrom(1024)
        ackQueue.put(data)
    print "unrelReceiver exiting"
    sock.close()
    sys.exit()
 
def messageSplit(message, size):
    out = []
    i = 0
    while(i < len(message)):
            out.append(message[i:i + size])
            i += size
    return out

def getCurrentTime():
    global start_time
    return 0
    return int((time.time() - start_time) * 1000)

def updateTimeout(inTime):
    global calculatedTimeout
    #print inTime 
    rtt = getCurrentTime() - inTime
    estimatedTimeout = (rtt * 100)/1000
    
    if (calculatedTimeout == 0):
        calculatedTimeout = rtt
    else:
        calculatedTimeout = .75 * calculatedTimeout + .25 * estimatedTimeout

    #print calculatedTimeout

 
def isCorrupt(packet):
    return False
 
def getReceiveWindow():
    return 10
 
def deliverData(data):
    print "RECEIVED:"+data
 
def makePacket(sourceIP, sourcePort, destIP, destPort, seqNum, ackNum, sizeOfPayload, SYN, ACK, FIN, LAST, FIRST, recvWindow, timeStamp, payload):
    return header.getPacket(sourceIP, sourcePort, destIP, destPort, seqNum, ackNum, sizeOfPayload, SYN, ACK, FIN, LAST, FIRST, recvWindow, timeStamp, payload)
 
def getPacket(packet):
    return header.decodePacket(packet)
 
 
 
 
if __name__=="__main__":
    main()