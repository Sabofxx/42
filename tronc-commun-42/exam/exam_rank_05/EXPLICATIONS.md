# Explications détaillées — Exam Rank 05

Ce document explique **en détail** les 4 fichiers de cet exercice. Chaque
ligne, chaque concept et chaque astuce est décortiqué, même les choses qui
peuvent sembler évidentes. L'objectif est que tu puisses **réécrire ces
fichiers de mémoire** en comprenant *pourquoi* chaque ligne existe.

## Sommaire

1. [`Spiral_Matrix.py` — générer une matrice en spirale](#1-spiral_matrixpy)
2. [`compress_decompress.py` — compression RLE](#2-compress_decompresspy)
3. [`graph_cycle_detector.py` — détection de cycle dans un graphe](#3-graph_cycle_detectorpy)
4. [`schedule_meetings.py` — planification de réunions / salles](#4-schedule_meetingspy)

---

## Rappels Python utiles pour tout le document

Avant de plonger dans les fichiers, voici des notions de base réutilisées
partout.

### Les annotations de type (`type hints`)

```python
def generate_spiral(n: int) -> list[list[int]]:
```

- `n: int` veut dire « le paramètre `n` est censé être un entier ».
- `-> list[list[int]]` veut dire « cette fonction **renvoie** une liste de
  listes d'entiers » (donc une matrice).
- ⚠️ Important : Python **n'oblige rien**. Ces annotations sont de la
  documentation. Si tu passes un texte à la place d'un `int`, Python ne va
  pas planter à cause de l'annotation — c'est juste une indication pour le
  lecteur et les outils (linters, IDE).

### Les listes (`list`)

- Une liste est une suite ordonnée d'éléments : `[10, 20, 30]`.
- On accède à un élément par son **indice**, qui commence à `0` :
  `ma_liste[0]` est le premier élément.
- `ma_liste[-1]` est le **dernier** élément (indice négatif = on compte
  depuis la fin).
- `len(ma_liste)` donne le nombre d'éléments.
- `ma_liste.append(x)` ajoute `x` à la fin.

### La fonction `range()`

`range(a, b)` génère les nombres de `a` **inclus** jusqu'à `b` **exclu**.

```python
range(0, 3)   # produit 0, 1, 2   (3 n'est PAS inclus)
range(2, 5)   # produit 2, 3, 4
```

Avec un 3ème argument (le « pas ») :

```python
range(5, 0, -1)   # produit 5, 4, 3, 2, 1  (compte à rebours, 0 exclu)
```

C'est la raison pour laquelle on voit souvent des `+ 1` ou des `- 1` :
pour compenser le fait que la borne de droite est exclue.

### `set` (ensemble)

- Un `set` est une collection **sans doublon** et **non ordonnée** :
  `{1, 2, 3}`.
- Test d'appartenance **très rapide** : `x in mon_set`.
- `mon_set.add(x)` ajoute, `mon_set.remove(x)` enlève.

---

## 1. `Spiral_Matrix.py`

### But

Construire une matrice carrée `n × n` remplie par les nombres `1, 2, 3, …`
en suivant un **parcours en spirale** (depuis le coin haut-gauche, vers la
droite, puis vers le bas, puis la gauche, puis le haut, en se rapprochant
du centre).

Exemple pour `n = 3` :

```
1  2  3
8  9  4
7  6  5
```

On part de `1` en haut à gauche, on va à droite (`1 2 3`), puis on descend
(`4 5`), puis on va à gauche (`6 7`), puis on remonte (`8`), et enfin le
centre (`9`).

### Le code complet

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

### Ligne par ligne

#### Création de la matrice vide

```python
matrix = [[0] * n for _ in range(n)]
```

- `[0] * n` crée une liste de `n` zéros. Par exemple `[0] * 3` → `[0, 0, 0]`.
  C'est **une ligne** de la matrice.
- `for _ in range(n)` répète l'opération `n` fois. On obtient donc `n`
  lignes → une matrice carrée.
- Le `_` est une **variable poubelle** : par convention en Python, `_`
  signifie « je dois écrire une variable ici mais je ne vais pas l'utiliser ».
  Ici on veut juste répéter `n` fois, peu importe l'indice.

⚠️ **Piège classique à éviter** : on n'écrit **pas** `[[0] * n] * n`. Cette
écriture créerait `n` fois la **même** ligne (la même référence en mémoire).
Modifier `matrix[0][0]` modifierait alors **toutes** les lignes en même
temps. La compréhension de liste (`for _ in range(n)`) crée bien `n` listes
**distinctes**.

#### Les quatre bornes

```python
top, bottom = 0, n - 1
left, right = 0, n - 1
value = 1
```

C'est le cœur de l'astuce. On délimite un **rectangle** (au début, c'est
toute la matrice) avec 4 indices :

- `top` : indice de la ligne la plus haute encore à remplir.
- `bottom` : indice de la ligne la plus basse encore à remplir.
- `left` : indice de la colonne la plus à gauche.
- `right` : indice de la colonne la plus à droite.

Comme les indices vont de `0` à `n - 1`, au départ `top = left = 0` et
`bottom = right = n - 1`.

`value` est le prochain nombre à écrire ; il commence à `1` et s'incrémente
à chaque case remplie.

L'idée : à chaque tour de boucle on remplit **le contour** du rectangle
actuel, puis on **rétrécit** le rectangle vers l'intérieur (en bougeant les
bornes). On répète jusqu'à ce que le rectangle soit vide.

#### La boucle principale

```python
while top <= bottom and left <= right:
```

Tant qu'il reste au moins une ligne **et** au moins une colonne valides
(c.-à-d. le rectangle n'est pas vide), on continue.

#### Étape 1 : aller vers la droite (bord du haut)

```python
for col in range(left, right + 1):
    matrix[top][col] = value
    value += 1
top += 1
```

- On parcourt les colonnes de `left` à `right` (le `+ 1` rend `right`
  inclus, voir le rappel sur `range`).
- On reste sur la ligne `top` (la plus haute) et on remplit de gauche à
  droite.
- Après avoir rempli toute la ligne du haut, elle est « terminée » : on
  fait `top += 1` pour **descendre** la frontière supérieure (cette ligne
  ne sera plus jamais touchée).

#### Étape 2 : descendre (bord de droite)

```python
for row in range(top, bottom + 1):
    matrix[row][right] = value
    value += 1
right -= 1
```

- On reste sur la colonne `right` (la plus à droite) et on descend de
  `top` (qui a déjà été incrémenté juste avant) jusqu'à `bottom`.
- Ensuite `right -= 1` : la colonne de droite est terminée, on **rétrécit**
  la frontière droite vers la gauche.

#### Étape 3 : aller vers la gauche (bord du bas)

```python
if top <= bottom:
    for col in range(right, left - 1, -1):
        matrix[bottom][col] = value
        value += 1
    bottom -= 1
```

- Le test `if top <= bottom:` évite de **réécrire** une ligne déjà remplie.
  Cas typique : une matrice avec une seule ligne restante. Après l'étape 1,
  `top` a dépassé `bottom`. Sans ce test, on remplirait deux fois la même
  ligne.
- `range(right, left - 1, -1)` : on parcourt **à l'envers** (pas de `-1`),
  de `right` jusqu'à `left`. Le `left - 1` comme borne de fin garantit que
  `left` est **inclus** (la borne de fin est exclue, donc on met une de
  moins).
- On reste sur la ligne `bottom` (la plus basse) et on va de droite à
  gauche.
- `bottom -= 1` : la ligne du bas est terminée, on **remonte** la frontière
  inférieure.

#### Étape 4 : remonter (bord de gauche)

```python
if left <= right:
    for row in range(bottom, top - 1, -1):
        matrix[row][left] = value
        value += 1
    left += 1
```

- Le test `if left <= right:` évite de réécrire une colonne déjà remplie
  (cas d'une seule colonne restante).
- `range(bottom, top - 1, -1)` : on remonte de `bottom` jusqu'à `top`
  (inclus grâce au `top - 1`).
- On reste sur la colonne `left` (la plus à gauche).
- `left += 1` : la colonne de gauche est terminée, on **avance** la
  frontière gauche vers la droite.

#### Fin

```python
return matrix
```

Quand le `while` se termine (rectangle vide), la matrice est entièrement
remplie ; on la renvoie.

### Récapitulatif visuel (pour `n = 4`)

```
 1   2   3   4
12  13  14   5
11  16  15   6
10   9   8   7
```

On voit bien la spirale : le tour extérieur `1→12`, puis le carré intérieur
`13→16`.

### Complexité

- **Temps** : `O(n²)` — chaque case est remplie exactement une fois.
- **Espace** : `O(n²)` — la matrice elle-même.

---

## 2. `compress_decompress.py`

### But

Implémenter une compression **RLE** (*Run-Length Encoding* / codage par
plages). Le principe : remplacer une suite de caractères identiques par le
caractère suivi de son **nombre de répétitions**.

Exemples :

| Original   | Compressé |
|------------|-----------|
| `aaabbc`   | `a3b2c`   |
| `abc`      | `abc`     |
| `aaaa`     | `a4`      |

Règle importante de cette implémentation : si un caractère apparaît **une
seule fois**, on n'écrit **pas** le `1` (on garde juste `a`, pas `a1`).
Ça rend la compression plus compacte.

### La fonction `compress`

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
```

#### Ligne par ligne

```python
if not s:
    return ""
```

- `not s` est `True` si `s` est une chaîne **vide** (`""`). En Python, une
  chaîne vide est considérée comme « fausse » (*falsy*).
- Cas limite : si l'entrée est vide, on renvoie vide tout de suite. Ça
  évite des erreurs plus bas (par ex. `s[-1]` planterait sur une chaîne
  vide).

```python
result = []
count = 1
```

- `result` est une **liste** dans laquelle on accumule les morceaux du
  résultat. Pourquoi une liste et pas une chaîne ? Parce que faire
  `chaine += ...` en boucle est lent (chaque `+=` recrée une nouvelle
  chaîne). Accumuler dans une liste puis faire `"".join(...)` à la fin est
  la méthode **idiomatique et rapide** en Python.
- `count` compte combien de fois le caractère courant s'est répété. On
  commence à `1` car le premier caractère compte déjà pour un.

```python
for i in range(1, len(s)):
```

- On parcourt à partir de l'indice `1` (le **deuxième** caractère), pas `0`.
  Raison : à chaque étape on compare `s[i]` au caractère **précédent**
  `s[i - 1]`. Commencer à `1` garantit que `s[i - 1]` existe toujours
  (sinon `s[-1]` au tout début ferait n'importe quoi).

```python
if s[i] == s[i - 1]:
    count += 1
```

- Si le caractère courant est **identique** au précédent, c'est la même
  « plage » : on incrémente le compteur.

```python
else:
    result.append(s[i - 1])
    if count > 1:
        result.append(str(count))
    count = 1
```

- Sinon, c'est qu'on **change** de caractère. On doit donc « valider » la
  plage précédente :
  - on ajoute le caractère précédent (`s[i - 1]`) au résultat ;
  - **seulement si** `count > 1`, on ajoute aussi le nombre, converti en
    texte avec `str(count)` (car `result` contient des chaînes, pas des
    entiers). C'est ici qu'on applique la règle « on n'écrit pas le 1 ».
  - on remet `count = 1` pour démarrer le comptage du nouveau caractère.

```python
result.append(s[-1])
if count > 1:
    result.append(str(count))
```

- ⚠️ **Subtilité importante** : la boucle valide une plage seulement quand
  elle détecte un **changement** de caractère. Mais la **dernière** plage
  n'est jamais suivie d'un changement (la chaîne se termine). Il faut donc
  la traiter **après** la boucle, à la main.
- `s[-1]` est le dernier caractère. On l'ajoute, puis son compteur si
  besoin.

```python
return "".join(result)
```

- `"".join(result)` colle tous les morceaux de la liste bout à bout, sans
  séparateur (`""`). Par ex. `["a", "3", "b", "2", "c"]` → `"a3b2c"`.

### La fonction `decompress`

C'est l'opération inverse : à partir de `a3b2c`, reconstruire `aaabbc`.

```python
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

#### Pourquoi un `while` et pas un `for` ?

Parce qu'on avance dans la chaîne par **bonds irréguliers** : tantôt on lit
juste une lettre, tantôt une lettre **plus plusieurs chiffres**. On contrôle
donc l'indice `i` nous-mêmes, ce qui est plus simple avec un `while`.

#### Ligne par ligne

```python
char = s[i]
i += 1
```

- On lit le caractère courant (une lettre). On avance d'un cran.

```python
num = ""
while i < len(s) and s[i].isdigit():
    num += s[i]
    i += 1
```

- On accumule **tous les chiffres** qui suivent la lettre. Pourquoi une
  boucle ? Parce qu'un nombre peut avoir **plusieurs chiffres** : `a12`
  signifie 12 fois `a`. Si on ne lisait qu'un seul chiffre, on lirait `1`
  puis on croirait que `2` est une lettre.
- `s[i].isdigit()` renvoie `True` si le caractère est un chiffre (`0`–`9`).
- L'ordre du `and` est important : `i < len(s)` est testé **avant**
  `s[i].isdigit()`. Python évalue les conditions de gauche à droite et
  s'arrête dès que possible (*court-circuit*). Si `i` dépasse la longueur,
  on ne tente même pas `s[i]`, ce qui éviterait une erreur d'indice.

```python
count = int(num) if num else 1
```

- Si on a collecté des chiffres (`num` non vide), on les convertit en
  entier. Sinon (la lettre n'était suivie d'aucun chiffre, comme le `c` de
  `a3b2c`), le compte vaut `1`.
- C'est une **expression conditionnelle** (le « ternaire » Python) :
  `valeur_si_vrai if condition else valeur_si_faux`.

```python
result.append(char * count)
```

- `char * count` répète la chaîne : `"a" * 3` → `"aaa"`. On ajoute ce bloc
  au résultat.

```python
return "".join(result)
```

- Même technique que pour `compress` : on assemble tout à la fin.

### Cas limites à connaître

- Chaîne vide `""` : `compress` renvoie `""` grâce au test initial.
  `decompress("")` : le `while i < len(s)` est faux dès le départ, on
  renvoie `""`.
- Un caractère unique `"a"` : `compress` → `"a"` (pas de `1`).
- ⚠️ Limite **conceptuelle** du format : si la chaîne d'origine contient
  déjà des chiffres (par ex. `"a3"`), la compression devient ambiguë. Cet
  exercice suppose des entrées **sans chiffres**.

### Complexité

- `compress` et `decompress` sont en `O(n)` (un seul parcours de la chaîne).

---

## 3. `graph_cycle_detector.py`

### But

Détecter s'il existe un **cycle** dans un graphe **orienté** (*directed
graph*). Renvoie `True` s'il y a au moins un cycle, `False` sinon.

### Vocabulaire : c'est quoi un graphe ?

- Un **graphe** est un ensemble de **nœuds** (ou sommets) reliés par des
  **arêtes** (ou liens).
- **Orienté** veut dire que les liens ont un **sens** : `A → B` ne veut pas
  dire `B → A`. Pense à des flèches à sens unique.
- Un **cycle** est un chemin qui part d'un nœud et **revient** à ce même
  nœud en suivant les flèches. Ex : `A → B → C → A`.

### Représentation du graphe

```python
graph: dict[int, list[int]]
```

C'est un **dictionnaire** (liste d'adjacence) :

- la **clé** est un nœud (un entier) ;
- la **valeur** est la liste des nœuds vers lesquels il pointe.

Exemple :

```python
{
    0: [1, 2],   # 0 pointe vers 1 et 2
    1: [2],      # 1 pointe vers 2
    2: [0],      # 2 pointe vers 0  ← crée un cycle 0 → 2 → 0
}
```

### Le code complet

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

### L'idée centrale : deux ensembles

C'est l'algorithme classique de détection de cycle par **DFS** (*Depth-First
Search*, parcours en profondeur). La clé est de comprendre la différence
entre les **deux** `set` :

- **`visited`** : tous les nœuds qu'on a **déjà explorés un jour**, peu
  importe quand. Sert à ne pas refaire deux fois le même travail.
- **`rec_stack`** (*recursion stack*, pile de récursion) : les nœuds du
  **chemin courant**, c.-à-d. ceux qu'on est en train de visiter et qu'on
  n'a pas encore « fermés ». C'est la branche sur laquelle on est
  actuellement descendu.

**Détecter un cycle = retomber sur un nœud qui est encore dans `rec_stack`.**
Si en suivant les flèches on revient sur un nœud déjà présent dans le chemin
courant, c'est qu'on a bouclé.

> Pourquoi `visited` ne suffit-il pas ? Parce que dans un graphe orienté on
> peut atteindre un même nœud par **deux chemins différents** sans qu'il y
> ait de cycle (par ex. `A → B`, `A → C`, `B → D`, `C → D`). Le nœud `D` est
> visité deux fois, mais il n'y a aucun cycle. `rec_stack` permet de
> distinguer « déjà vu ailleurs » (OK) de « déjà sur mon chemin actuel »
> (cycle !).

### Ligne par ligne

```python
if not graph:
    return False
```

- Si le graphe est vide (dictionnaire vide), il ne peut pas y avoir de
  cycle. On renvoie `False`.

```python
visited = set()
rec_stack = set()
```

- On initialise les deux ensembles à vide.

#### La fonction interne `has_cycle`

```python
def has_cycle(node):
```

- C'est une fonction **imbriquée** (définie à l'intérieur de l'autre). Elle
  peut accéder à `visited`, `rec_stack` et `graph` du contexte englobant
  (notion de *closure* / fermeture). Pas besoin de les passer en paramètre.
- Elle est **récursive** : elle s'appelle elle-même pour explorer en
  profondeur.

```python
visited.add(node)
rec_stack.add(node)
```

- En entrant dans un nœud, on le marque comme visité **et** on l'ajoute au
  chemin courant.

```python
for neighbor in graph.get(node, []):
```

- On parcourt tous les voisins (les nœuds vers lesquels `node` pointe).
- `graph.get(node, [])` : récupère la liste des voisins. Le `[]` est une
  **valeur par défaut** : si `node` n'est pas une clé du dictionnaire (un
  nœud sans flèche sortante), on obtient une liste vide au lieu d'une
  erreur `KeyError`. C'est plus sûr que `graph[node]`.

```python
if neighbor not in visited:
    if has_cycle(neighbor):
        return True
```

- Si le voisin n'a **jamais** été visité, on l'explore récursivement. Si
  cette exploration trouve un cycle, on propage `True` vers le haut.

```python
elif neighbor in rec_stack:
    return True
```

- ⚠️ **Le cœur de la détection.** Si le voisin **a déjà été visité** (donc
  le `if` précédent est faux) **et** qu'il est encore dans `rec_stack`,
  c'est qu'il fait partie du chemin actuel → on vient de **boucler** →
  cycle trouvé.
- Note le `elif` : on n'arrive ici que si `neighbor in visited`. Et on teste
  alors s'il est dans `rec_stack`.

```python
rec_stack.remove(node)
return False
```

- Si on a fini d'explorer **tous** les voisins sans trouver de cycle, on
  « ferme » le nœud : on le retire de `rec_stack` (on n'est plus sur cette
  branche), mais on le **laisse** dans `visited` (on l'a bien exploré).
- On renvoie `False` : pas de cycle depuis ce nœud.
- ⚠️ Détail essentiel : on enlève de `rec_stack` mais **pas** de `visited`.
  C'est exactement ce qui distingue les deux ensembles.

#### La boucle externe

```python
for node in graph:
    if node not in visited:  # not in
        if has_cycle(node):
            return True
return False
```

- Pourquoi cette boucle ? Parce qu'un graphe peut être **déconnecté** :
  tous les nœuds ne sont pas forcément atteignables depuis un seul point de
  départ. On doit donc lancer un DFS depuis **chaque** nœud pas encore
  visité, pour être sûr de couvrir tout le graphe.
- `if node not in visited` : inutile de relancer un DFS sur un nœud déjà
  exploré par un parcours précédent.
- Si un quelconque DFS trouve un cycle, on renvoie `True`. Si on a tout
  parcouru sans rien trouver, `False`.
- (Le commentaire `# not in` dans le code source est juste une note du
  développeur, sans effet.)

### Déroulé d'exemple

Graphe `{0: [1], 1: [2], 2: [0]}` (cycle `0 → 1 → 2 → 0`) :

1. `has_cycle(0)` : `visited={0}`, `rec_stack={0}`. Voisin `1` non visité →
2. `has_cycle(1)` : `visited={0,1}`, `rec_stack={0,1}`. Voisin `2` non
   visité →
3. `has_cycle(2)` : `visited={0,1,2}`, `rec_stack={0,1,2}`. Voisin `0` →
   `0` est déjà visité **et** dans `rec_stack` → **`return True`** !
4. Le `True` remonte toute la chaîne → la fonction renvoie `True`.

### Complexité

- **Temps** : `O(V + E)` où `V` = nombre de nœuds, `E` = nombre d'arêtes.
  Chaque nœud et chaque arête sont visités une fois.
- **Espace** : `O(V)` pour les deux ensembles et la pile de récursion.

---

## 4. `schedule_meetings.py`

### But

Étant donné une liste de réunions (avec une heure de **début** et de **fin**),
trouver le **nombre minimum de salles** nécessaires pour que deux réunions
qui se chevauchent ne soient jamais dans la même salle. On renvoie aussi la
répartition des réunions par salle.

C'est un problème classique d'**affectation de salles** (*meeting rooms*).

### Format des données

```python
intervals: list[tuple[int, int]]
```

- Une liste de **tuples** `(début, fin)`. Un tuple est comme une liste mais
  **non modifiable** ; on s'en sert ici pour représenter un couple de
  valeurs fixes.
- Ex : `[(0, 30), (5, 10), (15, 20)]` = trois réunions.

Valeur de retour :

```python
-> tuple[int, list]
```

- Un tuple `(nombre_de_salles, liste_des_salles)`.

### Le code complet

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

### Ligne par ligne

```python
if not intervals:
    return 0, []
```

- Cas limite : aucune réunion → `0` salles et une liste vide.
- Note que `return 0, []` renvoie en fait le **tuple** `(0, [])` ; en
  Python les parenthèses du tuple sont optionnelles.

```python
intervals = sorted(intervals, key=lambda x: x[0])
```

- On **trie** les réunions par **heure de début** croissante. C'est l'étape
  cruciale de l'algorithme : on traite les réunions dans l'ordre où elles
  commencent.
- `sorted(...)` renvoie une **nouvelle** liste triée (ne modifie pas
  l'originale).
- `key=lambda x: x[0]` indique **selon quoi** trier. `lambda x: x[0]` est
  une mini-fonction anonyme qui, pour un tuple `x = (début, fin)`, renvoie
  `x[0]` (le début). Donc on trie sur le début.

```python
rooms = []
```

- `rooms` est la liste des salles. Chaque salle est elle-même une **liste**
  des réunions qui lui sont affectées. C'est donc une liste de listes de
  tuples.

```python
for start, end in intervals:
```

- On parcourt chaque réunion. `for start, end in ...` fait du **déballage de
  tuple** (*unpacking*) : pour chaque tuple `(a, b)`, `start` vaut `a` et
  `end` vaut `b` directement. Plus lisible que `interval[0]` / `interval[1]`.

```python
placed = False
```

- Drapeau (*flag*) : indique si on a réussi à caser la réunion courante dans
  une salle existante. Au départ, non.

```python
for room in rooms:
    if room[-1][1] <= start:
        room.append((start, end))
        placed = True
        break
```

- Pour chaque salle déjà ouverte, on regarde si la réunion peut y entrer.
- `room[-1]` est la **dernière** réunion ajoutée dans cette salle. Comme on
  traite les réunions par ordre de début croissant, la dernière ajoutée est
  aussi celle qui finit en dernier dans cette salle → il suffit de comparer
  à elle.
- `room[-1][1]` est donc la **fin** de la dernière réunion de la salle
  (`[1]` = deuxième élément du tuple = la fin).
- `room[-1][1] <= start` : si cette réunion se **termine avant** (ou
  pile au moment où) la nouvelle commence, alors il n'y a pas de
  chevauchement → la salle est libre, on peut y mettre la nouvelle réunion.
  - Le `<=` (et non `<`) signifie qu'une réunion qui finit à `10` et une qui
    commence à `10` peuvent partager la salle (la fin est exclusive).
- Si ça rentre : on `append` la réunion, on lève le drapeau `placed`, et on
  `break` (inutile de regarder les autres salles, on a trouvé).

```python
if not placed:
    rooms.append([(start, end)])
```

- Si **aucune** salle existante ne convenait, on **ouvre une nouvelle salle**
  contenant juste cette réunion : `[(start, end)]` est une liste avec un
  seul tuple.

```python
return len(rooms), rooms
```

- `len(rooms)` = nombre de salles utilisées = la réponse au problème.
- `rooms` = le détail de qui va où.

### Déroulé d'exemple

`intervals = [(0, 30), (5, 10), (15, 20)]`

Après tri (déjà trié ici) :

1. `(0, 30)` : aucune salle → on ouvre la **salle 1** → `[[(0,30)]]`
2. `(5, 10)` : salle 1 finit à `30`, et `30 <= 5` est **faux** → ne rentre
   pas → on ouvre la **salle 2** → `[[(0,30)], [(5,10)]]`
3. `(15, 20)` :
   - salle 1 finit à `30`, `30 <= 15` faux → non.
   - salle 2 finit à `10`, `10 <= 15` **vrai** → ça rentre ! On ajoute à la
     salle 2 → `[[(0,30)], [(5,10),(15,20)]]`

Résultat : `(2, [[(0,30)], [(5,10),(15,20)]])` → **2 salles** suffisent.

### ⚠️ Nuance importante sur l'optimalité

Cet algorithme (*first-fit* après tri par début) trouve toujours le **bon
nombre de salles** (le minimum). En effet, le nombre minimal de salles est
égal au nombre maximal de réunions qui se chevauchent à un instant donné, et
ce glouton l'atteint.

En revanche, la **répartition exacte** des réunions dans les salles peut
varier selon l'ordre de traitement : ce n'est pas forcément « la seule »
répartition possible, mais le **nombre** de salles, lui, est bien optimal.

### Complexité

- Tri : `O(n log n)`.
- Double boucle : dans le pire cas `O(n × k)` où `k` est le nombre de
  salles (au pire `n`), donc `O(n²)` au pire.
- **Espace** : `O(n)` pour stocker toutes les réunions réparties.

---

## Conclusion — les patterns à retenir

| Fichier                    | Technique clé                                              |
|----------------------------|------------------------------------------------------------|
| `Spiral_Matrix.py`         | 4 bornes qui rétrécissent + `range` à l'envers             |
| `compress_decompress.py`   | Accumuler dans une liste + `"".join`, traiter la fin à part |
| `graph_cycle_detector.py`  | DFS récursif avec `visited` **et** `rec_stack`             |
| `schedule_meetings.py`     | Trier par début + glouton *first-fit*                      |

Astuces transversales vues partout :
- Toujours traiter le **cas vide** au début.
- Accumuler dans une **liste** puis `join`, plutôt que concaténer des chaînes.
- `range(a, b)` exclut `b` → d'où les `+ 1` / `- 1`.
- Un `set` pour les tests d'appartenance rapides.
