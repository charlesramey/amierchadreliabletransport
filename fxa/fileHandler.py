
def fileExists(fname):

	try:
		f = open(fname, 'r')
		out = f.read()
		f.close()
		return True
	except:
		return False


def getFile(fname):

	if (not fileExists(fname)):
		return None

	f = open(fname, 'r')
	out = f.read()
	f.close()

	return out

def printFile(fname):
	print getFile(fname)


def writeFile(fname, contents):
	f = open(fname, 'w+')
	f.write(contents)
	f.close()
