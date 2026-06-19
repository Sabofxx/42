# Guide complet pour reussir l'Exam Rank 05

Ce guide est fait pour reviser efficacement le dossier actuel. Il se base sur
les fichiers presents dans ce repo :

- `Spiral_Matrix.py`
- `compress_decompress.py`
- `graph_cycle_detector.py`
- `py_prism_detector.py`
- `schedule_meetings.py`

L'objectif n'est pas seulement de comprendre les solutions. L'objectif est de
pouvoir les refaire en exam, sous stress, avec une methode fiable :

- comprendre le sujet rapidement ;
- identifier le bon pattern algorithmique ;
- coder proprement sans casser la signature demandee ;
- gerer les cas limites ;
- tester vite ;
- expliquer pourquoi ton code marche.

---

## 1. Vision globale de l'exam

### Ce que l'exam teste vraiment

Ces exercices ne testent pas des bibliotheques compliquees. Ils testent surtout
ta capacite a manipuler proprement :

- des listes ;
- des chaines de caracteres ;
- des dictionnaires ;
- des ensembles (`set`) ;
- des boucles imbriquees ;
- des fonctions recursives ;
- des tris ;
- des indices ;
- des cas limites.

La difficulte principale n'est pas la syntaxe Python. La difficulte est de
garder une logique claire quand il y a beaucoup d'indices, comme dans une
matrice, un graphe, ou une recherche en grille.

### Le bon etat d'esprit

En exam, ne cherche pas a faire "intelligent". Cherche a faire :

- simple ;
- lisible ;
- correct ;
- testable ;
- conforme a la signature imposee.

Un code un peu plus long mais evident vaut mieux qu'une astuce compacte que tu
ne peux plus deboguer.

### Les cinq patterns du repo

| Fichier | Pattern principal | Idee a retenir |
|---|---|---|
| `Spiral_Matrix.py` | Matrice + bornes | Remplir un rectangle puis le reduire |
| `compress_decompress.py` | RLE | Compter les repetitions consecutives |
| `graph_cycle_detector.py` | DFS recursif | Detecter un retour dans la pile courante |
| `py_prism_detector.py` | Recherche en grille | Tester 8 directions depuis chaque case |
| `schedule_meetings.py` | Tri + glouton | Placer chaque intervalle dans une salle libre |

---

## 2. Prerequis Python indispensables

### 2.1 Indentation

En Python, l'indentation fait partie du langage. Ces deux codes ne disent pas la
meme chose :

```python
for x in values:
    if x > 0:
        print(x)
```

Ici, `print(x)` est execute seulement si `x > 0`.

```python
for x in values:
    if x > 0:
        pass
    print(x)
```

Ici, `print(x)` est execute pour tous les `x`, car il est dans la boucle mais
pas dans le `if`.

En exam, beaucoup d'erreurs viennent d'un `return`, d'un `break` ou d'un
append au mauvais niveau d'indentation.

### 2.2 Signature de fonction

Une signature ressemble a ca :

```python
def generate_spiral(n: int) -> list[list[int]]:
```

Elle dit :

- le nom de la fonction est `generate_spiral` ;
- elle prend un parametre `n` ;
- `n` est cense etre un entier ;
- elle renvoie une liste de listes d'entiers.

Les annotations de type ne bloquent pas Python a l'execution. Elles servent de
documentation. Mais en exam, il faut respecter la signature donnee, car le
correcteur automatique appellera exactement ce nom de fonction avec des donnees
precises.

### 2.3 Valeurs "truthy" et "falsy"

En Python, certaines valeurs valent `False` dans un test :

```python
if not s:
    return ""
```

Valeurs courantes considerees comme fausses :

- `""` : chaine vide ;
- `[]` : liste vide ;
- `{}` : dictionnaire vide ;
- `set()` : ensemble vide ;
- `0` : entier zero ;
- `None` : absence de valeur.

Donc :

```python
if not intervals:
    return 0, []
```

veut dire : si la liste des intervalles est vide, renvoyer directement le cas
vide.

### 2.4 Listes

Une liste est une collection ordonnee :

```python
values = [10, 20, 30]
```

Indices :

```python
values[0]   # 10
values[1]   # 20
values[-1]  # 30, dernier element
```

Operations utiles :

```python
values.append(40)    # ajoute a la fin
len(values)          # nombre d'elements
```

Piege classique avec les matrices :

```python
bad = [[0] * 3] * 3
bad[0][0] = 9
print(bad)
```

Le resultat devient :

```text
[[9, 0, 0], [9, 0, 0], [9, 0, 0]]
```

Pourquoi ? Parce que les trois lignes sont la meme liste repetee. La bonne
version est :

```python
matrix = [[0] * n for _ in range(n)]
```

Cette version cree une nouvelle ligne a chaque tour.

### 2.5 Tuples

Un tuple ressemble a une liste, mais il est immuable :

```python
meeting = (5, 10)
```

On l'utilise souvent pour representer une paire fixe :

- coordonnees `(x, y)` ;
- intervalle `(start, end)` ;
- direction `(dx, dy, name)`.

Le deballage est tres pratique :

```python
start, end = meeting
```

ou dans une boucle :

```python
for start, end in intervals:
    ...
```

### 2.6 Dictionnaires

Un dictionnaire associe une cle a une valeur :

```python
graph = {
    0: [1, 2],
    1: [2],
    2: [],
}
```

Acces direct :

```python
graph[0]  # [1, 2]
```

Acces avec valeur par defaut :

```python
graph.get(3, [])  # [] si 3 n'est pas une cle
```

En exam, `get` est utile pour eviter un `KeyError` quand un noeud apparait
comme voisin mais n'a pas sa propre entree dans le dictionnaire.

### 2.7 Ensembles (`set`)

Un `set` est une collection sans doublons, optimisee pour les tests
d'appartenance :

```python
visited = set()
visited.add(3)

if 3 in visited:
    ...
```

Operations importantes :

```python
visited.add(node)
visited.remove(node)
node in visited
node not in visited
```

Dans un DFS, `set` est souvent meilleur qu'une liste, car chercher dans un set
est beaucoup plus rapide.

