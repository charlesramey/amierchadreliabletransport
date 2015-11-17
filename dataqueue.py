from collections import deque
import threading



def main():
	dq = DataQueue()
	print "hi"
	s = "A wonderful fact to reflect upon, that every human creature is constituted to be that profound secret and mystery to every other. A solemn consideration, when I enter a great city by night, that every one of those darkly clustered houses encloses its own secret; that every room in every one of them encloses its own secret; that every beating heart in the hundreds of thousands of breasts there, is, in some of its imaginings, a secret to the heart nearest it! Something of the awfulness, even of Death itself, is referable to this. No more can I turn the leaves of this dear book that I loved, and vainly hope in time to read it all. No more can I look into the depths of this unfathomable water, wherein, as momentary lights glanced into it, I have had glimpses of buried treasure and other things submerged. It was appointed that the book should shut with a spring, for ever and for ever, when I had read but a page. It was appointed that the water should be locked in an eternal frost, when the light was playing on its surface, and I stood in ignorance on the shore. My friend is dead, my neighbour is dead, my love, the darling of my soul, is dead; it is the inexorable consolidation and perpetuation of the secret that was always in that individuality, and which I shall carry in mine to my life's end. In any of the burial-places of this city through which I pass, is there a sleeper more inscrutable than its busy inhabitants are, in their innermost personality, to me, or than I am to them?"
	bufferWorker(s, dq)


def bufferAdder(string, dq):

	n = 0
	i = 0
	while (i < len(string)):

		upBound = min(10, len(string) - i)
		print dq.getFreeSpace()

		while (not dq.enqueue(string[i : i + upBound])):
			n = 0
		i += upBound

def bufferWorker(string, dq):

	messageOutput = ""
	t = threading.Thread(target = bufferAdder, args= (string, dq) )
	t.start()
	while (t.isAlive()):
		x = dq.dequeue()

		if (x is not None):
			messageOutput += str(x)

	x = dq.dequeue()

	if (x is not None):
		messageOutput += str(x)
	print messageOutput




class DataQueue:

	def __init__(self):

		self.queue = deque()
		self.maxSize = 40
		self.currentSize = 0
		self.packetSize = 1024


	def enqueue(self, string):

		strLength = len(string)

		if (strLength > self.getFreeSpace()):
			return False

		self.queue.append(string)
		self.currentSize += strLength
		return True

	def dequeue(self):

		if (self.currentSize == 0):
			return None

		out = self.queue.popleft()
		strLength = len(out)
		self.currentSize -= strLength
		return out


	def getFreeSpace(self):
		return self.maxSize - self.currentSize



if __name__=="__main__":
    main()