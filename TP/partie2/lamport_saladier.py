#!/usr/bin/env python
import queue
import threading
from time import sleep
import paho.mqtt.client as mqtt
from request import Request
import random
import json

class Lamport:
  # Identifiants pour les échanges entre tous les nœuds, utilisés comme diffusion
  TOPIC = 'LAMPORT'
  # Préfixes des messages selon l'algorithme de Lamport
  MSG_REQUEST = 'REQUEST'
  MSG_RELEASE = 'RELEASE'
  MSG_PERMISSION = 'PERMISSION'

  def __init__(self, network_size):
    self.network_size = network_size
    # File d'attente des requêtes, sécurisée pour les threads et ordonnée par horodatages
    self.requests = queue.PriorityQueue()
    self.clock = 0  # Horloge logique utilisée par l'algorithme de Lamport
    self.received_permissions = 0  # Compteur global du nombre de permissions reçues pour la requête actuelle
    self.node_id = ''  # Identifiant de ce nœud dans le système
    self.sem = threading.Semaphore(0)  # Sémaphore pour la synchronisation

  def start_consumer(self):
    # Démarrage de la connexion
    self.node_id = "client-" + str(random.randint(1, 100))
    print(f'Démarrage de la connexion avec id: {self.node_id}')
    self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, self.node_id )
    self.client.on_connect = self.on_connect
    self.client.on_message = self.process_received_messages
    self.client.connect("localhost", 1883, 60)
    thread_consumer = threading.Thread(target=self.client.loop_start)
    thread_consumer.daemon = True
    thread_consumer.start()

  def on_connect(self, client, userdata, flags, rc, properties=None):
    print(f"Connected with result code {rc}")
    # Subscription renewal or other initial setup goes here
    self.client.subscribe(Lamport.TOPIC)

  def increment_clock(self):
    # Incrémentation de l'horloge globale
    self.clock += 1
    print(f"[HORLOGE] Horloge incrémentée à {self.clock}")

  def node_has_permissions(self):
    # Retourne True si toutes les permissions nécessaires pour la dernière requête ont été reçues
    return self.received_permissions == (self.network_size - 1)

  def requests_put(self, request):
    # Ajoute une requête dans la file d'attente du nœud
    self.requests.put_nowait(request)
    print(f'[AJOUT] {request}')
    print(list(self.requests.queue))

  def requests_get(self):
    # Récupère la première requête de la file d'attente du nœud
    req = self.requests.get()
    print(f'[RETRAIT] {req}')
    print(list(self.requests.queue))
    return req

  def send_msg(self, msg_type):
    # Envoie un message. Si le message est en broadcast, routing_key est ignoré.
    payload = json.dumps({"type": msg_type, "clock": self.clock, "sender_id": self.node_id})
    self.client.publish(Lamport.TOPIC, payload=payload)
    print(f'[ENVOI] msg: {msg_type}, horodatage: {self.clock}, topic: {Lamport.TOPIC}')

  def create_request(self):
    # Déclenche une requête selon les étapes de l'algorithme de Lamport
    self.increment_clock()
    request = Request(self.clock, self.node_id)
    self.requests_put(request)
    self.send_msg(Lamport.MSG_REQUEST)

  def process_received_messages(self, client, userdata, msg):
    # Décodage des attributs du message
    payload = json.loads(msg.payload)
    print(payload)
    msg_type = payload['type']
    msg_timestamp = payload['clock']
    sender_id = payload['sender_id']
    print(f"[RECEPTION] msg: {payload}, horodatage: {msg_timestamp}, expéditeur: {sender_id}")
    # Ignorer ses propres messages diffusés
    if sender_id == self.node_id:
      return

		# Recalcul de l'horloge, selon l'algorithme de Lamport
    self.clock = max(self.clock, msg_timestamp)
    self.increment_clock()
		# Traitement des messages différemment selon leur type
    if msg_type == Lamport.MSG_REQUEST:
			# Ajoute la demande reçue dans la file d'attente des requêtes
      self.requests_put(Request(msg_timestamp, sender_id))
			# Envoie la permission au demandeur
      self.send_msg(Lamport.MSG_PERMISSION)
    elif msg_type == Lamport.MSG_PERMISSION:
      self.received_permissions += 1
      print(f'[PERMISSION] {self.received_permissions}')
			# Après la réception de toutes les permissions, arrêter l'attente
      if self.node_has_permissions():
        print('Toutes les permissions ont été reçues')
				# Si la première requête dans la file appartient à ce nœud, la traiter
        req = self.requests_get()
        if req.owner_id == self.node_id:
          self.allow_critical_section()
        else:
					# Sinon, la remettre dans la file et continuer d'attendre
          self.requests_put(req)
    elif msg_type == Lamport.MSG_RELEASE:
			# Supprime le premier élément de la file, puisqu'il a été libéré par son propriétaire
      if not self.requests.empty():
        self.requests_get()
			# Si on a encore des requêtes
      if not self.requests.empty() and self.node_has_permissions():
        print('Toutes les permissions ont été reçues')
				# Si la première requête dans la file est de ce nœud, la traiter
        req = self.requests_get()
        if req.owner_id == self.node_id:
          self.allow_critical_section()
        else:
					# Sinon, la remettre dans la file
          self.requests_put(req)
  
  def enter_critical_section(self, request):
    # Réinitialisation du compteur de permissions reçues
    self.received_permissions = 0

    # Simulation de l'utilisation de la section critique
    self.simulate_critical_section_usage(5)

    # Notification aux autres nœuds que l'utilisation de la section critique est terminée
    self.send_msg(Lamport.MSG_RELEASE)

  def simulate_critical_section_usage(self, seconds):
    print(f'ENTRÉE dans la section critique pour {seconds} secondes')
    for i in range(1, seconds + 1):
      sleep(1)
      print(f'travail effectué : {str(int(100 * (i / seconds)))}%')
    print('SORTIE de la section critique')

  def wait_critical_section(self):
    # Attente d'autorisation pour entrer dans la section critique
    self.sem.acquire()

  def allow_critical_section(self):
    # Autorisation donnée pour entrer dans la section critique
    self.sem.release()

  def release_critical_section(self):
    # Réinitialisation du compteur de permissions et notification de la libération de la section critique
    self.received_permissions = 0
    self.send_msg(Lamport.MSG_RELEASE)

def read_keyboard(l):
  print("Tapez les requêtes à envoyer : ")
  while True:
    try:
      user_input = input("")
      request_time = int(user_input)
      # Envoi de la requête et attente des réponses
      l.create_request()
    except ValueError:
      print("Votre requête doit être un entier")
      continue

if __name__ == '__main__':
  l = Lamport(2)
  l.start_consumer()
  # Création d'un thread pour lire les entrées utilisateur
  thread_input = threading.Thread(target=read_keyboard, args=(l,))
  thread_input.start()