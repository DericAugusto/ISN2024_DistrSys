import time
from utilitaires import applySha256

class Bloc:
  def __init__(self, data, previousHash):
    self.data = data
    self.previousHash = previousHash
    self.timeStamp = time.time()
    self.nonce = 0  # Initialisation de nonce
    self.hash = self.calculateHash()

  def calculateHash(self):
    # Inclut maintenant nonce dans le calcul du hachage
    input_to_hash = str(self.previousHash) + str(self.timeStamp) + str(self.data) + str(self.nonce)
    return applySha256(input_to_hash)

  def mineBlock(self, difficulty):
    target = '0' * difficulty  # Définit la cible en fonction de la difficulté
    while self.hash[:difficulty] != target:
      self.nonce += 1  # Incrémente nonce pour changer le hachage
      self.hash = self.calculateHash()
    print(f"Bloc miné : {self.hash}")

if __name__ == '__main__':  
  # Créer et miner les blocs
  blocs = [
    Bloc("Bonjour je suis le premier bloc", "0"),
    Bloc("Hello je suis le deuxième bloc", ""),
    Bloc("Yo je suis le troisième bloc", "")
  ]
  
  for difficulty in range(1, 4):
    print(f"\n-----------------------\nDifficulté : {difficulty}\n")
    
    for i, bloc in enumerate(blocs, start=1):
      start_time = time.time()
      bloc.mineBlock(difficulty)
      end_time = time.time()
      print(f"Temps pour miner le bloc {i} avec une difficulté de {difficulty}: {end_time - start_time} secondes")
      
      # Pour chaîner correctement les blocs, le previousHash du bloc suivant doit être le hash du bloc actuel
      if i < len(blocs):
        blocs[i].previousHash = bloc.hash
