from threading import Lock
from rpyc.utils.server import ThreadedServer
import rpyc
import time

ingredients = [
    ("pomme", 3),
    ("pomme", 3),
    ("poire", 2),
    ("poire", 2),
    ("banane", 2),
    ("banane", 2),
    ("cerise", 1),
    ("cerise", 1),
    ("pêche", 3),
    ("pêche", 3),
    ("pastèque", 4),
]

tasks_to_do = [(i, *ingredient) for i, ingredient in enumerate(ingredients)]
tasks_being_done = []
lock = Lock() # Pour protéger les listes de tâches
start_time = None

class MasterService(rpyc.Service):
    def exposed_give_task(self):
        global start_time
        #A compléter
        
        return task
    def exposed_receive_result(self,task,result):
        print(f"{result} reçue")
        #A compléter


def start():
    server = ThreadedServer(MasterService, port=18861)
    server.start()

if __name__ == "__main__":
    start()
