import time
import rpyc

def create_connection():
    return rpyc.connect("localhost", 18861)


def prepare_fruit(id_, fruit, t):
    print(f"1 {fruit} en préparation ({t}s)")
    time.sleep(t)
    return f"1 {fruit} préparée"


def send_result(conn, task, result):
    # A compléter


def ask_task(conn):
    #A compléter


def run(conn):
    # `task` est un couple `(fruit, temps de préparation)`.
    task = ask_task(conn)

    while task:
        id_, fruit, t = task

        print(f"1 {fruit} à préparer reçue {id_}")
        prepared_fruit = prepare_fruit(id_, fruit, t)

        print(f"1 {fruit} prête envoyée {id_}")
        send_result(conn, task, prepared_fruit)

        task = ask_task(conn)


if __name__ == "__main__":
    run(create_connection())
