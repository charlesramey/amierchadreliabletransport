import threading, socket, header, time, Queue, packet, hashlib, sys, connection

server_ip = '127.0.0.1'
server_port = 5007
self_ip = '127.0.0.1'
self_port = 6005
unrel_rcvr_stop = False

start_time = 0
calculatedTimeout = 0

def main():
    global start_time
    send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #unrel_rcv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data = "TEST MESSAGE, THIS IS AN EXAMPLE OF DATA THAT CAN BE SENT AMONG OTHER THINGS THAT CAN BE SENT!!!!!"
    data2 = "A wonderful fact to reflect upon, that every human creature is constituted to be that profound secret and mystery to every other. A solemn consideration, when I enter a great city by night, that every one of those darkly clustered houses encloses its own secret; that every room in every one of them encloses its own secret; that every beating heart in the hundreds of thousands of breasts there, is, in some of its imaginings, a secret to the heart nearest it! Something of the awfulness, even of Death itself, is referable to this. No more can I turn the leaves of this dear book that I loved, and vainly hope in time to read it all. No more can I look into the depths of this unfathomable water, wherein, as momentary lights glanced into it, I have had glimpses of buried treasure and other things submerged. It was appointed that the book should shut with a spring, for ever and for ever, when I had read but a page. It was appointed that the water should be locked in an eternal frost, when the light was playing on its surface, and I stood in ignorance on the shore. My friend is dead, my neighbour is dead, my love, the darling of my soul, is dead; it is the inexorable consolidation and perpetuation of the secret that was always in that individuality, and which I shall carry in mine to my life's end. In any of the burial-places of this city through which I pass, is there a sleeper more inscrutable than its busy inhabitants are, in their innermost personality, to me, or than I am to them?"
    sapi = SenderAPI('127.0.0.1', 5007)
    authenticated = False
    while not authenticated:
        authenticated = sapi.handshake(send_sock)
    sapi.relSender(send_sock, data)
    sapi.relSender(send_sock, data2)