### 2.8 `range`

`range(a, b)` produit les entiers de `a` inclus a `b` exclu :

```python
for i in range(1, 4):
    print(i)
```

Affiche :

```text
1
2
3
```

Avec un pas negatif :

```python
for i in range(5, 0, -1):
    print(i)
```

Affiche :

```text
5
4
3
2
1
```

Pour inclure une borne finale quand on avance :

```python
range(left, right + 1)
```

Pour inclure une borne finale quand on recule :

```python
range(right, left - 1, -1)
```

C'est une des choses les plus importantes pour `Spiral_Matrix.py`.

### 2.9 Boucle `for` ou boucle `while`

Utilise `for` quand tu connais la sequence a parcourir :

```python
for char in s:
    ...
```

Utilise `while` quand tu dois controler l'indice toi-meme :

```python
i = 0
while i < len(s):
    ...
    i += 1
```

Dans `decompress`, on utilise `while` parce qu'on lit parfois un caractere,
puis plusieurs chiffres.

### 2.10 `break`

`break` sort de la boucle courante :

```python
for room in rooms:
    if room_is_free:
        place_meeting()
        break
```

Attention : `break` ne sort que d'une seule boucle, pas de toutes les boucles
imbriquees.

### 2.11 `return`

`return` termine immediatement la fonction.

Exemple :

```python
if ok:
    return (x, y, name)
```

Dans `py_prism_detector.py`, des qu'on trouve le motif, on peut renvoyer la
position. Pas besoin de continuer a chercher.

### 2.12 Recursion

Une fonction recursive s'appelle elle-meme :

```python
def has_cycle(node):
    ...
    has_cycle(neighbor)
```

Pour qu'une recursion soit saine, il faut :

- un moyen de ne pas rappeler infiniment la meme fonction ;
- une structure qui marque l'etat courant ;
- une condition qui renvoie un resultat.

Dans le graphe, c'est le role de `visited` et `rec_stack`.

### 2.13 Tri avec `sorted`

```python
intervals = sorted(intervals, key=lambda x: x[0])
```

`sorted` renvoie une nouvelle liste triee. Le parametre `key` indique sur quoi
trier. Ici, `x[0]` signifie : trier les intervalles selon leur heure de debut.

Equivalent plus long :

```python
def get_start(interval):
    return interval[0]

intervals = sorted(intervals, key=get_start)
```

### 2.14 Chaines de caracteres

Operations utiles :

```python
s[i]             # caractere a l'indice i
s[-1]            # dernier caractere
s[i].isdigit()   # True si c'est un chiffre
"".join(parts)   # assemble une liste de chaines
char * count     # repete un caractere
```

Exemples :

```python
"a" * 3          # "aaa"
"".join(["a", "3", "b"])  # "a3b"
```

### 2.15 Complexite

Il faut savoir expliquer grossierement :

- le temps ;
- la memoire.

Notations essentielles :

| Notation | Sens |
|---|---|
| `O(1)` | temps constant |
| `O(n)` | proportionnel a la taille de l'entree |
| `O(n log n)` | typique d'un tri |
| `O(n^2)` | double boucle sur une structure de taille n |
| `O(V + E)` | graphe : sommets + aretes |

Tu n'as pas besoin de faire des demonstrations longues. Mais tu dois etre
capable de dire : "chaque case est visitee une fois", "chaque caractere est lu
une fois", ou "chaque noeud et chaque arete sont explores".

---

## 3. Methode d'exam

### 3.1 Avant de coder

Prends 2 a 5 minutes pour clarifier :

1. Quelle est l'entree ?
2. Quelle est la sortie exacte ?
3. Que faire si l'entree est vide ?
4. Faut-il renvoyer `None`, `False`, `[]`, `0`, ou une chaine vide ?
5. Le correcteur attend-il un ordre precis ?
6. Le nom de la fonction est-il impose ?
7. Les donnees sont-elles toujours valides ?

Ne code pas tant que tu ne sais pas quoi renvoyer pour les cas simples.

### 3.2 Routine de codage

Pour chaque exercice, suis ce plan :

1. Recopier la signature exacte.
2. Gerer le cas vide au debut.
3. Initialiser les structures.
4. Ecrire le parcours principal.
5. Ajouter les protections d'indice.
6. Ajouter le `return`.
7. Tester sur un exemple normal.
8. Tester sur un cas limite.

### 3.3 Cas limites a tester presque toujours

Selon l'exercice :

- entree vide ;
- un seul element ;
- deux elements ;
- taille impaire ;
- taille paire ;
- aucune solution ;
- solution au debut ;
- solution a la fin ;
- doublons ;
- elements qui se touchent exactement, comme `(10, 20)` et `(20, 30)`.

### 3.4 Comment deboguer vite

Si ton code ne marche pas :

1. Verifie la signature.
2. Verifie l'indentation du `return`.
3. Verifie les bornes de `range`.
4. Ajoute un `print` temporaire des variables importantes.
5. Teste un exemple minuscule.
6. Supprime les `print` avant de rendre.

Exemples de variables utiles a afficher :

```python
print(top, bottom, left, right, value)
print(i, char, num)
print(node, visited, rec_stack)
print(x, y, dx, dy, nx, ny)
print(start, end, rooms)
```

### 3.5 Methode du "dry run"

Un dry run consiste a executer ton code a la main sur un petit exemple.

Regle importante : prends un exemple assez petit pour tenir dans ta tete.

Exemples :

- spirale : `n = 3` ;
- compression : `"aaabbc"` ;
- graphe : `{0: [1], 1: [2], 2: [0]}` ;
- grille : `["ABC", "DEF", "GHI"]`, pattern `"BEH"` ;
- meetings : `[(0, 30), (5, 10), (15, 20)]`.

### 3.6 Check final avant de rendre

Avant de soumettre :

- le fichier a le bon nom ;
- la fonction a le bon nom ;
- le nombre de parametres est correct ;
- le type de retour correspond au sujet ;
- il n'y a pas de `print` de debug ;
- il n'y a pas de code qui s'execute au chargement, sauf si le sujet le demande ;
- les cas vides sont geres ;
- les indices ne peuvent pas sortir de la structure ;
- les tests simples passent.

