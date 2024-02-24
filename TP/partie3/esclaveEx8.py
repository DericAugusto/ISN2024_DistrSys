import time
import rpyc

# Crée une connexion avec le serveur maître
def create_connection():
  return rpyc.connect("localhost", 18861)

# Prépare un fruit et simule le temps de préparation par un sleep
def prepare_fruit(id_, fruit, t):
  print(f"1 {fruit} en préparation ({t}s)")
  time.sleep(t)  # Simule le temps de préparation par un délai
  return f"1 {fruit} préparée"

# Envoie le résultat de la préparation au maître
def send_result(conn, task, result):
  return conn.root.receive_result(task, result)

# Demande une nouvelle tâche au maître
def ask_task(conn):
  return conn.root.give_task()

# Boucle principale de l'esclave
def run(conn):
  task = ask_task(conn)  # Demande la première tâche

  while task:  # Tant qu'il y a des tâches à effectuer
    id_, fruit, t = task

    print(f"1 {fruit} à préparer reçue {id_}")
    prepared_fruit = prepare_fruit(id_, fruit, t)  # Prépare le fruit

    print(f"1 {fruit} prête envoyée {id_}")
    send_result(conn, task, prepared_fruit)  # Envoie le résultat au maître

    task = ask_task(conn)  # Demande la prochaine tâche

# Point d'entrée du programme
if __name__ == "__main__":
  run(create_connection())  # Établit la connexion et commence le processus