class SenderAPI:

    def __init__(self):
        self.ackQueue = Queue.Queue()
        self.start_time = 0
        self.unrel_rcvr_stop = False
        self.killOther = False
        self.recvThreadSock = None
        self.recvThreadSockPort = 0


    def initRecvThreadSockPort(self, conn):
        self.recvThreadSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.recvThreadSock.bind((conn.ip, 0))
        self.recvThreadSockPort = self.recvThreadSock.getsockname()[1]


    def killReceiver(self, recvSock):
        self.killOther = True
        recvSock.setblocking(0)

    def unrelReceiver(self, sock, IP, PORT):
        global unrel_rcvr_stop
        ackQueue = self.ackQueue
        print sock.getsockname()
        try:
            sock.bind((IP, PORT))
        except socket.error:
            pass
        while True:
            data, addr = sock.recvfrom(1024)
            ackQueue.put(data)
     
    def messageSplit(self, message, size):
        out = []
        i = 0
        while(i < len(message)):
                out.append(message[i:i + size])
                i += size
        return out

    def getCurrentTime(self):
        global start_time
        return 0
        return int((time.time() - start_time) * 1000)

    def updateTimeout(self, inTime):
        global calculatedTimeout
        rtt = self.getCurrentTime() - inTime
        estimatedTimeout = (rtt * 100)/1000
        if (calculatedTimeout == 0):
            calculatedTimeout = rtt
        else:
            calculatedTimeout = .75 * calculatedTimeout + .25 * estimatedTimeout

    def getReceiveWindow(self):
        return 10
     
    def makePacket(self, sourceIP, sourcePort, destIP, destPort, seqNum, ackNum, sizeOfPayload, SYN, ACK, FIN, LAST, FIRST, recvWindow, timeStamp, payload):
        return header.getPacket(sourceIP, sourcePort, destIP, destPort, seqNum, ackNum, sizeOfPayload, SYN, ACK, FIN, LAST, FIRST, recvWindow, timeStamp, payload)

    def handshake(self, conn):

        self.initRecvThreadSockPort(conn)
        handshakeSocket = self.recvThreadSock

        server_ip = conn.peer_ip
        server_port = conn.peer_recvPort
        self_ip = conn.ip
        self_port = self.recvThreadSockPort
        send_socket = conn.sendSocket

        rcvr = threading.Thread(target=self.unrelReceiver, args=(handshakeSocket, conn.ip, self_port))
        rcvr.daemon = True
        rcvr.start()

        ackQueue = self.ackQueue
        syn_flag = 1
        send_packet = self.makePacket(
            self_ip, self_port, server_ip, server_port, 0, 0, 0, syn_flag, 0,
            0, 0, 0, 0, conn.my_recvPort, '')
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
                        ######
                        conn.peer_sendPort = pack.timeStamp
                        ######
                        break
        ack_rcvd = False
        attempts = 0
        while not ack_rcvd and attempts < 10:
            ack_flag = 1
            send_packet = self.makePacket(
                server_ip, self_port, server_ip, server_port, 0, 0, 0, 0, ack_flag,
                0, 0, 0, 0, conn.my_recvPort, challenge_resp)
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

                        ##############################
                        conn.peer_sendPort = pack.timeStamp
                        conn.status = True
                        conn.printConnection()
                        return conn
                        ##############################

                        return True
                    else: 
                        attempts += 1

        return ack_rcvd

    def close(self, conn):
        self_ip = conn.ip
        self_port = conn.my_sendPort
        server_ip = conn.peer_ip
        server_port = conn.peer_recvPort
        seq_num = 0
        send_socket = conn.sendSocket
        ackQueue = self.ackQueue
        conn.printConnection()
        un_rel_rcvr = threading.Thread(target=self.unrelReceiver, args=(self.recvThreadSock, self_ip, self_port))
        un_rel_rcvr.daemon = True
        un_rel_rcvr.start()
        fin_flag = 1
        send_packet = self.makePacket(
            self_ip, self_port, server_ip, server_port, seq_num, seq_num, 0, 0, 0,
            fin_flag, 0, 0, 0, 100000, '')
        ack_rcvd = False
        tries = 0
        while not ack_rcvd and tries < 10:
            send_socket.sendto(send_packet, (server_ip, server_port))
            send_time = time.time()
            print "Sent FIN"
            tries += 1
            while int(send_time - time.time()) < 3:
                print "waiting to receive fin ack"
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
            send_packet = self.makePacket(
                self_ip, self_port, server_ip, server_port, seq_num, seq_num, 0, 0, ack_flag,
                0, 0, 0, 0, 100000, '')
            send_socket.sendto(send_packet, (server_ip, server_port))
            print "RETURN TRUE"
            return True
        else: 
            return False

    def relSender(self, conn, data):
        timeTracker = {}
        sendSocket = conn.sendSocket
        peer_ip = conn.peer_ip
        peer_port = conn.peer_recvPort
        ackQueue = self.ackQueue
        packetSize = 5
        flowWindow = 5
        if (self.recvThreadSock == None):
            print "NOOOO"
            self.initRecvThreadSockPort(conn)
        recvSocket = self.recvThreadSock
        #recvSocket.bind(0)
        selfIP = conn.ip
        selfPort = self.recvThreadSockPort
        timer = False
        ackNum = -1
        sent = 0
        lastPrinted = -1
        last_packet = 0
        baseSeqNum = 0
        baseBase = 0
        nextSeqNumber = 0
        base = 0
        dataList = self.messageSplit(data, packetSize)
        un_rel_rcvr = threading.Thread(target=self.unrelReceiver, args=(recvSocket, selfIP, selfPort))
        un_rel_rcvr.daemon = True
        un_rel_rcvr.start()
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
                sendPacket = self.makePacket(
                    selfIP, selfPort, peer_ip, peer_port, packetNumber, packetNumber,
                    5, 0, 0, 0, last_packet, firstsent, self.getReceiveWindow(), self.getCurrentTime(), dataList[packetNumber]
                    )
                sendSocket.sendto(sendPacket, (peer_ip, peer_port))

                #timeTracker[packetNumber] = self.getCurrentTime()
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
                    lastPrinted = seconds
                if timer and int(currentTime-timerStart) > 5:
                    for packetNum in unAckedPackets:
                        print unAckedPackets
                        if packetNum + 1 == len(dataList):
                            #print "LAST PACKET"+str(dataList[packetNumber])
                            last_packet = 1
                        if packetNum == 0:
                            firstsent = 1
                        sendPacket = self.makePacket(
                            selfIP, selfPort, peer_ip, peer_port, packetNum,
                            packetNum, 5, 0, 0, 0, last_packet, firstsent, self.getReceiveWindow(),
                            self.getCurrentTime(), dataList[packetNum]
                            )
                        last_packet = 0
                        sendSocket.sendto(sendPacket, (peer_ip, peer_port))
                        #timeTracker[packetNumber] = self.getCurrentTime()
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
                        if not pack.isCorrupt():
                            #print "got ack! %d" %(pack.ackNum)
                            ackNum =  pack.ackNum
                            flowWindow = 5 #max(pack.recvWindow/packetSize, 1)
                            #print "FLOW WINDOW:"+str(flowWindow)
                            #print timeTracker[ackNum - 1]
                            #self.updateTimeout(timeTracker[ackNum - 1])
                            print "WE SHOULD UPDATE!"
                            base = ackNum + 1
                            print base
                            print len(dataList)
                            if ackNum in unAckedPackets:
                                if unAckedPackets.index(ackNum) == (len(unAckedPackets) - 1):
                                    unAckedPackets.remove(ackNum)
                                else:
                                    unAckedPackets = unAckedPackets[unAckedPackets.index(ackNum):]
                        if base >= nextSeqNumber and ackNum >= len(dataList):                            
                            timer = False
                            #ackQueue.queue.clear()
                            continue
                            send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                            exit = close(server_ip, server_port, nextSeqNumber, send_sock)
                            if exit:
                                print "exiting"
                        else:
                            print "restarting timer"
                            timer = True
                            timerStart = time.time()
                            #print ackNum
                            #print len(dataList)


 
 
 
if __name__=="__main__":
    main()