---

## 4. Tests rapides a lancer

Tu peux tester dans un terminal Python ou avec de petits scripts.

### `Spiral_Matrix.py`

```python
from Spiral_Matrix import generate_spiral

print(generate_spiral(1))
print(generate_spiral(3))
print(generate_spiral(4))
```

Attendu :

```python
[[1]]

[
    [1, 2, 3],
    [8, 9, 4],
    [7, 6, 5],
]

[
    [1, 2, 3, 4],
    [12, 13, 14, 5],
    [11, 16, 15, 6],
    [10, 9, 8, 7],
]
```

### `compress_decompress.py`

```python
from compress_decompress import compress, decompress

print(compress(""))
print(compress("a"))
print(compress("aaabbc"))
print(decompress("a3b2c"))
print(decompress(compress("aaabbcccc")))
```

Attendu :

```python
""
"a"
"a3b2c"
"aaabbc"
"aaabbcccc"
```

### `graph_cycle_detector.py`

```python
from graph_cycle_detector import py_graph_cycle_detector

print(py_graph_cycle_detector({}))
print(py_graph_cycle_detector({0: [1], 1: [2], 2: []}))
print(py_graph_cycle_detector({0: [1], 1: [2], 2: [0]}))
print(py_graph_cycle_detector({0: [1], 1: [], 2: [3], 3: [2]}))
```

Attendu :

```python
False
False
True
True
```

### `py_prism_detector.py`

```python
from py_prism_detector import prism_detector

grid = [
    "ABC",
    "DEF",
    "GHI",
]

print(prism_detector(grid, "ABC"))
print(prism_detector(grid, "ADG"))
print(prism_detector(grid, "AEI"))
print(prism_detector(grid, "CFI"))
print(prism_detector(grid, "XYZ"))
```

Attendu possible :

```python
(0, 0, "H")
(0, 0, "V")
(0, 0, "D1")
(2, 0, "V")
None
```

### `schedule_meetings.py`

```python
from schedule_meetings import schedule_meetings

print(schedule_meetings([]))
print(schedule_meetings([(0, 30), (5, 10), (15, 20)]))
print(schedule_meetings([(10, 20), (20, 30)]))
print(schedule_meetings([(1, 4), (2, 5), (3, 6)]))
```

Attendu :

```python
(0, [])
(2, [[(0, 30)], [(5, 10), (15, 20)]])
(1, [[(10, 20), (20, 30)]])
(3, [[(1, 4)], [(2, 5)], [(3, 6)]])
```

---

## 5. Exercice 1: `Spiral_Matrix.py`

### But

Construire une matrice carree `n x n` remplie avec les nombres de `1` a
`n * n`, dans l'ordre d'une spirale.

Exemple pour `n = 3` :

```text
1 2 3
8 9 4
7 6 5
```

### Code actuel

```python
def generate_spiral(n: int) -> list[list[int]]:

    matrix = [[0] * n for _ in range(n)]

    top, bottom = 0, n - 1
    left, right = 0, n - 1
    value = 1

    while top <= bottom and left <= right:
        for col in range(left, right + 1):
            matrix[top][col] = value
            value += 1
        top += 1

        for row in range(top, bottom + 1):
            matrix[row][right] = value
            value += 1
        right -= 1

        if top <= bottom:
            for col in range(right, left - 1, -1):
                matrix[bottom][col] = value
                value += 1
            bottom -= 1

        if left <= right:
            for row in range(bottom, top - 1, -1):
                matrix[row][left] = value
                value += 1
            left += 1
    return matrix
```

### Idee principale

On ne pense pas a la spirale comme une courbe. On pense a un rectangle.

Au debut, le rectangle est toute la matrice :

- `top = 0` ;
- `bottom = n - 1` ;
- `left = 0` ;
- `right = n - 1`.

A chaque tour :

1. remplir la ligne du haut de gauche a droite ;
2. remplir la colonne de droite de haut en bas ;
3. remplir la ligne du bas de droite a gauche ;
4. remplir la colonne de gauche de bas en haut ;
5. reduire le rectangle.

### Pourquoi ca marche

A chaque tour de boucle, on remplit le contour externe du rectangle restant.
Ensuite, on avance les bornes vers l'interieur. Une case remplie ne sera plus
jamais touchee, car elle sort du rectangle actif.

La boucle s'arrete quand il n'existe plus de rectangle valide :

```python
while top <= bottom and left <= right:
```

### Explication ligne par ligne

```python
matrix = [[0] * n for _ in range(n)]
```

Cree une matrice `n x n` remplie de zeros. Chaque ligne est une liste
distincte.

```python
top, bottom = 0, n - 1
left, right = 0, n - 1
```

Initialise les quatre frontieres du rectangle actif.

```python
value = 1
```

`value` est le prochain nombre a placer dans la matrice.

```python
for col in range(left, right + 1):
    matrix[top][col] = value
    value += 1
top += 1
```

Remplit la ligne du haut. Apres ca, cette ligne est terminee, donc `top`
descend d'une ligne.

```python
for row in range(top, bottom + 1):
    matrix[row][right] = value
    value += 1
right -= 1
```

Remplit la colonne de droite. Apres ca, cette colonne est terminee, donc
`right` recule d'une colonne.

```python
if top <= bottom:
```

Verifie qu'il reste encore une ligne a remplir. Sans ce test, on pourrait
reecrire une ligne deja remplie dans les matrices impaires ou tres petites.

```python
for col in range(right, left - 1, -1):
```

Parcourt les colonnes a l'envers, de `right` jusqu'a `left` inclus.

```python
if left <= right:
```

Verifie qu'il reste encore une colonne a remplir.

```python
for row in range(bottom, top - 1, -1):
```

Parcourt les lignes a l'envers, de `bottom` jusqu'a `top` inclus.

### Invariants a connaitre

Un invariant est une verite qui reste vraie pendant l'algorithme.

Ici :

- toutes les cases hors du rectangle actif sont deja remplies ;
- toutes les cases dans le rectangle actif sont encore a remplir ;
- `value` vaut toujours le prochain nombre a ecrire ;
- les bornes decrivent toujours la zone restante.

