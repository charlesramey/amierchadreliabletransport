import threading, time, logging, socket

result = [""]
def main():
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.bind(('127.0.0.1', 6050))
	print "About to start thread"
	t = threading.Thread(target=test, args=(5.0, sock))
	t.start()
	print "Thread started"
	t.join()
	print result[0]

def test(time, sock):
	sock.settimeout(time)
	try:
		sock.recv(1024)
		result[0] = "Success"
		return
	except socket.timeout:
		result[0] = "Timedout"
		return

if __name__ == '__main__':
	main()