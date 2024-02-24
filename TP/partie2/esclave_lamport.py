import time
import rpyc
from lamport_saladier import *

def create_connection():
  # Crée une connexion RPyC au serveur local sur le port 18861
  return rpyc.connect("localhost", 18861)

def prepare_fruit(id_, fruit, t):
  # Simule la préparation d'un fruit en attendant un certain temps (t)
  print(f"1 {fruit} en préparation ({t}s)")
  time.sleep(t)
  return f"1 {fruit} préparée"

def send_result(conn, task, result):
  # Envoie le résultat de la préparation au serveur via RPyC
  conn.root.receive_result(task, result)

def ask_task(conn):
  # Demande une nouvelle tâche au serveur via RPyC
  return conn.root.give_task()

def run(conn):
  # Boucle principale pour traiter les tâches reçues du serveur
  task = ask_task(conn)

  while task:
    id_, fruit, t = task

    # Crée une demande d'accès à la section critique avant de préparer le fruit
    lamport.create_request()
    # Attente pour l'accès à la section critique
    lamport.wait_critical_section()

    print(f"1 {fruit} à préparer reçue {id_}")
    prepared_fruit = prepare_fruit(id_, fruit, t)

    print(f"1 {fruit} prête envoyée {id_}")
    send_result(conn, task, prepared_fruit)

    # Libération de la section critique après la préparation
    lamport.release_critical_section()

    task = ask_task(conn)

if __name__ == "__main__":
  # Initialisation de l'instance Lamport avec 2 comme taille du réseau
  lamport = Lamport(2)
  # Démarrage du consommateur pour écouter les messages MQTT
  lamport.start_consumer()
  run(create_connection())
  
