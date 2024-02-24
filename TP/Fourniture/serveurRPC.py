import rpyc
from rpyc.utils.server import ThreadedServer


class MyService(rpyc.Service):
    def exposed_f(self):
        return self.g()
    def exposed_add(self,a,b):
        return a+b
    def g(self):
        return 5

def start():
    t = ThreadedServer(MyService, port=18861)
    t.start()

if __name__ == "__main__":
    start()
