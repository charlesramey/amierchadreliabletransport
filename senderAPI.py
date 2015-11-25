import threading, socket, header, time, Queue, packet, hashlib, sys, connection, os

server_ip = '127.0.0.1'
server_port = 5007
self_ip = '127.0.0.1'
self_port = 6005
unrel_rcvr_stop = False

start_time = 0
calculatedTimeout = 0

# def main():
#     global start_time
#     send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     data = "TEST MESSAGE, THIS IS AN EXAMPLE OF DATA THAT CAN BE SENT AMONG OTHER THINGS THAT CAN BE SENT!!!!!"
#     data2 = "A wonderful fact to reflect upon, that every human creature is constituted to be that profound secret and mystery to every other. A solemn consideration, when I enter a great city by night, that every one of those darkly clustered houses encloses its own secret; that every room in every one of them encloses its own secret; that every beating heart in the hundreds of thousands of breasts there, is, in some of its imaginings, a secret to the heart nearest it! Something of the awfulness, even of Death itself, is referable to this. No more can I turn the leaves of this dear book that I loved, and vainly hope in time to read it all. No more can I look into the depths of this unfathomable water, wherein, as momentary lights glanced into it, I have had glimpses of buried treasure and other things submerged. It was appointed that the book should shut with a spring, for ever and for ever, when I had read but a page. It was appointed that the water should be locked in an eternal frost, when the light was playing on its surface, and I stood in ignorance on the shore. My friend is dead, my neighbour is dead, my love, the darling of my soul, is dead; it is the inexorable consolidation and perpetuation of the secret that was always in that individuality, and which I shall carry in mine to my life's end. In any of the burial-places of this city through which I pass, is there a sleeper more inscrutable than its busy inhabitants are, in their innermost personality, to me, or than I am to them?"
#     sapi = SenderAPI('127.0.0.1', 5007)
#     authenticated = False
#     while not authenticated:
#         authenticated = sapi.handshake(send_sock)
#     sapi.relSender(send_sock, data)
#     print "in between sends"
#     sapi.relSender(send_sock, data2)
#     print "hi"
#     sys.exit(0)
#     print "meeeehhhhh"

