#! /usr/bin/env python
#
#NetEmu - network emulator
#
# Based on code by Flavio Castro
# Updated for CS 3251, Spring 2015

#
from random import randint
import Queue,thread,time
import socket,sys,signal
import optparse
import binascii
from copy import copy
from optparse import Option, OptionValueError
#import numpy as np

PSINT=0.5

def signal_handler(signal, frame):
    print "Shutting down the emulator."
    sys.exit(0)

def Main():   
    sock.setblocking(0)
    try:
        thread.start_new_thread(ReceivePacket,())
        thread.start_new_thread(ProcessQueue,())
    except:
        print "Error"
    while 1:
        pass

def ReceivePacket():
    while 1:
        try:
            packet = sock.recvfrom(65535)
            data=packet[0]
            if not data: break

            print "Packet received from:", packet[1]

            if (randint(1,100) < corruptProb): 
                print "Corrupting this packet"
                packet=(corrupt(packet[0]),packet[1])  # corrupt
            elif (randint(1,100) < dupProb): 
                print "Duplicating this packet"
                queue.put(packet) # duplicate by adding twice to queue
            if (randint(1,100) < dropProb):
                print "Dropping this packet"
            else: 
                queue.put(packet)
        except socket.error,msg:
            continue

# Randomly munge the data. We shouldn't be treating it as a string but then,
# the whole point is to corrupt it so this will work fine.
def corrupt(data):
    list=split(data,8)
    data=""
    for i in xrange(0,len(list)):
        data=data+list[i][:-1]+"0"
    return data

# This thread runs continually, pulling packets off the queue and sending
# them. This is horribly inefficient as a busy wait loop but it works
# for this demonstration.
def ProcessQueue():
    while 1:
        while not queue.empty():
            packet=queue.get()
            if (randint(1,100) < reorderProb): # put it back in the queue to reorder
	        print "Reordering this packet"
                queue.put(packet)
                break
            PSINT=randint(0,delay)/1000.0
            if (PSINT > 0) :
               print "Delaying this packet for:",PSINT
            time.sleep(PSINT) # wait for a random delay time
            send(packet)

def send(packet):
    inport = packet[1][1]
    ip = packet[1][0]
    outport = inport + (1 if inport%2 is 0 else -1)
    sock.sendto(packet[0],(ip,outport))

    # hexdump the data so that we can see what changed
    print "packet sent to :", packet[1]
    hexvalue = binascii.hexlify(packet[0]) #.decode()
    print ['0x'+hexvalue[i:i+2] for i in range(0, len(hexvalue),2)]


def check_prob(option,opt,x):
    try:
        x=int(x)
    except ValueError:
        raise optparse.OptionValueError(
            "option %s: invalid integer value: %r" % (opt, x))
    if not(0<x<100):
        raise optparse.OptionValueError("option: %s - Probability should be between 0 and 100" %opt)
    return x

def check_ms(option,opt,x):
    try:
        x = int(x)
    except ValueError:
        raise optparse.OptionValueError(
            "option %s: invalid integer value: %r" % (opt, x))
    if not(0<x<1000):
        raise optparse.OptionValueError("option: %s - Delay should be between 0 and 1000 miliseconds" %opt)
    return x

def split(str, num):
    return [ str[start:start+num] for start in range(0, len(str), num) ]

class MyOptions (Option):
    TYPES = Option.TYPES + ("prob","ms")
    TYPE_CHECKER = copy(Option.TYPE_CHECKER)
    TYPE_CHECKER["prob"] = check_prob
    TYPE_CHECKER["ms"] = check_ms
	
if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    queue = Queue.Queue(maxsize=15000);

    usage = "usage: %prog port [-l loss_prob] [-c corruption_prob] [-d duplication_prob] [-r reordering_prob] [-D average_delay]"

    parser = optparse.OptionParser(option_class=MyOptions,usage=usage)
    parser.add_option('-l', '--loss', type="prob", dest='loss', default=0)
    parser.add_option('-c', '--corruption', type="prob", dest='corrupt', default=0)
    parser.add_option('-d', '--duplication', type="prob", dest='dup', default=0)
    parser.add_option('-r', '--reordering', type="prob", dest='reord', default=0)
    parser.add_option('-D', '--delaying', type="ms", dest='delay', default=0)
    try:
        (options, args) = parser.parse_args()
        if len(args) < 1 : parser.error("Argument port is required")
        if len(args) > 1 : parser.error("Only 1 argument is required")
        port=int(args[0])
        if not(100<port<20000): parser.error("Port number should be between 100 and 20000")
    except ValueError: parser.error("Port number should be a integer")
    except Exception,e: print str(e)
    print options
    options = options.__dict__
    corruptProb = options['corrupt']
    dupProb = options['dup']
    dropProb = options['loss']    
    reorderProb = options['reord']
    delay = options['delay']
    host = ''
    UDP_PORT = port
    try :
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print 'Socket created'
    except socket.error, msg :
        print 'Failed to create socket. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit()
    try:
        sock.bind((host, UDP_PORT))
        print "Waiting for data"
    except socket.error , msg:
        print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit()
    Main()
