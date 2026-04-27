# Fly-in : Explication complete du code

Ce fichier explique en detail chaque fichier, chaque classe, chaque methode et chaque choix de design du projet Fly-in.

---

## Table des matieres

1. [Vue d'ensemble du projet](#1-vue-densemble-du-projet)
2. [Structure des fichiers](#2-structure-des-fichiers)
3. [models/zone.py — Le modele de zone](#3-modelszonespy--le-modele-de-zone)
4. [models/connection.py — Le modele de connexion](#4-modelsconnectionpy--le-modele-de-connexion)
5. [models/drone.py — Le modele de drone](#5-modelsdronepy--le-modele-de-drone)
6. [models/network.py — Le graphe du reseau](#6-modelsnetworkpy--le-graphe-du-reseau)
7. [parser/map_parser.py — Le parseur de carte](#7-parsermap_parserpy--le-parseur-de-carte)
8. [engine/pathfinder.py — L'algorithme de routage](#8-enginepathfinderpy--lalgorithme-de-routage)
9. [engine/simulation.py — Le moteur de simulation](#9-enginesimulationpy--le-moteur-de-simulation)
10. [visual/terminal.py — L'affichage terminal](#10-visualterminalpy--laffichage-terminal)
11. [main.py — Le point d'entree](#11-mainpy--le-point-dentree)
12. [Makefile — L'automatisation](#12-makefile--lautomatisation)
13. [Le flux complet d'execution](#13-le-flux-complet-dexecution)
14. [Concepts algorithmiques cles](#14-concepts-algorithmiques-cles)

---

## 1. Vue d'ensemble du projet

Fly-in simule le routage de N drones d'une zone de depart vers une zone d'arrivee a travers un reseau de zones interconnectees. Le but est de minimiser le nombre total de tours necessaires.

Le programme fonctionne en 4 etapes :
1. **Parsing** : lire le fichier carte et construire le graphe
2. **Pathfinding** : trouver des chemins optimaux pour chaque drone
3. **Simulation** : executer le mouvement des drones tour par tour
4. **Affichage** : montrer les resultats en couleur dans le terminal

---

## 2. Structure des fichiers

```
fly-in/
├── main.py                  Point d'entree du programme
├── Makefile                 Commandes make (install, run, lint...)
├── requirements.txt         Dependances Python (flake8, mypy, pytest)
├── models/                  Les modeles de donnees (OOP)
│   ├── __init__.py
│   ├── zone.py              Zone = noeud du graphe
│   ├── connection.py        Connection = arete du graphe
│   ├── drone.py             Drone = entite qui se deplace
│   └── network.py           Network = le graphe complet
├── parser/                  Lecture des fichiers carte
│   ├── __init__.py
│   └── map_parser.py        Parse le format de carte specifique
├── engine/                  Logique de calcul
│   ├── __init__.py
│   ├── pathfinder.py        Algorithme Dijkstra + assignation
│   └── simulation.py        Moteur de simulation tour par tour
├── visual/                  Representation visuelle
│   ├── __init__.py
│   └── terminal.py          Affichage ANSI colore
└── maps/                    Fichiers carte de test
    ├── easy/
    ├── medium/
    ├── hard/
    └── challenger/
```

---

## 3. models/zone.py — Le modele de zone

### ZoneType (Enum)

Un enum qui definit les 4 types de zones possibles :

- `NORMAL` = "normal" : zone standard, cout de traversee = 1 tour
- `BLOCKED` = "blocked" : zone infranchissable, aucun drone ne peut entrer
- `RESTRICTED` = "restricted" : zone lente, cout = 2 tours (le drone passe 1 tour "en transit" sur la connexion avant d'arriver)
- `PRIORITY` = "priority" : zone preferee, cout = 1 tour mais poids 0 dans le pathfinding (Dijkstra la prefere)

### Zone (classe)

Represente un noeud dans le graphe du reseau.

**Attributs :**
- `name` (str) : identifiant unique de la zone (ex: "start", "waypoint1", "goal")
- `x`, `y` (int) : coordonnees pour la representation visuelle
- `zone_type` (ZoneType) : type de la zone
- `color` (Optional[str]) : couleur pour l'affichage (ex: "green", "red")
- `max_drones` (int) : capacite maximale de drones simultanes (defaut 1). Les zones start/end n'ont pas de limite en pratique.
- `is_start` (bool) : vrai si c'est la zone de depart
- `is_end` (bool) : vrai si c'est la zone d'arrivee

**Propriete `movement_cost`** :
Retourne le cout de mouvement :
- `RESTRICTED` → 2 (le drone met 2 tours pour traverser)
- `BLOCKED` → -1 (signal que c'est infranchissable)
- Tout le reste → 1

**Methodes `__eq__` et `__hash__`** :
Deux zones sont egales si elles ont le meme nom. Le hash est base sur le nom aussi. Ca permet d'utiliser des Zone dans des sets et comme cles de dict.

---

## 4. models/connection.py — Le modele de connexion

### Connection (classe)

Represente une arete bidirectionnelle entre deux zones.

**Attributs :**
- `zone1_name`, `zone2_name` (str) : les noms des deux zones connectees
- `max_link_capacity` (int) : nombre maximum de drones pouvant utiliser cette connexion simultanement dans un meme tour (defaut 1)

**Propriete `key`** :
Retourne une cle canonique pour la connexion. Les deux noms sont tries alphabetiquement puis joints par un tiret : `sorted(["B", "A"])` → `"A-B"`. Ca garantit que peu importe l'ordre dans lequel on specifie les zones, la cle est la meme. C'est utilise pour detecter les doublons et pour identifier les connexions en transit.

**Methode `other(zone_name)`** :
Retourne le nom de la zone de l'autre cote. Si tu passes "A", tu obtiens "B", et vice versa. Utile pour naviguer le graphe.

---

## 5. models/drone.py — Le modele de drone

### DroneState (Enum)

Les 4 etats possibles d'un drone :

- `WAITING` : le drone attend au depart, il n'a pas encore bouge
- `MOVING` : le drone est dans une zone et peut bouger au prochain tour
- `IN_TRANSIT` : le drone est en train de traverser une connexion vers une zone restricted (il arrivera au tour suivant)
- `DELIVERED` : le drone est arrive a la zone d'arrivee, il ne bouge plus

### Drone (classe)

Represente un drone individuel.

**Attributs :**
- `drone_id` (int) : numero unique (1, 2, 3...)
- `current_zone` (str) : nom de la zone ou le drone se trouve actuellement
- `state` (DroneState) : etat actuel
- `path` (list[str]) : le chemin pre-calcule a suivre (liste de noms de zones, sans le depart)
- `path_index` (int) : index actuel dans le chemin (a quel point du chemin le drone est rendu)
- `transit_target` (Optional[str]) : si IN_TRANSIT, le nom de la zone de destination
- `transit_connection` (Optional[str]) : si IN_TRANSIT, la cle de la connexion utilisee

**Propriete `label`** :
Retourne "D1", "D2", etc. C'est le format demande par le sujet.

**Propriete `next_zone`** :
Regarde `path[path_index]` pour savoir ou le drone doit aller ensuite. Retourne None si le drone a fini son chemin.

**Methode `advance()`** :
Incremente `path_index` de 1. Appele quand le drone arrive dans une zone (il passe a l'etape suivante de son chemin).

---

## 6. models/network.py — Le graphe du reseau

### Network (classe)

Le graphe complet qui contient toutes les zones et connexions.

**Attributs :**
- `nb_drones` (int) : nombre de drones a simuler
- `zones` (dict[str, Zone]) : toutes les zones indexees par nom
- `connections` (list[Connection]) : toutes les connexions
- `adjacency` (dict[str, list[Connection]]) : liste d'adjacence — pour chaque zone, la liste de ses connexions. C'est la structure cle pour naviguer le graphe efficacement.
- `start_zone`, `end_zone` (Optional[str]) : noms des zones de depart et d'arrivee

**Methode `add_zone(zone)`** :
Ajoute une zone au graphe. Met a jour le dict `zones`, initialise sa liste d'adjacence, et enregistre si c'est le start ou l'end.

**Methode `add_connection(conn)`** :
Ajoute une connexion. L'ajoute dans la liste `connections` ET dans la liste d'adjacence des deux zones connectees. La connexion apparait dans les deux listes d'adjacence car elle est bidirectionnelle.

**Methode `get_neighbors(zone_name)`** :
Retourne la liste des voisins d'une zone sous forme de tuples `(nom_voisin, connexion)`. Utilise la liste d'adjacence pour etre rapide (O(degre) au lieu de O(nb_connexions)).

**Methode `get_connection(zone1, zone2)`** :
Cherche la connexion entre deux zones specifiques. Parcourt la liste d'adjacence de zone1 et verifie si l'autre bout est zone2. Retourne None si pas de connexion directe.

---

## 7. parser/map_parser.py — Le parseur de carte

### ParseError (exception)

Exception custom qui inclut le numero de ligne. Le message est formate comme "Line 5: Zone name cannot contain dashes: 'my-zone'". Ca aide enormement au debug quand un fichier carte a une erreur.

### Fonctions privees

**`_parse_metadata(raw, line_num)`** :
Parse les metadonnees entre crochets. Format attendu : `[key1=value1 key2=value2]`.
- Verifie que ca commence par `[` et finit par `]`
- Split par espaces, puis chaque token par `=`
- Retourne un dict `{"key1": "value1", "key2": "value2"}`

Exemple : `[zone=restricted color=orange max_drones=3]` → `{"zone": "restricted", "color": "orange", "max_drones": "3"}`

**`_parse_zone_type(type_str, line_num)`** :
Convertit une string ("normal", "blocked", "restricted", "priority") en ZoneType enum. Leve une ParseError avec les valeurs valides si la string n'est pas reconnue.

**`_parse_zone_line(parts, line_num, is_start, is_end)`** :
Parse une ligne de definition de zone. Attend au minimum 3 elements : `<nom> <x> <y>`, plus optionnellement des metadonnees.

Validations :
- Le nom ne peut pas contenir de tirets (car les tirets sont utilises dans le format de sortie D1-zone et dans les cles de connexion)
- Les coordonnees doivent etre des entiers
- max_drones doit etre un entier positif
- Le type de zone doit etre valide

**`_parse_connection_line(parts, line_num)`** :
Parse une ligne de connexion. Format : `<zone1>-<zone2> [metadata]`.
Separe les deux noms de zones au premier tiret. Parse optionnellement `max_link_capacity` dans les metadonnees.

### Fonction principale : `parse_map(filepath)`

Lit le fichier ligne par ligne et construit le Network.

**Directives supportees :**
- `nb_drones: <N>` : nombre de drones
- `start_hub: <nom> <x> <y> [metadata]` : zone de depart
- `end_hub: <nom> <x> <y> [metadata]` : zone d'arrivee
- `hub: <nom> <x> <y> [metadata]` : zone intermediaire
- `connection: <zone1>-<zone2> [metadata]` : connexion

**Validations :**
- Les lignes vides et commentaires (commencant par #) sont ignores
- Pas de nom de zone en doublon
- Les zones d'une connexion doivent exister avant d'etre connectees
- Pas de connexion en doublon (verifie via la cle canonique)
- nb_drones, start_hub, et end_hub sont obligatoires
- Directive inconnue → erreur

---

## 8. engine/pathfinder.py — L'algorithme de routage

C'est le coeur algorithmique du projet. Le challenge est de trouver des chemins optimaux pour PLUSIEURS drones a travers un graphe avec des contraintes de capacite.

### Pathfinder (classe)

**Constructeur** :
Prend le Network et pre-calcule l'ensemble des zones bloquees (`_blocked`). Les zones bloquees sont exclues de tout pathfinding.

### Strategie : chemins node-disjoints via Dijkstra iteratif

Le probleme ressemble a un probleme de flot maximal, mais les contraintes de capacite s'appliquent PAR TOUR (pas globalement). Donc on ne peut pas utiliser un algorithme de flot classique. A la place, on cherche des chemins qui utilisent des noeuds differents pour maximiser le parallelisme.

**`_get_weight(zone_name)`** :
Retourne le poids d'une zone pour Dijkstra :
- `PRIORITY` → 0 (prefere, le chemin passera par la si possible)
- `RESTRICTED` → 2 (penalise, car ca coute 2 tours)
- Tout le reste → 1

**`_dijkstra(node_usage)`** :
Dijkstra classique avec une twist : il prend en compte combien de chemins passent deja par chaque noeud (`node_usage`).

Si un noeud intermediaire a deja ete utilise par autant de chemins que son `max_drones`, il est ignore. Ca force Dijkstra a trouver un chemin alternatif.

Implementation :
- File de priorite (heapq) avec `(distance, compteur, noeud)`
- Le compteur evite les comparaisons de strings quand les distances sont egales
- Reconstruction du chemin via le dict `prev` (chaque noeud pointe vers son predecesseur)
- Les zones start/end ne sont jamais saturees (pas de check de capacite)

**`_find_all_paths_bfs(max_paths=50)`** :
Boucle iterative qui appelle `_dijkstra` plusieurs fois :
1. Trouve le chemin le plus court
2. Marque les noeuds intermediaires comme "utilises" dans `node_usage`
3. Re-lance Dijkstra qui doit contourner les noeuds satures
4. Repete jusqu'a ce que Dijkstra ne trouve plus de chemin

Resultat : une liste de chemins aussi disjoints que possible. Exemple sur un graphe en fourche :
- Chemin 1 : start → A → B → end
- Chemin 2 : start → C → D → end
Les noeuds A et B sont marques, donc Dijkstra est force de trouver le chemin via C et D.

**`find_augmenting_paths()`** :
Simple wrapper qui appelle `_find_all_paths_bfs()`.

**`assign_drones()`** :
Distribue les N drones sur les chemins disponibles pour minimiser le temps total.

Algorithme glouton :
1. Calcule le cout de chaque chemin (somme des `movement_cost` des zones)
2. Pour chaque drone, trouve le chemin avec le plus petit "temps de fin estime"
3. Le temps de fin estime = cout_du_chemin + nb_drones_deja_sur_ce_chemin
4. Assigne le drone a ce chemin et incremente la charge

Pourquoi `+ nb_drones_deja_sur_ce_chemin` ? Parce que les drones sur le meme chemin doivent se suivre en pipeline. Avec des zones de capacite 1, un seul drone peut etre dans une zone a la fois. Donc le 2eme drone demarre 1 tour apres le 1er, le 3eme 2 tours apres, etc.

Exemple avec 2 chemins de cout 3 et 5, et 4 drones :
- Drone 1 → chemin 1 (cout 3+0=3)
- Drone 2 → chemin 2 (cout 5+0=5)
- Drone 3 → chemin 1 (cout 3+1=4)
- Drone 4 → chemin 1 (cout 3+2=5)

Le chemin retourne pour chaque drone exclut la zone de depart (on donne uniquement les zones a visiter).

---

## 9. engine/simulation.py — Le moteur de simulation

Le moteur execute le mouvement des drones tour par tour en respectant toutes les contraintes de capacite.

### Simulation (classe)

**Constructeur** :
Prend le Network et les chemins pre-calcules. Cree les objets Drone, chacun positionne a la zone de depart avec son chemin assigne.

**Attributs :**
- `drones` (list[Drone]) : tous les drones
- `turn_log` (list[str]) : les lignes de sortie de chaque tour
- `turn_delivered` (list[int]) : combien de drones sont arrives a chaque tour (pour la barre de progression)
- `total_turns` (int) : compteur total de tours

### Le cycle d'un tour

Chaque tour se deroule en 3 phases :

#### Phase 1 : `_plan_arrivals()`
Identifie les drones en etat IN_TRANSIT (qui etaient en train de traverser une connexion vers une zone restricted au tour precedent). Ces drones vont arriver a destination ce tour-ci.

Retourne une liste de `(index_drone, zone_destination)`.

#### Phase 2 : `_plan_departures(arrivals)`
Planifie les nouveaux deplacements pour les drones qui peuvent bouger.

C'est la partie la plus complexe. Le systeme doit :
1. Prendre en compte les arrivees qui vont liberer de la capacite
2. Verifier la capacite de la zone cible (occupants actuels + arrivees - departs)
3. Verifier la capacite de la connexion (drones en transit + nouveaux departs)
4. Ne pas envoyer un drone vers une zone bloquee
5. Gerer les zones restricted (cout 2 tours) differemment

**Tri par priorite :**
Les drones sont tries par longueur de chemin restant (du plus court au plus long). Ca donne la priorite aux drones qui sont presque arrives, evitant qu'un drone bloque un autre qui n'a plus qu'un pas a faire.

**Verification de capacite zone :**
```
net_occ = occupants_actuels + arrivees_ce_tour + departs_planifies_vers_cette_zone - departs_depuis_cette_zone
```
Si `net_occ >= max_drones`, le drone ne peut pas y aller (sauf si c'est la zone de fin).

**Verification de capacite connexion :**
`_link_usage()` compte les drones IN_TRANSIT sur cette connexion PLUS les departs deja planifies ce tour qui utilisent la meme connexion.

**Cas special restricted :**
Pour les zones restricted (movement_cost=2), le drone n'arrive pas dans le meme tour. Donc il ne compte pas dans les arrivees immédiates pour le calcul de capacite zone. Mais il va etre IN_TRANSIT sur la connexion, donc il compte dans l'usage de la connexion.

#### Phase 3 : `_execute_turn()`
Execute les mouvements planifies :

1. **Arrivees** : les drones IN_TRANSIT arrivent a destination
   - Met a jour `current_zone`, reset `transit_target` et `transit_connection`
   - Passe en etat MOVING
   - Avance dans le chemin (`advance()`)
   - Si la destination est la zone de fin → passe en DELIVERED

2. **Departs** : les nouveaux mouvements
   - Si la zone cible est restricted (movement_cost=2) :
     - Le drone passe en IN_TRANSIT
     - `transit_target` = zone destination
     - `transit_connection` = cle de la connexion
     - Il reste dans sa zone d'origine pour le calcul de sortie
     - Le mouvement affiche est `D<id>-<connexion>` (pas la zone)
   - Sinon (mouvement normal) :
     - Le drone se deplace directement dans la zone cible
     - Passe en etat MOVING, avance dans le chemin
     - Si c'est la zone de fin → DELIVERED

3. **Format de sortie** : les mouvements sont joints par des espaces
   - Mouvement normal : `D1-waypoint2`
   - Mouvement restricted : `D1-waypoint1-restricted_zone` (la connexion)

### `run()`

Boucle principale de la simulation :
- Maximum de `nb_drones * 200` tours (securite anti boucle infinie)
- A chaque tour, verifie si tous les drones sont DELIVERED → arret
- Execute un tour
- Si le resultat est None (aucun mouvement possible et pas tous delivered) → arret
- Enregistre le resultat dans `turn_log`
- Enregistre le nombre de drones delivered dans `turn_delivered`

---

## 10. visual/terminal.py — L'affichage terminal

### Constantes de couleur

`COLORS` est un dict qui mappe des noms de couleurs vers des codes ANSI escape :
- `"\033[92m"` = vert clair
- `"\033[91m"` = rouge
- `"\033[94m"` = bleu
- etc.

`RESET` (`"\033[0m"`) remet le terminal a sa couleur par defaut.
`BOLD` (`"\033[1m"`) et `DIM` (`"\033[2m"`) pour le gras et le grise.

### TerminalDisplay (classe)

**`_colorize(text, color)`** :
Entoure le texte avec le code ANSI de la couleur et le RESET. Si `visual` est False ou la couleur est None, retourne le texte tel quel.

**`_zone_type_symbol(zone_type)`** :
Retourne un symbole pour chaque type de zone :
- Normal → `o`
- Blocked → `X`
- Restricted → `~`
- Priority → `*`

**`print_header()`** :
Affiche le bandeau d'intro avec les stats du reseau (nb drones, zones, connexions, start, end). Chaque valeur est coloree.

**`print_network()`** :
Liste toutes les zones avec leur symbole, leur type (si non-normal), leur capacite (si != 1), et si c'est le START ou END. Chaque zone est affichee dans sa couleur configuree dans la carte.

**`print_paths(paths)`** :
Affiche les chemins calcules par le pathfinder. Chaque chemin est une fleche de zones : `start -> A -> B -> end`.

**`print_turn(turn_num, line, delivered, total)`** :
Affiche un tour de simulation avec :
- Le numero de tour (grise, format "Turn   1")
- Une barre de progression `[████░░░░░░░░]` verte/grise
- Le ratio `delivered/total`
- Les mouvements colores (label du drone en cyan, destination en jaune)

La barre de progression est calculee proportionnellement : `filled = bar_len * delivered / total`.

**`print_summary(total_turns, drones)`** :
Affiche le bilan final : nombre total de tours, ratio delivered, et status (ALL DRONES DELIVERED en vert ou INCOMPLETE en rouge).

**`print_raw_output(turns)`** :
Affiche la sortie brute demandee par le sujet : une ligne par tour, chaque ligne contient les mouvements separes par des espaces. Pas de couleur, pas de decoration.

---

## 11. main.py — Le point d'entree

Le flux est lineaire :

1. **Parse les arguments** : `sys.argv` pour le fichier carte et les flags `--visual` / `--raw`. Si aucun flag, les deux sont actifs par defaut.

2. **Parse la carte** : appelle `parse_map(map_file)`. Gere les erreurs ParseError et FileNotFoundError.

3. **Cree le display** : `TerminalDisplay(network, visual=has_visual)`

4. **Affiche les infos reseau** : header + topology (si visual)

5. **Calcule les chemins** : `Pathfinder(network)` puis `find_augmenting_paths()`. Si aucun chemin → erreur.

6. **Affiche les chemins** (si visual)

7. **Assigne les drones** : `pathfinder.assign_drones()` distribue les drones sur les chemins

8. **Lance la simulation** : `Simulation(network, drone_paths)` puis `sim.run()`

9. **Affiche les resultats** :
   - Si visual : affiche chaque tour avec barre de progression, puis le resume
   - Si raw : affiche les lignes brutes

---

## 12. Makefile — L'automatisation

| Commande | Action |
|----------|--------|
| `make install` | `pip install -r requirements.txt` |
| `make run` | Lance le programme avec la carte par defaut ou `MAP=...` |
| `make debug` | Lance avec pdb (debugger Python) |
| `make clean` | Supprime les `__pycache__` et caches mypy/pytest |
| `make lint` | flake8 + mypy avec checks de base |
| `make lint-strict` | flake8 + mypy --strict (le plus severe) |
| `make test` | Lance pytest (si des tests existent) |

La variable `MAP` peut etre surchargee : `make run MAP=maps/hard/01_maze_nightmare.txt`

---

## 13. Le flux complet d'execution

Voici ce qui se passe quand tu lances `python main.py maps/easy/02_simple_fork.txt` :

```
1. main.py lit le fichier
2. map_parser.py parse :
   - nb_drones: 4
   - start_hub: start 0 0
   - hub: path_a 1 0, hub: path_b 1 2, etc.
   - connection: start-path_a, start-path_b, etc.
   → Network avec 6 zones, 6 connexions, 4 drones

3. Pathfinder._find_all_paths_bfs() :
   - Dijkstra #1 : start → path_a → mid_a → end (cout 3)
   - Marque path_a et mid_a comme utilises
   - Dijkstra #2 : start → path_b → mid_b → end (cout 3)
   - Marque path_b et mid_b comme utilises
   - Dijkstra #3 : pas de chemin → stop
   → 2 chemins trouves

4. Pathfinder.assign_drones() :
   - Chemin 1 (cout 3), Chemin 2 (cout 3)
   - Drone 1 → chemin 1 (finish=3)
   - Drone 2 → chemin 2 (finish=3)
   - Drone 3 → chemin 1 (finish=4)
   - Drone 4 → chemin 2 (finish=4)

5. Simulation.run() :
   Tour 1: D1→path_a, D2→path_b                    (2 drones bougent)
   Tour 2: D1→mid_a, D2→mid_b, D3→path_a, D4→path_b (4 drones)
   Tour 3: D1→end✓, D2→end✓, D3→mid_a, D4→mid_b
   Tour 4: D3→end✓, D4→end✓
   → 4 tours au lieu de 7 si un seul chemin (pipeline 4 drones sur 3 etapes = 3+3=6)

6. Affichage des 4 tours avec barres de progression
```

---

## 14. Concepts algorithmiques cles

### Pourquoi Dijkstra et pas BFS ?

BFS traite toutes les aretes comme ayant le meme poids. Mais les zones restricted coutent 2 tours et les zones priority coutent 0 (preferees). Dijkstra avec des poids differents permet de trouver le chemin reellement le plus rapide.

### Pourquoi des chemins node-disjoints ?

Si 2 chemins partagent un noeud intermediaire de capacite 1, les drones ne peuvent pas passer simultanement. Ca revient a avoir un seul chemin au point de goulot. En forcant des chemins qui ne partagent pas de noeuds, on maximise le parallelisme.

### Pourquoi un tri par chemin restant dans la simulation ?

Imagine un croisement ou deux drones veulent entrer dans la meme zone de capacite 1. Le drone qui est plus proche de la fin (chemin restant plus court) est prioritaire. Ca evite les blocages ou un drone "presque arrive" est bloque par un drone qui a encore un long chemin devant lui.

### Pourquoi tracker arrivees ET departs dans le meme tour ?

Les mouvements sont simultanes. Au meme tour, un drone peut quitter une zone ET un autre peut y entrer. Si on ne prend pas en compte les departs, on pourrait refuser un mouvement alors que la place va se liberer. Le tracking bidirectionnel (arrivees - departs) permet une simulation correcte.

### Le pipeline de drones

Quand N drones prennent le meme chemin de cout C a travers des zones de capacite 1, le temps total est C + (N-1). Le premier drone arrive en C tours. Chaque drone suivant part 1 tour apres le precedent car la zone de capacite 1 ne se libere qu'apres le depart du drone precedent. C'est exactement comme un pipeline de processeur : le debit est 1 drone/tour apres le remplissage initial.

### La gestion des zones restricted

Les zones restricted prennent 2 tours :
- Tour T : le drone part de sa zone actuelle, passe en etat IN_TRANSIT. Le mouvement affiche est la connexion (pas la zone cible).
- Tour T+1 : le drone arrive dans la zone restricted. Le mouvement affiche est la zone cible.

Pendant qu'il est IN_TRANSIT, le drone occupe la connexion (compte dans link_usage) mais pas sa zone d'origine ni sa zone cible. Ca libere la zone d'origine pour qu'un autre drone puisse y entrer.