### Pieges classiques

| Erreur | Consequence |
|---|---|
| utiliser `[[0] * n] * n` | toutes les lignes sont liees |
| oublier `right + 1` | derniere colonne non remplie |
| oublier `left - 1` avec le pas `-1` | premiere colonne non incluse |
| oublier les `if top <= bottom` / `if left <= right` | cases reecrites |
| incrementer `value` au mauvais endroit | doublons ou trous |

### Methode pour le refaire de memoire

1. Ecrire la matrice.
2. Ecrire les quatre bornes.
3. Ecrire `value = 1`.
4. Ecrire le `while`.
5. Ecrire les quatre directions dans cet ordre : droite, bas, gauche, haut.
6. Apres chaque direction, reduire la borne correspondante.
7. Ajouter les deux `if` avant gauche et haut.

### Complexite

- Temps : `O(n^2)`, car chaque case est remplie une fois.
- Memoire : `O(n^2)`, car on construit la matrice.

---

## 6. Exercice 2: `compress_decompress.py`

### But

Faire une compression RLE, pour "Run-Length Encoding".

Le principe :

- une suite de `a` repetes 3 fois devient `a3` ;
- une lettre seule reste seule ;
- `aaabbc` devient `a3b2c`.

La decompression fait l'inverse :

- `a3b2c` devient `aaabbc`.

### Code actuel

```python
def compress(s: str) -> str:
    if not s:
        return ""

    result = []
    count = 1

    for i in range(1, len(s)):
        if s[i] == s[i - 1]:
            count += 1
        else:
            result.append(s[i - 1])
            if count > 1:
                result.append(str(count))
            count = 1
    result.append(s[-1])
    if count > 1:
        result.append(str(count))
    return "".join(result)


def decompress(s: str) -> str:
    result = []
    i = 0

    while i < len(s):
        char = s[i]
        i += 1
        num = ""
        while i < len(s) and s[i].isdigit():
            num += s[i]
            i += 1
        count = int(num) if num else 1
        result.append(char * count)

    return "".join(result)
```

### Idee de `compress`

On parcourt la chaine en comparant chaque caractere au precedent.

Si c'est le meme, on augmente le compteur.

Si c'est different, la sequence precedente est finie :

- on ajoute le caractere precedent ;
- on ajoute le compteur seulement s'il est plus grand que `1` ;
- on remet le compteur a `1`.

### Pourquoi on traite la fin a part

Dans la boucle, on valide une sequence seulement quand on voit un changement.
Mais la derniere sequence n'est suivie d'aucun changement : la chaine s'arrete.

Il faut donc ajouter apres la boucle :

```python
result.append(s[-1])
if count > 1:
    result.append(str(count))
```

C'est un pattern tres frequent : quand tu comptes des groupes consecutifs, le
dernier groupe doit souvent etre ajoute apres la boucle.

### Pourquoi utiliser une liste puis `join`

Mauvais reflexe :

```python
result = ""
result += char
```

Ca marche, mais c'est moins efficace si tu le fais beaucoup, car les chaines
sont immuables.

Bon reflexe :

```python
parts = []
parts.append(char)
return "".join(parts)
```

### Idee de `decompress`

On lit :

1. un caractere ;
2. tous les chiffres qui le suivent ;
3. si aucun chiffre ne suit, le compteur vaut `1` ;
4. sinon, le compteur vaut le nombre lu ;
5. on ajoute `char * count`.

### Pourquoi `while`

On utilise `while` parce que l'indice avance de facon variable.

Exemple avec `a12b` :

- lire `a` ;
- lire `1` puis `2` ;
- comprendre que le nombre est `12` ;
- passer ensuite a `b`.

Avec une boucle `for`, ce serait plus penible, car `for` avance
automatiquement d'un seul caractere.

### Detail important : plusieurs chiffres

Ce code gere bien `a12` :

```python
while i < len(s) and s[i].isdigit():
    num += s[i]
    i += 1
```

Sans cette boucle, tu lirais seulement `1`, et tu decomprimerais mal.

### Limite du format

Le format est ambigu si les donnees originales peuvent contenir des chiffres.

Exemple :

```python
compress("a3")
```

peut devenir difficile a distinguer d'une compression qui voudrait dire
"trois fois a".

Pour cet exercice, on suppose generalement que les caracteres compresses ne
sont pas des chiffres. Si le sujet precise autre chose, il faut adapter le
format.

### Pieges classiques

| Erreur | Consequence |
|---|---|
| oublier le cas `not s` dans `compress` | `s[-1]` plante sur chaine vide |
| commencer la boucle a `0` | comparaison avec `s[-1]` involontaire |
| oublier la derniere sequence | resultat tronque |
| ajouter toujours `1` | format non conforme si le sujet ne veut pas les `1` |
| lire un seul chiffre dans `decompress` | `a12` devient mal interprete |
| oublier `int(num)` | impossible de multiplier par un vrai nombre |

### Methode pour le refaire de memoire

Pour `compress` :

1. Si chaine vide, return `""`.
2. `result = []`, `count = 1`.
3. Boucler de `1` a `len(s) - 1`.
4. Si meme caractere que le precedent, `count += 1`.
5. Sinon, ajouter le precedent et son compteur si besoin.
6. Apres la boucle, ajouter le dernier caractere et son compteur si besoin.
7. `return "".join(result)`.

Pour `decompress` :

1. `result = []`, `i = 0`.
2. Tant que `i < len(s)`.
3. Lire `char = s[i]`, puis avancer.
4. Lire tous les chiffres dans `num`.
5. `count = int(num) if num else 1`.
6. Ajouter `char * count`.
7. Joindre le resultat.

### Complexite

- `compress` : `O(n)`.
- `decompress` : `O(n + m)`, ou `m` est la taille de la chaine reconstruite.
- Memoire : proportionnelle a la taille du resultat.

---

## 7. Exercice 3: `graph_cycle_detector.py`

### But

Detecter si un graphe oriente contient un cycle.

Un cycle existe si, en suivant les fleches, on peut revenir a un noeud deja
present dans le chemin courant.

