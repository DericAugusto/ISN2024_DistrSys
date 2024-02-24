# 19/02/24 - TP Algorithmes distribuées et blockchain
# exercice 2, Q1 - page 3

import rpyc
from rpyc.utils.server import ThreadedServer
from threading import Thread

i = 0
N = 10**6

class MyService(rpyc.Service):
	def exposed_f(self):
		global i
		for _ in range(N):
			i +=1
		print("N - i = ", N - i)
   
def start():
	t = ThreadedServer(MyService, port=18861)
	t.start()
 
if __name__ == "__main__":
	start()