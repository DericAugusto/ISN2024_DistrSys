from threading import Lock
from rpyc.utils.server import ThreadedServer
import rpyc
import time

# Importation de la classe Bloc du fichier précédent
from blocEx6et7 import Bloc

# Liste initiale des ingrédients pour préparer la salade
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

# Initialisation des tâches à effectuer et des tâches en cours
tasks_to_do = [(i, *ingredient) for i, ingredient in enumerate(ingredients)]
tasks_being_done = []

# Verrous pour protéger l'accès aux listes de tâches et à la chaîne de blocs
lockTask = Lock()
lockBlocs = Lock()

# Liste pour stocker la blockchain
blocs = []

# Enregistrement du temps de démarrage
start_time = None

# Définition du service maître
class MasterService(rpyc.Service):
  # Fonction pour distribuer une tâche à un esclave
  def exposed_give_task(self):
    global start_time
    if start_time == None:
      start_time = time.time()

    if len(tasks_to_do) <= 0:
      return None

    with lockTask :
      task = tasks_to_do.pop()
      tasks_being_done.append(task)
    return task

  # Fonction pour recevoir le résultat d'une tâche d'un esclave
  def exposed_receive_result(self,task,result):
    with lockTask :
      tasks_being_done.remove(task)
    print(f"{result} reçue")

    # Calcul du bloc précédent pour la création d'un nouveau bloc
    previous = "0"
    if len(blocs) > 0 :
      previous = blocs[len(blocs)-1].hash

    # Création et minage d'un nouveau bloc
    bloc = Bloc(result, previous)
    bloc.mineBlock(3)

    # Ajout du bloc miné à la chaîne
    with lockBlocs:
      blocs.append(bloc)

    # Affichage de tous les blocs minés
    for b in blocs :
      print("Blocs : ",b.hash)

    # Vérification si toutes les tâches ont été complétées
    Finish = len(tasks_being_done) + len(tasks_to_do)

    # Si toutes les tâches sont terminées, affichage du temps total et message final
    if Finish == 0:
      print(f"La salade est prête! bonne dégustation")
      end_time = time.time()
      tpsTot = "{:.2f}".format(end_time - start_time)
      print(f"Temps de préparation : "+tpsTot+"s")

# Fonction pour démarrer le serveur
def start():
  server = ThreadedServer(MasterService, port=18861)
  server.start()

if __name__ == "__main__":
  start()

