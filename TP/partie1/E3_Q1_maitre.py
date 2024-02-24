# 19/02/24 - TP Algorithmes distribuées et blockchain
# exercice 3, Q1 - page 4

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
    global lock, tasks_to_do, tasks_being_done
    
    if start_time is None:
      start_time = time.time()
    
    with lock:
      if tasks_to_do:
        task = tasks_to_do.pop(0)  # Récupère et enlève la première tâche de la liste
        tasks_being_done.append(task)  # Ajoute la tâche à la liste des tâches en cours
        return task
      else:
        return None  # ou une indication que toutes les tâches sont attribuées
      
  def exposed_receive_result(self,task,result):
    print(f"{result} reçue")
    global lock, tasks_being_done, tasks_to_do
    with lock:
      tasks_being_done.remove(task)  # Enlève la tâche de la liste des tâches en cours
      if not tasks_being_done and not tasks_to_do:
        
        end_time = time.time()
        total_time = end_time - start_time
        print(f"Temps de préparation : {total_time:0.1f}s")
        
        print("La salade est prête ! Bonne dégustation")


def start():
  server = ThreadedServer(MasterService, port=18861)
  server.start()
  

if __name__ == "__main__":
  start()