class SenderAPI:

    def __init__(self):
        self.ackQueue = Queue.Queue()
        self.start_time = 0
        self.unrel_rcvr_stop = False
        self.killThreads = False
        self.timeoutTime = 5
        self.ackReceiveRunning = False
        self.timeTracker = {}
        #self.recvThreadSock = None
        #self.recvThreadSockPort = 0



    def initRecvThreadSockPort(self, conn):
        self.recvThreadSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            self.recvThreadSock.bind((conn.ip, 0))
        except socket.error:
            pass
        self.recvThreadSockPort = self.recvThreadSock.getsockname()[1]


    def killReceiver(self, recvSock):
        self.killOther = True
        recvSock.setblocking(0)

    def unrelReceiver(self, sock, conn):
        global unrel_rcvr_stop

        self.ackReceiveRunning = True
        ackQueue = self.ackQueue
        sock.settimeout(1)
        print sock.getsockname()

        while True:
            try:
                data, addr = sock.recvfrom(1024)
                ackQueue.put(data)
                ###############UPDATE TIMEOUT HERE#######
                pack = packet.Packet()
                pack.createPacketFromString(data)
                self.updateTimeout(pack.ackNum)
                #########################################
            except:

                if (conn.killEverything):
                    print "KILLED SENDER SOCKET"
                    sock.close()
                    return
                continue


        print "unrelReceiver exiting"
     
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

    def updateTimeout(self, ackNum):

        if (ackNum in self.timeTracker):
            self.timeoutTime = min((.25 * ((time.time() - self.timeTracker[ackNum]) * 100) + .75 * self.timeoutTime), 4) + 1
            print "TIMEOUT TIME:"+str(self.timeoutTime) 
    
    def getReceiveWindow(self, conn):
        return conn.my_recvWindow
     
    def makePacket(self, sourceIP, sourcePort, destIP, destPort, seqNum, ackNum, sizeOfPayload, SYN, ACK, FIN, LAST, FIRST, recvWindow, timeStamp, payload):
        return header.getPacket(sourceIP, sourcePort, destIP, destPort, seqNum, ackNum, sizeOfPayload, SYN, ACK, FIN, LAST, FIRST, recvWindow, timeStamp, payload)

    def sendMessage(self, conn, message):
        
        peer_ip = conn.peer_ip
        peer_port = conn.peer_recvPort
        self_ip = conn.ip

        my_ip = conn.ip
        my_socket = conn.sendSocket
        my_port = conn.my_sendPort

        if (conn.netEmu):
            my_socket.sendto(message, (my_ip, conn.netEmuPort))
        else:
            my_socket.sendto(message, (peer_ip, peer_port))



    def handshake(self, conn):

        peer_ip = conn.peer_ip
        peer_port = conn.peer_recvPort
        self_ip = conn.ip

        my_ip = conn.ip
        my_socket = conn.sendSocket
        my_port = conn.my_sendPort

        rcvr = threading.Thread(target=self.unrelReceiver, args=(my_socket, conn))

        rcvr.daemon = True
        rcvr.start()
        ackQueue = self.ackQueue
        syn_flag = 1
        send_packet = self.makePacket(
            my_ip, my_port, peer_ip, peer_port, 0, 0, 0, syn_flag, 0,
            0, 0, 0, 5, conn.my_recvPort, '')
        syn_ack_rcvd = False
        challenge_resp = ''
        while not syn_ack_rcvd:
            self.sendMessage(conn, send_packet)
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

                        ###################################################
                        challengeInfo = header.unpackHandshakeInfo(pack.payload)
                        challenge = challengeInfo[0]
                        conn.peer_sendPort = int(challengeInfo[1])

                        recvSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        recvSocket.bind((my_ip , conn.peer_sendPort+1))
                        conn.my_recvPort = recvSocket.getsockname()[1]
                        conn.recvSocket = recvSocket
                        ###################################################

                        challenge_resp = hashlib.md5(challenge).hexdigest()
                        syn_ack_rcvd = True
                        break
        ack_rcvd = False
        attempts = 0
        while not ack_rcvd and attempts < 10:
            ack_flag = 1

            send_packet = self.makePacket(
                my_ip, my_port, peer_ip, peer_port, 0, 0, 0, 0, ack_flag,
                0, 0, 0, 5, conn.my_recvPort, challenge_resp)

            self.sendMessage(conn, send_packet)
            send_time = time.time()
            print "Sent challenge_resp"
            while int(send_time - time.time()) < 10:
                if not ackQueue.empty():
                    print "HERE"
                    rcvd_packet = ackQueue.get()
                    pack = packet.Packet()
                    pack.createPacketFromString(rcvd_packet)
                    conn.peer_recvWindow = pack.recvWindow
                    print "ACK packet", 
                    print pack.packlist
                    if pack.isACK():
                        ack_rcvd = True
                        print "Got ACK"
                        ##############################
                        conn.status = True
                        conn.printConnection()
                        return conn
                        ##############################
                        return True
                    else: 
                        attempts += 1
        return ack_rcvd

    def close(self, conn):

        peer_ip = conn.peer_ip
        peer_port = conn.peer_recvPort
        self_ip = conn.ip

        my_ip = conn.ip
        my_socket = conn.sendSocket
        my_port = conn.my_sendPort


        seq_num = 0
        send_socket = conn.sendSocket
        ackQueue = self.ackQueue
        conn.printConnection()
        fin_flag = 1
        send_packet = self.makePacket(
            my_ip, my_port, peer_ip, peer_port, seq_num, seq_num, 0, 0, 0,
            fin_flag, 0, 0, 5, 100000, '')
        #print "CLOSE"+str(server_port)
        print "CLOSE"+str(server_port)
        ack_rcvd = False
        tries = 0
        while not ack_rcvd and tries < 10:
            self.sendMessage(conn, send_packet)
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
            send_packet = self.makePacket(
                my_ip, my_port, server_ip, server_port, seq_num, seq_num, 0, 0, ack_flag,
                0, 0, 0, 5, 100000, '')
            self.sendMessage(conn, send_packet)
            #print "RETURN TRUE"
            print "BLERGH"

            conn.killEverything = True
            #conn.sendSocket.settimeout(1)
            #conn.recvSocket.settimeout(1)

            return True
            
        else:
            print "MEEHHHHHH"
            return False

    def relSender(self, conn, data):


        peer_ip = conn.peer_ip
        peer_port = conn.peer_recvPort
        self_ip = conn.ip

        my_ip = conn.ip
        my_socket = conn.sendSocket
        my_port = conn.my_sendPort


        ackQueue = self.ackQueue
        packetSize = 5
        flowWindow = 5 #conn.peer_recvWindow#
        #if (self.recvThreadSock == None):
        #    print "NOOOO"
        #    self.initRecvThreadSockPort(conn)
        #recvSocket = self.recvThreadSock
        selfIP = conn.ip
        #selfPort = self.recvThreadSockPort
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

        un_rel_rcvr = threading.Thread(target=self.unrelReceiver, args=(my_socket, conn))
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
                    my_ip, my_port, peer_ip, peer_port, packetNumber, packetNumber,
                    packetSize, 0, 0, 0, last_packet, firstsent, self.getReceiveWindow(conn), self.getCurrentTime(), dataList[packetNumber]
                    )

                self.sendMessage(conn, sendPacket)
                #####TIMEOUT STUFF########
                self.timeTracker[packetNumber] = time.time()
                ##########################
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
                        if packetNum + 1 == len(dataList):
                            last_packet = 1
                        if packetNum == 0:
                            firstsent = 1
                        sendPacket = self.makePacket(
                            my_ip, my_port, peer_ip, peer_port, packetNum,
                            packetNum, packetSize, 0, 0, 0, last_packet, firstsent, self.getReceiveWindow(conn),
                            self.getCurrentTime(), dataList[packetNum]
                            )
                        last_packet = 0
                        self.sendMessage(conn, sendPacket)
                        firstsent = 0
                    timerStart = time.time()
                    timer = True
                else:
                    if not ackQueue.empty():
                        ackPacket = ackQueue.get()
                        pack = packet.Packet()
                        pack.createPacketFromString(ackPacket)
                        if not pack.isCorrupt():
                            ackNum =  pack.ackNum
                            conn.peer_recvWindow = pack.recvWindow #max(pack.recvWindow/packetSize, 1)
                            base = ackNum + 1
                            
                            if ackNum in unAckedPackets:
                                if unAckedPackets.index(ackNum) == (len(unAckedPackets) - 1):
                                    unAckedPackets.remove(ackNum)
                                else:
                                    unAckedPackets = unAckedPackets[unAckedPackets.index(ackNum):]
                        if base >= nextSeqNumber and ackNum >= len(dataList):
                            timer = False
                            ackQueue.queue.clear()
                            self.recvThreadSock = None
                            if not self.recvThreadSock:
                                print "SET TO NONE"
                            continue
                        else:
                            print "restarting timer"
                            timer = True
                            timerStart = time.time()

if __name__=="__main__":
    main()