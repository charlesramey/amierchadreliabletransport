import threading

recvWindow = 5

def main():

	r = threading.Thread(target = receiver)
	r.start()

	s = threading.Thread(target = sender)
	s.start()

	print "yo"


def receiver():

	i = 0
	global recvWindow

	while (True):

		if (i == 10000000):
			#print "R"
			i = 0

		recvWindow += recvWindow * i
		i += 1

def sender():
	global recvWindow
	print "S"
	print "HI"
	i = 0

	while (True):

		if (i == 10000000/3):
			print recvWindow
			i = 0
		i += 1



if __name__=="__main__":
    main()