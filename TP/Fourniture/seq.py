import time
from random import shuffle

# Une liste d'ingrédients. Chaque ingrédient est un couple
# (nom, temps de préparation en secondes). Les temps inscrits ici ne
# sont pas réalistes.
INGREDIENTS = [
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


def prepare_seq(ingredients):
    for fruit, t in ingredients:
        print("1 {} en préparation ({}s)...".format(fruit,t))
        time.sleep(t)
    print("\nLa salade est prête ! Bonne dégustation !")


if __name__ == "__main__":
    shuffle(INGREDIENTS)
    print(INGREDIENTS)
    start_time = time.time()
    prepare_seq(INGREDIENTS)
    end_time = time.time()
    print("Temps de préparation: {:.1f}s".format(end_time - start_time))