Exemple avec cycle :

```python
{
    0: [1],
    1: [2],
    2: [0],
}
```

Ici : `0 -> 1 -> 2 -> 0`.

### Code actuel

```python
def py_graph_cycle_detector(graph: dict[int, list[int]]) -> bool:
    if not graph:
        return False

    visited = set()
    rec_stack = set()

    def has_cycle(node):
        visited.add(node)
        rec_stack.add(node)

        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                if has_cycle(neighbor):
                    return True
            elif neighbor in rec_stack:
                return True

        rec_stack.remove(node)
        return False

    for node in graph:
        if node not in visited:  # not in
            if has_cycle(node):
                return True
    return False
```

### Graphe oriente

Un graphe oriente est un graphe ou les liens ont un sens.

Si on a :

```python
0: [1]
```

ca veut dire `0 -> 1`. Ca ne veut pas dire `1 -> 0`.

### Representation par liste d'adjacence

Le dictionnaire :

```python
{
    0: [1, 2],
    1: [2],
    2: [],
}
```

veut dire :

- `0` pointe vers `1` et `2` ;
- `1` pointe vers `2` ;
- `2` ne pointe vers rien.

### Idee principale : DFS

DFS signifie "Depth-First Search", parcours en profondeur.

Au lieu d'explorer tous les voisins d'un niveau avant de descendre, on suit un
chemin le plus loin possible, puis on revient en arriere.

### Les deux ensembles

Le code utilise deux `set` :

```python
visited = set()
rec_stack = set()
```

Ils n'ont pas le meme role.

`visited` :

- contient tous les noeuds deja vus au moins une fois ;
- evite de refaire le meme travail ;
- un noeud reste dans `visited` jusqu'a la fin.

`rec_stack` :

- contient les noeuds du chemin recursif actuel ;
- represente la pile courante ;
- un noeud est retire quand on a fini de l'explorer.

La regle centrale :

```python
elif neighbor in rec_stack:
    return True
```

Si un voisin est deja dans la pile courante, on vient de revenir sur un noeud
du chemin actuel. Il y a donc un cycle.

### Pourquoi `visited` seul ne suffit pas

Ce graphe n'a pas de cycle :

```python
{
    0: [1, 2],
    1: [3],
    2: [3],
    3: [],
}
```

Le noeud `3` peut etre atteint par deux chemins differents, mais ca ne cree pas
un cycle. Il ne faut donc pas dire "deja visite = cycle".

Le cycle existe seulement si le noeud est deja dans le chemin courant, donc
dans `rec_stack`.

### Fonction interne

```python
def has_cycle(node):
```

Cette fonction est definie dans `py_graph_cycle_detector`, donc elle peut
acceder a `graph`, `visited` et `rec_stack`.

Elle renvoie :

- `True` si elle trouve un cycle depuis ce noeud ;
- `False` sinon.

### Deroule de l'algorithme

En entrant dans un noeud :

```python
visited.add(node)
rec_stack.add(node)
```

On le marque comme vu et comme present dans le chemin actuel.

Pour chaque voisin :

```python
for neighbor in graph.get(node, []):
```

On recupere les voisins. Le `get(node, [])` evite une erreur si le noeud n'a
pas de cle dans le dictionnaire.

Si le voisin n'a jamais ete visite :

```python
if neighbor not in visited:
    if has_cycle(neighbor):
        return True
```

On descend recursivement.

Si le voisin est dans la pile courante :

```python
elif neighbor in rec_stack:
    return True
```

Cycle.

Si aucun voisin ne cree de cycle :

```python
rec_stack.remove(node)
return False
```

On retire le noeud du chemin courant et on annonce qu'aucun cycle n'a ete
trouve depuis lui.

### Pourquoi la boucle finale est necessaire

```python
for node in graph:
    if node not in visited:
        if has_cycle(node):
            return True
```

Un graphe peut etre deconnecte.

Exemple :

```python
{
    0: [1],
    1: [],
    2: [3],
    3: [2],
}
```

Si tu pars seulement de `0`, tu ne verras jamais le cycle `2 -> 3 -> 2`.

Il faut donc lancer un DFS depuis chaque noeud pas encore visite.

### Pieges classiques

| Erreur | Consequence |
|---|---|
| utiliser seulement `visited` | faux positifs |
| oublier `rec_stack.remove(node)` | faux cycles plus tard |
| enlever aussi de `visited` | beaucoup de travail refait |
| oublier les graphes deconnectes | cycles rates |
| utiliser `graph[node]` au lieu de `graph.get(node, [])` | `KeyError` possible |

### Methode pour le refaire de memoire

1. Cas vide : `False`.
2. Creer `visited` et `rec_stack`.
3. Creer une fonction interne `has_cycle(node)`.
4. A l'entree, ajouter `node` aux deux sets.
5. Pour chaque voisin :
   - si pas visite, DFS ;
   - sinon si dans `rec_stack`, cycle.
6. A la sortie, retirer `node` de `rec_stack`.
7. Boucler sur tous les noeuds du graphe.

### Complexite

- Temps : `O(V + E)`, avec `V` noeuds et `E` aretes.
- Memoire : `O(V)`, pour les sets et la pile de recursion.

---

## 8. Exercice 4: `py_prism_detector.py`

### But

Chercher un motif (`pattern`) dans une grille de caracteres.

La grille est une liste de chaines :

```python
grid = [
    "ABC",
    "DEF",
    "GHI",
]
```

On veut savoir si un mot apparait :

- horizontalement ;
- verticalement ;
- diagonalement ;
- dans les directions positives ou negatives.

La fonction renvoie :

- `(x, y, name)` si elle trouve le motif ;
- `None` sinon.

### Code actuel

