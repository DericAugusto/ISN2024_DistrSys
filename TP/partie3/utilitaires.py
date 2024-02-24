import hashlib

def applySha256(input):
  # Encode l'entrée en bytes, nécessaire pour l'utilisation avec hashlib
  encoded_input = input.encode()
  # Crée un objet sha256
  sha256 = hashlib.sha256()
  # Met à jour cet objet avec les données encodées
  sha256.update(encoded_input)
  # Retourne le hachage hexadécimal de ces données
  return sha256.hexdigest()

# Exemple d'utilisation
if __name__ == '__main__':
  exemple_input = "Bonjour, je suis un exemple de données à hacher."
  hash_result = applySha256(exemple_input)
  print(f"Le hachage SHA256 de '{exemple_input}' est : {hash_result}")
