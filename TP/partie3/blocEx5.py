import time
from utilitaires import applySha256

class Bloc:
  def __init__(self, data, previousHash):
    self.data = data
    self.previousHash = previousHash
    self.timeStamp = time.time()
    self.hash = self.calculateHash()

  def calculateHash(self):
    # Concaténation des attributs pour calculer le hachage
    input_to_hash = str(self.previousHash) + str(self.timeStamp) + str(self.data)
    return applySha256(input_to_hash)


if __name__ == '__main__':
  maChaine = []

  # Création du premier bloc avec previousHash '0'
  bloc1 = Bloc("Bonjour je suis le premier bloc", "0")
  maChaine.append(bloc1)

  # Création du deuxième bloc avec previousHash du premier bloc
  bloc2 = Bloc("Hello je suis le deuxième bloc", bloc1.hash)
  maChaine.append(bloc2)

  # Création du troisième bloc avec previousHash du deuxième bloc
  bloc3 = Bloc("Yo je suis le troisième bloc", bloc2.hash)
  maChaine.append(bloc3)

  # Affichage des valeurs de hachage pour chaque bloc
  for bloc in maChaine:
    print(f"Hash du bloc: {bloc.hash}")

  # Explication sur les changements de hachage à chaque exécution
  print("Exercice 5 : Les valeurs de hachage des blocs changent à chaque exécution car le timeStamp (l'heure de création) du bloc change, affectant ainsi le résultat du hachage.")