```python
def prism_detector(grid: list[str], pattern: str):
    if not grid or not pattern:
        return None

    h = len(grid)
    w = len(grid[0])

    directions = [
        (1, 0, "H"),
        (-1, 0, "H-"),
        (0, 1, "V"),
        (0, -1, "V-"),
        (1, 1, "D1"),
        (-1, -1, "D1-"),
        (-1, 1, "D2"),
        (1, -1, "D2-"),
    ]

    for y in range(h):
        for x in range(w):
            for dx, dy, name in directions:
                ok = True

                for i in range(len(pattern)):
                    nx = x + dx * i
                    ny = y + dy * i

                    if (
                        nx < 0
                        or ny < 0
                        or nx >= w
                        or ny >= h
                        or grid[ny][nx] != pattern[i]
                    ):
                        ok = False
                        break

                if ok:
                    return (x, y, name)

    return None
```

### Coordonnees

Ici :

- `x` represente la colonne ;
- `y` represente la ligne ;
- `grid[y][x]` donne le caractere.

Exemple :

```python
grid = [
    "ABC",
    "DEF",
    "GHI",
]
```

Coordonnees :

```text
(0,0)=A  (1,0)=B  (2,0)=C
(0,1)=D  (1,1)=E  (2,1)=F
(0,2)=G  (1,2)=H  (2,2)=I
```

Il faut retenir : ligne d'abord dans la grille, donc `grid[y][x]`.

### Dimensions

```python
h = len(grid)
w = len(grid[0])
```

- `h` est la hauteur : nombre de lignes ;
- `w` est la largeur : nombre de colonnes.

Ce code suppose que toutes les lignes ont la meme longueur que `grid[0]`.

### Directions

Chaque direction est un tuple :

```python
(dx, dy, name)
```

`dx` indique comment `x` change a chaque lettre.

`dy` indique comment `y` change a chaque lettre.

Table :

| Direction | Tuple | Sens |
|---|---|---|
| `H` | `(1, 0)` | droite |
| `H-` | `(-1, 0)` | gauche |
| `V` | `(0, 1)` | bas |
| `V-` | `(0, -1)` | haut |
| `D1` | `(1, 1)` | diagonale bas-droite |
| `D1-` | `(-1, -1)` | diagonale haut-gauche |
| `D2` | `(-1, 1)` | diagonale bas-gauche |
| `D2-` | `(1, -1)` | diagonale haut-droite |

### Parcours principal

```python
for y in range(h):
    for x in range(w):
        for dx, dy, name in directions:
```

On teste :

- chaque ligne `y` ;
- chaque colonne `x` ;
- chaque direction possible.

Autrement dit : "Depuis chaque case, essaie de lire le mot dans les 8
directions."

### Test d'un motif

```python
ok = True
```

On part du principe que la direction marche, puis on cherche une raison de la
rejeter.

Pour chaque lettre du pattern :

```python
for i in range(len(pattern)):
    nx = x + dx * i
    ny = y + dy * i
```

`i` est la position dans le motif.

Si `i = 0`, on reste sur la case de depart :

```python
nx = x
ny = y
```

Si `i = 1`, on avance d'un pas dans la direction :

```python
nx = x + dx
ny = y + dy
```

Si `i = 2`, on avance de deux pas :

```python
nx = x + 2 * dx
ny = y + 2 * dy
```

### Protection des bornes

```python
if (
    nx < 0
    or ny < 0
    or nx >= w
    or ny >= h
    or grid[ny][nx] != pattern[i]
):
```

On rejette la direction si :

- `nx` sort a gauche ;
- `ny` sort en haut ;
- `nx` sort a droite ;
- `ny` sort en bas ;
- le caractere de la grille ne correspond pas au caractere attendu.

L'ordre est important : on verifie les bornes avant d'acceder a
`grid[ny][nx]`. Grace au `or`, Python s'arrete des qu'une condition est vraie.
Donc si `nx` est invalide, Python ne tente pas l'acces dangereux.

### Retour du resultat

```python
if ok:
    return (x, y, name)
```

Des que tout le motif est valide, on renvoie la position de depart et le nom de
la direction.

Si aucune combinaison ne marche :

```python
return None
```

### Pieges classiques

| Erreur | Consequence |
|---|---|
| confondre `grid[x][y]` et `grid[y][x]` | resultats faux |
| oublier les directions negatives | mots inverses non trouves |
| verifier `grid[ny][nx]` avant les bornes | `IndexError` |
| oublier `break` quand une lettre echoue | travail inutile, logique fragile |
| renvoyer `False` au lieu de `None` | mauvais type de retour si le sujet attend `None` |
| supposer une grille non vide sans test | `grid[0]` peut planter |

### Methode pour le refaire de memoire

1. Si `not grid` ou `not pattern`, retourner `None`.
2. Calculer `h` et `w`.
3. Ecrire la liste des 8 directions.
4. Boucler sur `y`, puis `x`, puis directions.
5. Pour chaque direction, mettre `ok = True`.
6. Pour chaque indice `i` du pattern, calculer `nx`, `ny`.
7. Si sortie de grille ou mauvais caractere, `ok = False`, `break`.
8. Si `ok`, retourner `(x, y, name)`.
9. A la fin, retourner `None`.

### Complexite

Soit :

- `h` = hauteur ;
- `w` = largeur ;
- `p` = longueur du pattern.

Temps :

```text
O(h * w * 8 * p)
```

Comme `8` est constant, on dit souvent :

```text
O(h * w * p)
```

Memoire :

```text
O(1)
```

hors stockage de l'entree.

---

## 9. Exercice 5: `schedule_meetings.py`

### But

On te donne des reunions sous forme d'intervalles `(start, end)`.

Tu dois trouver combien de salles sont necessaires pour qu'aucune reunion qui
se chevauche ne soit dans la meme salle.

La fonction renvoie :

```python
(nombre_de_salles, salles)
```

Exemple :

```python
[(0, 30), (5, 10), (15, 20)]
```

Il faut deux salles :

- salle 1 : `(0, 30)` ;
- salle 2 : `(5, 10)`, puis `(15, 20)`.

### Code actuel

```python
def schedule_meetings(intervals: list[tuple[int, int]]) -> tuple[int, list]:
    if not intervals:
        return 0, []

    intervals = sorted(intervals, key=lambda x: x[0])
    rooms = []

    for start, end in intervals:
        placed = False
        for room in rooms:
            if room[-1][1] <= start:
                room.append((start, end))
                placed = True
                break
        if not placed:
            rooms.append([(start, end)])
    return len(rooms), rooms
```

