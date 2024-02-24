from threading import Lock
from rpyc.utils.server import ThreadedServer
import rpyc
import time

# Liste des ingrédients nécessaires pour la préparation d'une salade
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

# Initialisation des listes de tâches à faire et des tâches en cours
tasks_to_do = [(i, *ingredient) for i, ingredient in enumerate(ingredients)]
tasks_being_done = []

# Verrou pour synchroniser l'accès aux listes de tâches
lockTask = Lock()

# Variable pour enregistrer le temps de démarrage
start_time = None

class MasterService(rpyc.Service):
  # Fonction exposée pour attribuer une tâche
  def exposed_give_task(self):
    global start_time
    if start_time == None:
      start_time = time.time()

    if len(tasks_to_do) <= 0:
      return None

    with lockTask:
      task = tasks_to_do.pop()
      tasks_being_done.append(task)

    return task

  # Fonction exposée pour recevoir le résultat d'une tâche
  def exposed_receive_result(self, task, result):
    with lockTask:
      tasks_being_done.remove(task)
    print(f"{result} reçue")

    finish = len(tasks_being_done) + len(tasks_to_do)

    # Vérification si toutes les tâches sont terminées
    if finish == 0:
      print("La salade est prête! Bonne dégustation")
      end_time = time.time()
      tpsTot = "{:.2f}".format(end_time - start_time)
      print(f"Temps de préparation : {tpsTot}s")

# Fonction pour démarrer le serveur
def start():
  server = ThreadedServer(MasterService, port=18861)
  server.start()

if __name__ == "__main__":
  start()
