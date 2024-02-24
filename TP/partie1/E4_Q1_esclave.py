# 19/02/24 - TP Algorithmes distribuées et blockchain
# exercice 4, Q1 - page 5

import time
import rpyc

def create_connection():
  return rpyc.connect("localhost", 18861)


def prepare_fruit(id_, fruit, t):
  print(f"1 {fruit} en préparation pour {t} secondes")
  time.sleep(t)
  return f"1 {fruit} préparée"


def send_result(conn, task, result):
  conn.root.exposed_receive_result(task, result)


def ask_task(conn):
  return conn.root.exposed_give_task()


def run(conn):
  task = ask_task(conn) # `task` est un couple : (fruit, temps de préparation)

  while task:
    id_, fruit, t = task

    print(f"1 {fruit} à préparer reçue, id : {id_}")
    prepared_fruit = prepare_fruit(id_, fruit, t)

    print(f"1 {fruit} prête envoyée, id : {id_}")
    send_result(conn, task, prepared_fruit)

    task = ask_task(conn)

if __name__ == "__main__":
  run(create_connection())