### Idee principale

On trie d'abord les reunions par heure de debut.

Ensuite, pour chaque reunion :

- on cherche une salle deja libre ;
- si on en trouve une, on ajoute la reunion dedans ;
- sinon, on ouvre une nouvelle salle.

### Pourquoi trier

Sans tri, la derniere reunion d'une salle ne serait pas forcement pertinente.

Avec le tri par debut, quand on traite une reunion, toutes les reunions deja
placees commencent avant elle. Pour savoir si une salle est libre, il suffit de
regarder la fin de la derniere reunion de cette salle.

### Ligne par ligne

```python
if not intervals:
    return 0, []
```

Cas vide : aucune reunion, aucune salle.

```python
intervals = sorted(intervals, key=lambda x: x[0])
```

Trie les reunions par debut croissant.

```python
rooms = []
```

Chaque element de `rooms` est une salle, et chaque salle est une liste
d'intervalles.

```python
for start, end in intervals:
```

Parcourt les reunions triees, avec deballage du tuple.

```python
placed = False
```

Indique si la reunion courante a deja ete placee.

```python
for room in rooms:
    if room[-1][1] <= start:
```

Pour chaque salle, on regarde la fin de sa derniere reunion.

Si cette fin est inferieure ou egale au debut de la nouvelle reunion, la salle
est libre.

Pourquoi `<=` ?

Parce qu'une reunion qui finit a `10` et une autre qui commence a `10` ne se
chevauchent pas.

```python
room.append((start, end))
placed = True
break
```

On ajoute la reunion, on marque qu'elle est placee, puis on arrete de chercher
une salle.

```python
if not placed:
    rooms.append([(start, end)])
```

Si aucune salle existante ne marche, on cree une nouvelle salle contenant cette
reunion.

```python
return len(rooms), rooms
```

On renvoie le nombre de salles et le planning complet.

### Pourquoi le nombre de salles est minimal

Quand l'algorithme ouvre une nouvelle salle, cela signifie que toutes les salles
existantes ont une derniere reunion qui finit apres le debut de la reunion
courante.

Donc, a cet instant, toutes ces reunions chevauchent la reunion courante.

S'il y a deja `k` salles occupees et que la nouvelle reunion chevauche les `k`
dernieres reunions, alors il faut au moins `k + 1` salles. Ouvrir une nouvelle
salle est donc necessaire.

### Pieges classiques

| Erreur | Consequence |
|---|---|
| ne pas trier | placements faux |
| utiliser `<` au lieu de `<=` | cree trop de salles quand deux reunions se touchent |
| regarder `room[0]` au lieu de `room[-1]` | compare avec la mauvaise reunion |
| oublier `placed = True` | cree une salle en trop |
| oublier `break` | peut placer la meme reunion plusieurs fois |
| renvoyer seulement `rooms` | retour non conforme si le sujet attend le nombre aussi |

### Methode pour le refaire de memoire

1. Si liste vide, retourner `(0, [])`.
2. Trier par debut.
3. Creer `rooms = []`.
4. Pour chaque `(start, end)` :
   - `placed = False` ;
   - tester chaque salle ;
   - si `room[-1][1] <= start`, ajouter et `break` ;
   - sinon creer une nouvelle salle.
5. Retourner `(len(rooms), rooms)`.

### Complexite

Tri :

```text
O(n log n)
```

Placement :

```text
O(n * k)
```

ou `k` est le nombre de salles. Dans le pire cas, `k = n`, donc :

```text
O(n^2)
```

Memoire :

```text
O(n)
```

car on stocke toutes les reunions dans les salles.

---

## 10. Templates mentaux a memoriser

### 10.1 Matrice avec quatre bornes

Utilise ce template quand tu dois parcourir une matrice par couches :

```python
top, bottom = 0, n - 1
left, right = 0, n - 1

while top <= bottom and left <= right:
    # haut
    for col in range(left, right + 1):
        ...
    top += 1

    # droite
    for row in range(top, bottom + 1):
        ...
    right -= 1

    # bas
    if top <= bottom:
        for col in range(right, left - 1, -1):
            ...
        bottom -= 1

    # gauche
    if left <= right:
        for row in range(bottom, top - 1, -1):
            ...
        left += 1
```

### 10.2 Compter des groupes consecutifs

Template :

```python
if not s:
    return ""

count = 1
result = []

for i in range(1, len(s)):
    if s[i] == s[i - 1]:
        count += 1
    else:
        # valider le groupe precedent
        ...
        count = 1

# valider le dernier groupe
...
```

### 10.3 DFS avec pile de recursion

Template :

```python
visited = set()
rec_stack = set()

def dfs(node):
    visited.add(node)
    rec_stack.add(node)

    for neighbor in graph.get(node, []):
        if neighbor not in visited:
            if dfs(neighbor):
                return True
        elif neighbor in rec_stack:
            return True

    rec_stack.remove(node)
    return False
```

### 10.4 Recherche dans 8 directions

Template :

```python
directions = [
    (1, 0),
    (-1, 0),
    (0, 1),
    (0, -1),
    (1, 1),
    (-1, -1),
    (-1, 1),
    (1, -1),
]

for y in range(h):
    for x in range(w):
        for dx, dy in directions:
            ok = True
            for i in range(len(pattern)):
                nx = x + dx * i
                ny = y + dy * i
                if nx < 0 or ny < 0 or nx >= w or ny >= h:
                    ok = False
                    break
                if grid[ny][nx] != pattern[i]:
                    ok = False
                    break
            if ok:
                return ...
```

### 10.5 Glouton apres tri

Template :

```python
items = sorted(items, key=lambda x: x[0])
result = []

for item in items:
    placed = False
    for group in result:
        if can_place(group, item):
            group.append(item)
            placed = True
            break
    if not placed:
        result.append([item])
```

---

## 11. Diagnostic des erreurs frequentes

### `IndexError`

Cause probable :

- tu accedes a une liste ou une chaine avec un indice invalide ;
- tu verifies les bornes trop tard ;
- un `range` va trop loin.

Reflexes :

- verifier les `+ 1` et `- 1` ;
- afficher l'indice juste avant l'acces ;
- dans une grille, verifier `0 <= x < w` et `0 <= y < h`.

### `KeyError`

Cause probable :

- tu utilises `graph[node]` alors que `node` n'est pas une cle.

Reflexe :

```python
graph.get(node, [])
```

### `TypeError`

Cause probable :

- tu multiplies une chaine par une chaine au lieu d'un entier ;
- tu ajoutes un entier dans une liste de chaines puis tu fais `join` ;
- tu appelles une fonction avec le mauvais nombre d'arguments.

Exemple :

```python
result.append(count)       # mauvais pour join
result.append(str(count))  # bon
```

### Resultat presque bon mais decale

Cause probable :

- probleme de borne ;
- `range` exclut la fin ;
- increment/decrement place trop tot ou trop tard.

Reflexes :

- tester une taille `1`, puis `2`, puis `3` ;
- afficher les variables de controle ;
- verifier les `right + 1`, `left - 1`, `top - 1`.

### Boucle infinie

Cause probable :

- dans un `while`, l'indice n'avance pas dans tous les cas ;
- recursion sans marquage correct.

Reflexes :

- verifier que `i += 1` arrive bien ;
- verifier que les noeuds sont ajoutes a `visited`.

---

## 12. Plan de revision

### Si tu as une semaine

Jour 1 :

- revoir les bases Python ;
- refaire `compress` sans regarder.

Jour 2 :

- refaire `decompress` ;
- tester avec des nombres a deux chiffres.

Jour 3 :

- refaire `generate_spiral` ;
- insister sur `range(..., ..., -1)`.

Jour 4 :

- refaire le DFS de graphe ;
- dessiner `visited` et `rec_stack` a la main.

Jour 5 :

- refaire `prism_detector` ;
- tester les 8 directions.

Jour 6 :

- refaire `schedule_meetings` ;
- tester les cas qui se touchent exactement.

Jour 7 :

- refaire les cinq exercices dans l'ordre, sans correction ;
- noter les endroits ou tu bloques ;
- relire uniquement ces parties.

### Si tu as une seule journee

1. Lire les cinq "Methode pour le refaire de memoire".
2. Recoder chaque exercice une fois.
3. Tester les cas limites donnes dans ce guide.
4. Refaire seulement les exercices rates.
5. Le soir, relire les pieges classiques.

### Si tu as une heure

Priorite :

1. Signatures et retours attendus.
2. Cas vides.
3. Templates mentaux.
4. Pieges classiques.
5. Tests rapides.

---

## 13. Comment expliquer ton code a l'oral

Meme si l'exam est automatique, savoir expliquer aide a coder proprement.

### Spirale

"Je maintiens quatre bornes qui representent le rectangle restant. A chaque
tour, je remplis le haut, la droite, le bas et la gauche, puis je reduis les
bornes. Les tests avant le bas et la gauche evitent de reecrire une ligne ou
une colonne dans les cas impairs."

### Compression

"Je parcours la chaine en comptant les caracteres consecutifs identiques. Quand
le caractere change, j'ajoute le groupe precedent au resultat. Je traite le
dernier groupe apres la boucle parce qu'il n'est jamais suivi d'un changement."

### Decompression

"Je lis un caractere, puis tous les chiffres qui le suivent. Si aucun chiffre
n'est present, le compteur vaut 1. Ensuite j'ajoute le caractere repete ce
nombre de fois."

### Graphe

"J'utilise un DFS avec deux ensembles. `visited` contient les noeuds deja
explores, et `rec_stack` contient seulement les noeuds du chemin courant. Si je
retombe sur un noeud de `rec_stack`, alors il y a un cycle."

### Prism detector

"Je teste chaque case comme point de depart, puis chaque direction possible.
Pour chaque lettre du motif, je calcule la nouvelle position avec `x + dx * i`
et `y + dy * i`. Je verifie les bornes avant d'acceder a la grille."

### Meetings

"Je trie les reunions par debut. Pour chaque reunion, je cherche une salle dont
la derniere reunion finit avant son debut. Si aucune salle n'est libre, j'en
ouvre une nouvelle. Quand j'ouvre une salle, c'est necessaire car toutes les
salles existantes chevauchent la reunion courante."

---

## 14. Fiche ultra-condensee

### Cas vides

```python
if not s:
    return ""

if not graph:
    return False

if not grid or not pattern:
    return None

if not intervals:
    return 0, []
```

### Bornes importantes

```python
range(left, right + 1)
range(top, bottom + 1)
range(right, left - 1, -1)
range(bottom, top - 1, -1)
```

### Acces grille

```python
grid[y][x]
```

Jamais oublier : `y` d'abord, `x` ensuite.

### Protection grille

```python
if nx < 0 or ny < 0 or nx >= w or ny >= h:
    ...
```

### DFS cycle

```python
if neighbor not in visited:
    if has_cycle(neighbor):
        return True
elif neighbor in rec_stack:
    return True
```

### RLE dernier groupe

```python
result.append(s[-1])
if count > 1:
    result.append(str(count))
```

### Meetings

```python
if room[-1][1] <= start:
    room.append((start, end))
```

---

## 15. Checklist finale de reussite

Avant l'exam, tu dois pouvoir refaire sans aide :

- creer une matrice avec des lignes independantes ;
- utiliser `range` en avant et en arriere ;
- expliquer pourquoi `right + 1` et `left - 1` sont necessaires ;
- compter des repetitions consecutives ;
- traiter le dernier groupe apres une boucle ;
- lire plusieurs chiffres dans une chaine ;
- utiliser `set` pour `visited` ;
- expliquer la difference entre `visited` et `rec_stack` ;
- parcourir une grille avec `x`, `y`, `dx`, `dy` ;
- verifier les bornes avant d'acceder a une case ;
- trier une liste de tuples avec `key=lambda x: x[0]` ;
- utiliser `room[-1][1]` pour lire la fin de la derniere reunion ;
- choisir le bon retour pour les cas vides.

Si tu maitrises ces points, tu as l'essentiel pour reussir ce dossier.

