# Guide de defense 42 - Pac-Man

Ce document est un support personnel pour preparer la defense du projet.
Il est volontairement long et pedagogique. L'objectif est de pouvoir expliquer
le projet a quelqu'un qui debute, mais aussi de repondre a des questions plus
techniques sur les algorithmes, l'architecture, les choix de fichiers et la
pipeline complete.

Le fichier est ajoute au `.gitignore`, donc il peut rester dans le dossier sans
etre pousse dans le depot Git.

---

## 1. Pitch tres court pour commencer la defense

Le projet est une recreation de Pac-Man en Python avec `pygame`.

Le joueur controle Pac-Man dans un labyrinthe genere automatiquement. Le but est
de manger toutes les pacgums, d'eviter les fantomes, et de passer les niveaux.
Les super-pacgums mettent les fantomes en mode effraye, ce qui permet de les
manger pour gagner des points bonus.

Le projet est decoupe en deux grandes parties:

- Le moteur du jeu, dans `pacman/game.py`, `pacman/entities/`, `pacman/scoring.py`,
  `pacman/maze_loader.py`, etc.
- L'interface graphique, dans `pacman/ui/`, qui utilise `pygame` pour dessiner
  la fenetre, le labyrinthe, Pac-Man, les fantomes, les menus et les ecrans.

Le point important a dire a l'oral:

> On a separe la logique du jeu de l'affichage. Le moteur ne depend pas de
> `pygame`; il calcule l'etat du jeu. L'UI lit un `GameState` et le dessine.

---

## Amelioration 2 - Fiche orale ultra courte, 5 minutes

Cette fiche sert si on te demande d'expliquer tout le projet rapidement. Le but
est de donner une reponse structuree, sans te perdre dans les details.

### Version 30 secondes

> C'est un Pac-Man en Python avec `pygame`. Le projet est separe entre moteur
> et affichage. Le moteur gere le labyrinthe, Pac-Man, les fantomes, les
> collisions, le score, les niveaux et les highscores. L'UI lit un `GameState`
> et le dessine. Les labyrinthes viennent de `mazegenerator`, puis sont
> convertis en grille jouable `(2W+1)x(2H+1)`. Les fantomes ont plusieurs
> comportements, et ceux qui poursuivent utilisent BFS pour trouver le plus
> court chemin dans la grille.

### Version 5 minutes

#### 0:00 - 0:45: ce que fait le jeu

> Le joueur controle Pac-Man avec les fleches ou WASD. Il doit manger toutes
> les pacgums du labyrinthe. Les fantomes se deplacent automatiquement. Si
> Pac-Man touche un fantome normal, il perd une vie. S'il mange une
> super-pacgum, les fantomes passent en mode effraye et Pac-Man peut les
> manger pour gagner des points bonus.

Code a citer:

- Point d'entree: `pac-man.py:176`.
- Creation du jeu quand on choisit Start Game: `pac-man.py:74` a `pac-man.py:80`.
- Boucle principale: `pac-man.py:67`.

#### 0:45 - 1:30: architecture

> Le projet est decoupe en deux parties. Le moteur ne depend pas de `pygame`:
> il calcule l'etat du jeu. L'UI utilise `pygame`: elle lit cet etat et le
> dessine. Cette separation rend le code plus testable, parce qu'on peut tester
> le moteur sans ouvrir de fenetre.

Code a citer:

- Moteur principal: `pacman/game.py:63`.
- Snapshot lu par l'UI: `pacman/game.py:46`.
- Rendu de ce snapshot: `pacman/ui/renderer.py:66`.
- Fenetre et clavier: `pacman/ui/window.py:27`.

#### 1:30 - 2:15: labyrinthe

> Le generateur externe ne donne pas directement une grille Pac-Man. Il donne
> des cellules avec des murs encodes en bits. On convertit donc ce format en
> une vraie grille de tiles. Une grille brute `W x H` devient une grille
> jouable `(2W+1) x (2H+1)`, ce qui permet d'avoir des murs reels entre les
> cellules.

Code a citer:

- Appel du generateur: `pacman/maze_loader.py:57`.
- Conversion en tiles: `pacman/maze_loader.py:84`.
- Placement super-pacgums: `pacman/maze_loader.py:135`.
- Spawn Pac-Man: `pacman/maze_loader.py:142`.
- Spawn fantomes: `pacman/maze_loader.py:150`.

#### 2:15 - 3:00: boucle de jeu

> A chaque frame, on lit le clavier, on calcule `dt`, on met a jour le moteur,
> puis on dessine. Dans `Game.update`, l'ordre est important: cheats, mouvement
> joueur, mouvement fantomes, pacgums, collisions, timer, fin de niveau.

Code a citer:

- Lecture input: `pacman/ui/window.py:47`.
- Update moteur: `pacman/game.py:288`.
- Mouvement joueur: `pacman/entities/player.py:87`.
- Mouvement fantome: `pacman/entities/ghost.py:256`.
- Pacgums: `pacman/game.py:176`.
- Collisions: `pacman/game.py:194`.

#### 3:00 - 4:00: IA des fantomes

> Les fantomes ont quatre comportements: chase, ambush, random et scatter. Pour
> trouver une direction vers une cible, on utilise BFS. BFS est adapte parce que
> la grille n'est pas ponderee: chaque deplacement coute 1. Donc BFS donne le
> plus court chemin simplement. A* ou Dijkstra auraient ete possibles, mais
> plus lourds pour ce besoin.

Code a citer:

- BFS: `pacman/entities/ghost.py:42`.
- Types de comportement: `pacman/entities/ghost.py:88`.
- Etats des fantomes: `pacman/entities/ghost.py:97`.
- Choix de direction: `pacman/entities/ghost.py:200`.
- Creation des 4 fantomes: `pacman/entities/ghost.py:331`.

#### 4:00 - 4:40: score, niveaux, highscores

> Le score est separe dans `Scoring`. Les pacgums donnent des points fixes, les
> super-pacgums aussi, et les fantomes donnent 200, 400, 800, 1600 grace a un
> multiplicateur. Les highscores sont sauvegardes en JSON, nettoyes et limites
> au top 10.

Code a citer:

- Scoring: `pacman/scoring.py:8`.
- Pacgum: `pacman/scoring.py:20`.
- Super-pacgum: `pacman/scoring.py:27`.
- Fantome mange: `pacman/scoring.py:37`.
- Highscores: `pacman/highscore.py:23`.
- Ajout score: `pacman/highscore.py:81`.

#### 4:40 - 5:00: robustesse et tests

> Le projet gere les erreurs de config, les fichiers highscores corrompus, les
> imports manquants et les cas de test principaux. Les tests automatises
> couvrent le moteur, les highscores et l'initialisation UI.

Code a citer:

- Config robuste: `pacman/config.py:183`.
- Validation config: `pacman/config.py:125`.
- Tests moteur: `tests/test_engine.py:23`.
- Tests UI/highscore: `tests/test_ui.py:13`.

### Phrase de conclusion

> Le point principal du projet, c'est que la logique du jeu est proprement
> separee du rendu. Le moteur calcule un etat coherent, l'UI le dessine, et les
> algorithmes choisis sont simples mais adaptes a Pac-Man: grille convertie,
> BFS pour les chemins, machines a etats pour le jeu et les fantomes.

---

## Amelioration 3 - Mapping sujet 42 -> code

Ce tableau sert a repondre vite a la question: "Ou est-ce que cette exigence est
faite dans le code ?"

| Attendu / point de defense | Fichier et ligne | Ce qu'il faut dire |
|---|---|---|
| Programme lance avec un fichier config JSON | `pac-man.py:176` | `main()` verifie les arguments et exige un `.json`. |
| Message d'erreur propre, pas traceback par defaut | `pac-man.py:15`, `pac-man.py:199` | `_log()` prefixe les erreurs; traceback seulement avec `--debug`. |
| Boucle principale du jeu | `pac-man.py:67` | Une boucle gere `dt`, events, etats, rendu. |
| Menu principal | `pacman/ui/menu.py:28` | `MainMenu` gere selection et affichage. |
| Etats menu/play/pause/gameover/highscores | `pac-man.py:58`, `pac-man.py:74`, `pac-man.py:95`, `pac-man.py:119` | `state` pilote l'application. |
| Fenetre graphique | `pacman/ui/window.py:27` | `GameWindow` encapsule `pygame`. |
| Lecture clavier | `pacman/ui/window.py:47`, `pacman/ui/window.py:62` | `get_input()` et `handle_events()` gerent les touches. |
| Labyrinthe genere par bibliotheque externe | `pacman/maze_loader.py:57` | `MazeGenerator` est appele avec taille, perfect et seed. |
| Fallback si le generateur echoue | `pacman/maze_loader.py:36`, `pacman/maze_loader.py:57` | `_fallback_maze()` permet au jeu de continuer. |
| Conversion en grille jouable | `pacman/maze_loader.py:84` | Le bitmask devient une grille de tiles `(2W+1)x(2H+1)`. |
| Murs et collisions | `pacman/entities/player.py:8`, `pacman/entities/ghost.py:11` | `_is_blocked()` empeche joueur et fantomes de traverser les murs. |
| Spawn Pac-Man | `pacman/maze_loader.py:142` | Le spawn est place au centre ou cellule ouverte proche. |
| Spawn fantomes | `pacman/maze_loader.py:150` | Les fantomes ont des positions de depart separees. |
| Pac-Man controlable | `pacman/entities/player.py:42`, `pacman/entities/player.py:79` | `Player` stocke position, direction et input buffer. |
| Mouvement fluide | `pacman/entities/player.py:70`, `pacman/entities/player.py:122` | `_move_progress` donne une interpolation visuelle. |
| Fantomes autonomes | `pacman/entities/ghost.py:105`, `pacman/entities/ghost.py:256` | Chaque fantome choisit et applique sa direction. |
| Plusieurs comportements de fantomes | `pacman/entities/ghost.py:88`, `pacman/entities/ghost.py:331` | Chase, ambush, random, scatter. |
| Plus court chemin | `pacman/entities/ghost.py:42` | BFS trouve le premier pas vers la cible. |
| Mode frightened | `pacman/entities/ghost.py:97`, `pacman/game.py:190` | Une super-pacgum passe les fantomes en `FRIGHTENED`. |
| Fantome mange | `pacman/game.py:204`, `pacman/game.py:208` | Collision avec fantome effraye ajoute des points et passe en `EATEN`. |
| Perte de vie | `pacman/entities/player.py:160`, `pacman/game.py:217` | Pac-Man perd une vie sur collision dangereuse. |
| Game over | `pacman/game.py:218` | Si plus de vies, mode `GAMEOVER`. |
| Score pacgums | `pacman/game.py:176`, `pacman/scoring.py:20` | Manger une pacgum modifie la grille et ajoute des points. |
| Score super-pacgums | `pacman/game.py:184`, `pacman/scoring.py:27` | Une super-pacgum donne des points et declenche frightened. |
| Bonus fantomes 200/400/800/1600 | `pacman/scoring.py:37` | Le multiplicateur double jusqu'a 8. |
| Passage niveau suivant | `pacman/game.py:258`, `pacman/game.py:372` | Quand toutes les pacgums sont mangees, `next_level()` est appele. |
| Temps limite par niveau | `pacman/game.py:73`, `pacman/game.py:360` | Le timer descend et relance le niveau a 0. |
| Highscores persistants | `pacman/highscore.py:23`, `pacman/highscore.py:66` | JSON charge/sauvegarde sans crash. |
| Top 10 highscores | `pacman/highscore.py:30`, `pacman/highscore.py:102` | Les scores sont tries et limites a 10. |
| Nom joueur valide | `pacman/highscore.py:108`, `pacman/ui/screens.py:72` | Nom nettoye, 10 caracteres max. |
| Cheat mode | `pacman/cheat.py:8`, `pacman/cheat.py:74`, `pac-man.py:104` | Touches `i`, `l`, `f`, `+`, `s`, `p`. |
| Overlay cheats | `pacman/ui/renderer.py:412` | Le renderer affiche les cheats actifs. |
| Pause | `pacman/ui/screens.py:39`, `pac-man.py:119` | `PauseScreen` gere resume/menu/quit. |
| Game over/victoire | `pacman/ui/screens.py:118`, `pac-man.py:112` | Ecran commun avec message different. |
| Instructions | `pacman/ui/screens.py:155`, `pac-man.py:156` | Ecran dedie aux controles. |
| Rendu du jeu | `pacman/ui/renderer.py:24`, `pacman/ui/renderer.py:66` | `Renderer` dessine toute la scene. |
| HUD score/vies/niveau/temps | `pacman/ui/renderer.py:292` | Le HUD est dessine en haut. |
| Tests moteur | `tests/test_engine.py:23` | Tests config, scoring, maze, joueur, fantomes, game. |
| Tests UI/highscore | `tests/test_ui.py:13` | Tests highscores et creation des classes UI. |
| Commandes projet | `Makefile:17`, `Makefile:22`, `Makefile:49` | `make install`, `make run`, `make test`. |
| Packaging executable | `pac-man.spec:1` | Spec PyInstaller pour construire `pac-man`. |

### Mapping par module

| Module | Responsabilite principale | Ligne de depart |
|---|---|---|
| `pac-man.py` | Orchestration application | `pac-man.py:29` |
| `pacman/config.py` | Config robuste | `pacman/config.py:11` |
| `pacman/maze_loader.py` | Generation et conversion maze | `pacman/maze_loader.py:57` |
| `pacman/game.py` | Moteur global | `pacman/game.py:63` |
| `pacman/entities/player.py` | Pac-Man | `pacman/entities/player.py:42` |
| `pacman/entities/ghost.py` | Fantomes et IA | `pacman/entities/ghost.py:105` |
| `pacman/scoring.py` | Points | `pacman/scoring.py:8` |
| `pacman/cheat.py` | Cheats | `pacman/cheat.py:8` |
| `pacman/highscore.py` | Scores persistants | `pacman/highscore.py:23` |
| `pacman/ui/window.py` | Fenetre et input | `pacman/ui/window.py:27` |
| `pacman/ui/renderer.py` | Dessin | `pacman/ui/renderer.py:24` |
| `pacman/ui/menu.py` | Menu | `pacman/ui/menu.py:28` |
| `pacman/ui/screens.py` | Ecrans secondaires | `pacman/ui/screens.py:39` |

---

## Amelioration 4 - References fichier/ligne pour reviser vite

Cette section sert d'index. Si quelqu'un te demande "montre-moi ou c'est fait",
tu peux ouvrir directement la ligne indiquee.

### Point d'entree et application

| Sujet | Reference | A expliquer |
|---|---|---|
| Fonction principale | `pac-man.py:176` | Lit les args, charge config, lance `_run`. |
| Chargement config | `pac-man.py:21` | Delegue a `parse_config`. |
| Initialisation jeu/UI | `pac-man.py:29` | Cree fenetre, renderer, menu, highscores. |
| Etat global app | `pac-man.py:58` | `state` choisit menu/play/pause/etc. |
| Boucle frame | `pac-man.py:67` | Tick, events, update, render, flip. |
| Passage en jeu | `pac-man.py:74` | Menu Start Game. |
| Cheats clavier | `pac-man.py:104` | Dispatch vers `CheatMode`. |
| Update + rendu | `pac-man.py:107`, `pac-man.py:109` | Moteur puis affichage. |

### Config

| Sujet | Reference | A expliquer |
|---|---|---|
| Defaults | `pacman/config.py:11` | Valeurs utilisees si config incomplete. |
| Commentaires `#` | `pacman/config.py:73` | Retire les lignes commentees avant JSON. |
| Entiers bornes | `pacman/config.py:84` | Convertit et clamp. |
| Floats bornes | `pacman/config.py:94` | Idem pour vitesses/timers. |
| Couleurs RGB | `pacman/config.py:109` | Verifie liste de 3 valeurs 0..255. |
| Validation globale | `pacman/config.py:125` | Merge defaults + valeurs utilisateur. |
| Parsing fichier | `pacman/config.py:183` | Lit JSON, gere erreurs, retourne config valide. |

### Maze

| Sujet | Reference | A expliquer |
|---|---|---|
| Constantes tiles | `pacman/maze_loader.py:16` | Noms normalises des cases. |
| Fallback maze | `pacman/maze_loader.py:36` | Maze simple si lib externe indisponible. |
| Appel MazeGenerator | `pacman/maze_loader.py:57` | Generation brute avec seed. |
| Conversion tiles | `pacman/maze_loader.py:84` | Passage bitmask -> grille jouable. |
| Super-pacgums | `pacman/maze_loader.py:135` | Placement aux coins jouables. |
| Spawn Pac-Man | `pacman/maze_loader.py:142` | Centre ou cellule ouverte proche. |
| Spawn ghosts | `pacman/maze_loader.py:150` | Un spawn par coin. |
| Cellule ouverte proche | `pacman/maze_loader.py:156` | Recherche par rayon croissant. |

### Moteur

| Sujet | Reference | A expliquer |
|---|---|---|
| Modes de jeu | `pacman/game.py:24` | PLAY, PAUSE, GAMEOVER, WIN. |
| Effet flottant | `pacman/game.py:34` | Texte `+200` temporaire. |
| Snapshot UI | `pacman/game.py:46` | `GameState` lu par le renderer. |
| Classe moteur | `pacman/game.py:63` | Etat complet de la partie. |
| Chargement niveau | `pacman/game.py:93` | Maze, spawns, joueur, fantomes. |
| Comptage pacgums | `pacman/game.py:153` | Sert a savoir quand le niveau finit. |
| Pickup pacgum | `pacman/game.py:176` | Points + remplacement par corridor. |
| Collisions | `pacman/game.py:194` | Fantome effraye, eaten, invincible, perte vie. |
| Effet `+points` | `pacman/game.py:229` | Ajoute un `FloatingEffect`. |
| Fin niveau | `pacman/game.py:255` | Passage niveau suivant ou victoire. |
| Snapshot final | `pacman/game.py:263` | Retourne `GameState`. |
| Update principal | `pacman/game.py:288` | Pipeline moteur complet. |
| Difficulte par niveau | `pacman/game.py:320` | Fantomes plus rapides par niveau. |
| Timer niveau | `pacman/game.py:360` | Restart si temps termine. |
| Niveau suivant | `pacman/game.py:372` | Nouvelle seed et reload. |

### Pac-Man

| Sujet | Reference | A expliquer |
|---|---|---|
| Collision mur | `pacman/entities/player.py:8` | Teste si une direction est bloquee. |
| Classe joueur | `pacman/entities/player.py:42` | Position, vies, direction, buffer. |
| Position visuelle | `pacman/entities/player.py:70` | Interpolation entre cases. |
| Buffer direction | `pacman/entities/player.py:79` | Memorise un virage demande. |
| Update joueur | `pacman/entities/player.py:87` | Applique input, vitesse, collision mur. |
| Vitesse joueur | `pacman/entities/player.py:118` | `player_speed` en cases/seconde. |
| Perte vie | `pacman/entities/player.py:160` | Decremente et signale game over. |
| Respawn joueur | `pacman/entities/player.py:166` | Reset position et mouvement. |

### Fantomes

| Sujet | Reference | A expliquer |
|---|---|---|
| Collision mur | `pacman/entities/ghost.py:11` | Meme logique que joueur. |
| BFS | `pacman/entities/ghost.py:42` | Plus court chemin en grille non ponderee. |
| Comportements | `pacman/entities/ghost.py:88` | Chase, ambush, random, scatter. |
| Etats | `pacman/entities/ghost.py:97` | Normal, frightened, eaten. |
| Classe fantome | `pacman/entities/ghost.py:105` | Position, comportement, etat, timers. |
| Changement etat | `pacman/entities/ghost.py:158` | Timer, demi-tour frightened. |
| Voisins possibles | `pacman/entities/ghost.py:175` | Evite reverse sauf cul-de-sac. |
| Choix direction | `pacman/entities/ghost.py:200` | Applique comportement et BFS. |
| Fuite frightened | `pacman/entities/ghost.py:212` | Max distance Manhattan. |
| Ambush | `pacman/entities/ghost.py:227` | Cible 4 cases devant Pac-Man. |
| Fallback distance | `pacman/entities/ghost.py:247` | Si BFS ne marche pas. |
| Update fantome | `pacman/entities/ghost.py:256` | Timer, vitesse, mouvement. |
| Vitesse frightened | `pacman/entities/ghost.py:281` | Ralentissement a 60%. |
| Respawn fantome | `pacman/entities/ghost.py:315` | Reset au spawn. |
| Creation des 4 fantomes | `pacman/entities/ghost.py:331` | Behaviors differents. |

### Score, cheats, highscores

| Sujet | Reference | A expliquer |
|---|---|---|
| Classe scoring | `pacman/scoring.py:8` | Stocke points et multiplicateur. |
| Pacgum | `pacman/scoring.py:20` | Ajoute points pacgum. |
| Super-pacgum | `pacman/scoring.py:27` | Ajoute points et reset chain. |
| Fantome | `pacman/scoring.py:37` | Points x multiplicateur. |
| Reset multiplicateur | `pacman/scoring.py:45` | Retour a 1. |
| Classe cheats | `pacman/cheat.py:8` | Etats cheat. |
| Power-up cheat | `pacman/cheat.py:55` | Demande consommee dans moteur. |
| Mapping touches cheats | `pacman/cheat.py:74` | `i`, `l`, `f`, `+`, `s`, `p`. |
| Skip consume | `pacman/cheat.py:89` | Skip applique une seule fois. |
| Classe highscores | `pacman/highscore.py:23` | Charge top 10. |
| Load highscores | `pacman/highscore.py:30` | Recovery sur erreur. |
| Save highscores | `pacman/highscore.py:66` | Ecriture JSON. |
| Add score | `pacman/highscore.py:81` | Trie et garde top 10. |
| Validation nom | `pacman/highscore.py:108` | Alnum/espace, 10 chars. |

### UI

| Sujet | Reference | A expliquer |
|---|---|---|
| Fenetre | `pacman/ui/window.py:27` | Init pygame, screen, clock. |
| Input | `pacman/ui/window.py:47` | Direction bufferisee ou touche maintenue. |
| Events | `pacman/ui/window.py:62` | QUIT, KEYDOWN, callbacks. |
| Clamp dt | `pacman/ui/window.py:98` | Evite les grands sauts apres freeze. |
| Renderer | `pacman/ui/renderer.py:24` | Objet qui dessine le jeu. |
| Rendu frame | `pacman/ui/renderer.py:66` | Grille, Pac-Man, fantomes, HUD. |
| Grille | `pacman/ui/renderer.py:123` | Murs caches + pacgums. |
| Pac-Man | `pacman/ui/renderer.py:168` | Polygone avec bouche animee. |
| Fantomes | `pacman/ui/renderer.py:267` | Sprites caches, frightened blink. |
| HUD | `pacman/ui/renderer.py:292` | Score, vies, niveau, temps. |
| Pause overlay | `pacman/ui/renderer.py:402` | Overlay graphique. |
| Cheat overlay | `pacman/ui/renderer.py:412` | Labels cheats actifs. |
| Flip | `pacman/ui/renderer.py:430` | Affiche la frame. |
| Menu | `pacman/ui/menu.py:28` | Items et selection. |
| Menu events | `pacman/ui/menu.py:52` | Navigation clavier. |
| Menu render | `pacman/ui/menu.py:76` | Dessin menu + highscores preview. |
| Pause screen | `pacman/ui/screens.py:39` | Resume/menu/quit. |
| Name entry | `pacman/ui/screens.py:72` | Saisie nom highscore. |
| Game over | `pacman/ui/screens.py:118` | Continue ou retour menu. |
| Instructions | `pacman/ui/screens.py:155` | Controles et regles. |
| Highscores screen | `pacman/ui/screens.py:192` | Affiche top 10. |

### Tests et outils

| Sujet | Reference | A expliquer |
|---|---|---|
| Tests config | `tests/test_engine.py:23` | Commentaires, defaults, JSON invalide. |
| Test scoring | `tests/test_engine.py:57` | 200/400/800/1600. |
| Test cheats | `tests/test_engine.py:73` | Toggles principaux. |
| Test maze | `tests/test_engine.py:86` | Conversion `7x7 -> 15x15`. |
| Test joueur mur | `tests/test_engine.py:101` | Pac-Man bloque par mur. |
| Test ghost chase | `tests/test_engine.py:113` | Un fantome bouge vers joueur. |
| Test game smoke | `tests/test_engine.py:135` | Update sans crash. |
| Test eaten ghost | `tests/test_engine.py:156` | Un fantome eaten ne tue pas. |
| Tests noms/highscores | `tests/test_ui.py:13` | Validation et persistence. |
| Test UI import | `tests/test_ui.py:51` | Classes UI constructibles. |
| Install | `Makefile:17` | Installe wheel + requirements. |
| Run | `Makefile:22` | Lance le jeu. |
| Test | `Makefile:49` | Pytest en SDL dummy. |
| Requirements | `requirements.txt:1` | Dependances principales. |
| Mypy config | `pyproject.toml:27` | Typage. |
| Pytest config | `pyproject.toml:35` | Dossier tests. |

---

## 2. Commandes importantes

Installer les dependances:

```bash
make install
```

Lancer le jeu:

```bash
make run
```

Equivalent direct:

```bash
python3 pac-man.py config.json
```

Lancer les tests:

```bash
make test
```

Verifier le style et le typage:

```bash
make lint
```

Nettoyer les caches:

```bash
make clean
```

Construire un executable avec PyInstaller:

```bash
pyinstaller pac-man.spec
```

---

## 3. Vocabulaire de base

### Moteur

Le moteur est la partie qui decide ce qui se passe dans le jeu:

- position de Pac-Man;
- position des fantomes;
- collisions;
- score;
- vies;
- temps restant;
- passage au niveau suivant;
- game over ou victoire.

Dans ce projet, le moteur est principalement dans:

- `pacman/game.py`
- `pacman/entities/player.py`
- `pacman/entities/ghost.py`
- `pacman/scoring.py`
- `pacman/maze_loader.py`
- `pacman/config.py`

### UI

L'UI est la partie visible:

- fenetre;
- menu;
- rendu du labyrinthe;
- dessin des sprites;
- HUD score/vies/temps;
- ecrans pause/game over/highscores/instructions.

Dans ce projet, l'UI est principalement dans:

- `pacman/ui/window.py`
- `pacman/ui/renderer.py`
- `pacman/ui/menu.py`
- `pacman/ui/screens.py`
- `pacman/ui/hud.py`

### GameState

`GameState` est une photo de l'etat du jeu a un instant donne.

Il contient par exemple:

- le score;
- les vies;
- le niveau;
- Pac-Man;
- les fantomes;
- la grille;
- le mode actuel du jeu.

L'UI ne modifie pas le moteur directement. Elle lit `GameState` et dessine.

### Tile

Une tile est une case de la grille affichee.

Exemples de tiles:

- `WALL`: mur;
- `CORRIDOR`: couloir vide;
- `PACGUM`: petite pastille;
- `SUPER_PACGUM`: grosse pastille;
- `SPAWN_PACMAN`: position de depart de Pac-Man;
- `SPAWN_GHOST`: position de depart d'un fantome.

### dt

`dt` signifie "delta time": le temps ecoule depuis la frame precedente.

Exemple: si le jeu tourne a 60 FPS, `dt` vaut environ `1 / 60`, donc environ
`0.016` seconde.

Utiliser `dt` permet d'avoir une vitesse stable meme si le nombre de frames
varie legerement.

---

## 4. Arborescence utile du projet

```text
.
├── pac-man.py
├── config.json
├── Makefile
├── requirements.txt
├── pyproject.toml
├── pac-man.spec
├── mazegenerator-2.0.2-py3-none-any.whl
├── pacman/
│   ├── __init__.py
│   ├── config.py
│   ├── maze_loader.py
│   ├── game.py
│   ├── scoring.py
│   ├── cheat.py
│   ├── highscore.py
│   ├── entities/
│   │   ├── player.py
│   │   └── ghost.py
│   └── ui/
│       ├── window.py
│       ├── renderer.py
│       ├── menu.py
│       ├── screens.py
│       └── hud.py
├── tests/
│   ├── test_engine.py
│   └── test_ui.py
└── project_management/
    ├── ACCEPTANCE_TESTS.md
    ├── CONFLICTS.md
    ├── GANTT.md
    ├── RISKS.md
    └── TEAM.md
```

---

## 5. Utilite de chaque fichier

| Fichier | Role simple |
|---|---|
| `pac-man.py` | Point d'entree. Il lance le jeu, gere les menus, les ecrans et la boucle globale. |
| `config.json` | Fichier de configuration: tailles, vitesses, couleurs, scores, nombre de vies. |
| `Makefile` | Raccourcis de commandes: installer, lancer, tester, nettoyer. |
| `requirements.txt` | Dependances Python a installer. |
| `pyproject.toml` | Metadonnees du projet, dependances et config de `mypy`/`pytest`. |
| `pac-man.spec` | Fichier PyInstaller pour creer un executable. |
| `mazegenerator-2.0.2-py3-none-any.whl` | Bibliotheque externe fournie pour generer les labyrinthes. |
| `pacman/config.py` | Lit et valide `config.json`. |
| `pacman/maze_loader.py` | Appelle `MazeGenerator` et convertit le labyrinthe en grille de tiles jouable. |
| `pacman/game.py` | Coeur du jeu: update, collisions, niveaux, score, etat global. |
| `pacman/scoring.py` | Calcule les points et le multiplicateur quand on mange des fantomes. |
| `pacman/cheat.py` | Gere les cheats: invincible, freeze, skip level, vitesse x2, +1 vie. |
| `pacman/highscore.py` | Charge, valide, trie et sauvegarde les meilleurs scores. |
| `pacman/entities/player.py` | Logique de Pac-Man: direction, mouvement, vies, respawn. |
| `pacman/entities/ghost.py` | Logique des fantomes: IA, BFS, etats normal/effraye/mange. |
| `pacman/ui/window.py` | Initialise `pygame`, gere la fenetre, le clavier et le temps. |
| `pacman/ui/renderer.py` | Dessine le jeu: murs, pacgums, Pac-Man, fantomes, HUD, overlays. |
| `pacman/ui/menu.py` | Menu principal. |
| `pacman/ui/screens.py` | Ecrans pause, game over, victoire, nom du joueur, instructions, highscores. |
| `pacman/ui/hud.py` | Ancien/mini wrapper pour dessiner une barre score/vies/temps. |
| `tests/test_engine.py` | Tests de la logique du moteur. |
| `tests/test_ui.py` | Tests non interactifs de l'UI et des highscores. |
| `project_management/*` | Documents de gestion projet pour la defense. |

---

## 6. Pipeline complete du programme

Cette section explique le trajet complet depuis la commande terminal jusqu'a
l'affichage d'une frame de jeu.

### 6.1 Lancement

Commande:

```bash
python3 pac-man.py config.json
```

Ce qui se passe:

1. Python execute `pac-man.py`.
2. La fonction `main()` lit les arguments.
3. Elle verifie qu'il y a exactement un argument.
4. Elle verifie que l'argument finit par `.json`.
5. Elle appelle `_load_config(config_path)`.
6. `_load_config()` appelle `parse_config()` dans `pacman/config.py`.
7. Si la config est valide, `main()` appelle `_run(config)`.
8. `_run()` initialise `pygame`, la fenetre, le renderer, le menu et les highscores.
9. La boucle principale commence.

### 6.2 Boucle principale

Dans `_run()`, il y a une boucle:

```python
while running:
```

A chaque tour:

1. `dt = window.tick()` calcule le temps ecoule.
2. `window.handle_events()` lit les evenements clavier/fenetre.
3. Selon `state`, le programme sait quoi faire:
   - `menu`;
   - `play`;
   - `pause`;
   - `gameover`;
   - `name_entry`;
   - `instructions`;
   - `highscores`.
4. La partie active traite les evenements.
5. Si on est en jeu, `game.update(dt, direction)` met a jour le moteur.
6. `game.get_state()` donne une photo du jeu.
7. `renderer.render_game(game_state, dt)` dessine la frame.
8. `renderer.flip()` affiche la frame a l'ecran.

### 6.3 Pipeline pendant une frame de jeu

Quand `state == "play"`:

1. On regarde si `ESC` est presse.
2. On regarde si une touche de cheat est presse (`i`, `l`, `f`, `+`, `s`, `p`).
3. On lit la direction clavier avec `window.get_input()`.
4. On appelle `game.update(dt, direction)`.
5. Dans `Game.update()`:
   - on applique les cheats;
   - on gere les demandes speciales comme skip level ou power-up;
   - on met a jour Pac-Man;
   - on met a jour les fantomes;
   - on mange les pacgums;
   - on verifie les collisions;
   - on met a jour les effets visuels;
   - on diminue le temps;
   - on regarde si le niveau est termine.
6. On recupere un `GameState`.
7. Le renderer dessine:
   - fond;
   - grille;
   - Pac-Man;
   - fantomes;
   - HUD;
   - barre de frightened mode;
   - effets flottants;
   - overlay READY si besoin;
   - overlay cheats si besoin.
8. `pygame.display.flip()` montre le resultat.

### 6.4 Pipeline moteur

```text
input clavier
    ↓
GameWindow.get_input()
    ↓
Game.update(dt, direction)
    ↓
Player.update()
    ↓
Ghost.update() pour chaque fantome
    ↓
pickup pacgum / super-pacgum
    ↓
collisions
    ↓
score / vies / niveau / game over
    ↓
GameState
    ↓
Renderer.render_game()
```

### 6.5 Pipeline affichage

```text
GameState
    ↓
Renderer.render_game()
    ↓
render_grid()
    ↓
render_pacman()
    ↓
render_ghosts()
    ↓
render_hud()
    ↓
render overlays
    ↓
pygame.display.flip()
```

---

## 7. Bibliotheques utilisees

### `pygame`

`pygame` est utilise pour:

- creer la fenetre;
- lire le clavier;
- gerer le temps avec `Clock`;
- dessiner des rectangles, cercles, polygones;
- afficher du texte;
- rafraichir l'ecran.

Pourquoi `pygame`?

- C'est simple pour un jeu 2D.
- C'est tres connu en Python.
- Il permet de dessiner sans moteur lourd.
- Il est suffisant pour Pac-Man.

### `mazegenerator`

La bibliotheque `mazegenerator` genere un labyrinthe.

Elle renvoie une grille d'entiers. Chaque entier est un bitmask qui indique
quels murs existent autour d'une cellule.

Bitmask utilise:

| Bit | Valeur | Mur |
|---|---:|---|
| bit 0 | `1` | nord |
| bit 1 | `2` | est |
| bit 2 | `4` | sud |
| bit 3 | `8` | ouest |

Exemple:

- `0`: aucun mur;
- `1`: mur au nord;
- `2`: mur a l'est;
- `4`: mur au sud;
- `8`: mur a l'ouest;
- `15`: tous les murs (`1 + 2 + 4 + 8`).

Dans ce projet, `15` est aussi traite comme une decoration speciale `WALL_42`.

### `json`

Utilise pour:

- lire `config.json`;
- lire et sauvegarder les highscores.

Pourquoi JSON?

- Lisible par humain;
- simple a modifier;
- inclus dans Python;
- parfait pour une petite config et un top 10.

### `pathlib.Path`

Utilise pour manipuler les chemins de fichiers proprement.

Exemple:

```python
path = Path(filepath)
path.exists()
path.read_text(encoding="utf-8")
```

### `dataclasses`

Utilise dans `pacman/game.py` pour `FloatingEffect` et `GameState`.

Une dataclass evite d'ecrire beaucoup de code repetitif pour stocker des
donnees.

### `Enum`

Utilise pour:

- `GameMode`;
- `GhostBehavior`;
- `GhostState`;
- `MenuItem`.

Pourquoi `Enum`?

Parce que c'est plus clair et moins fragile que des chaines de caracteres
dispersees partout.

### `random`

Utilise pour:

- generer les seeds des niveaux suivants;
- donner un comportement aleatoire a certains fantomes;
- rendre le frightened mode un peu moins previsible.

### `collections.deque`

Utilise pour BFS dans `ghost.py`.

`deque` est une file efficace:

- on ajoute a droite;
- on retire a gauche;
- c'est parfait pour BFS.

### `math`

Utilise pour:

- animer la bouche de Pac-Man avec `sin`;
- faire clignoter les super-pacgums;
- calculer les points d'un polygone circulaire.

### `pytest`

Utilise pour les tests.

### `flake8`

Utilise pour verifier le style Python.

### `mypy`

Utilise pour verifier les types.

### `pyinstaller`

Utilise pour creer un executable autonome.

---

## 8. Pourquoi cette architecture?

### 8.1 Separation moteur / UI

Le moteur ne doit pas dependre de `pygame`.

Avantages:

- les tests du moteur sont plus simples;
- on peut comprendre la logique sans regarder l'affichage;
- l'UI peut etre modifiee sans casser les regles du jeu;
- le moteur expose un `GameState` propre.

Si l'UI modifiait directement les objets partout, le projet deviendrait plus
difficile a deboguer.

### 8.2 Point d'entree unique

`pac-man.py` est le chef d'orchestre.

Il ne contient pas toute la logique du jeu. Il relie les modules:

- config;
- fenetre;
- menu;
- jeu;
- renderer;
- highscores;
- ecrans.

C'est une bonne separation: chaque fichier garde un role clair.

### 8.3 `GameState` comme contrat

Le moteur dit:

> Voici l'etat actuel du jeu.

L'UI repond:

> Je vais le dessiner.

Cette separation evite que le renderer change accidentellement le score, les
vies ou la position des entites.

### 8.4 Machines a etats

Le projet utilise plusieurs machines a etats.

#### Etat global dans `pac-man.py`

Valeurs:

- `menu`;
- `play`;
- `pause`;
- `gameover`;
- `name_entry`;
- `instructions`;
- `highscores`.

Chaque etat a son propre comportement.

#### Etat du jeu dans `GameMode`

Valeurs:

- `PLAY`;
- `PAUSE`;
- `GAMEOVER`;
- `WIN`.

#### Etat des fantomes dans `GhostState`

Valeurs:

- `NORMAL`;
- `FRIGHTENED`;
- `EATEN`.

Une machine a etats est utile quand un objet peut etre dans plusieurs modes
clairs, et que les regles changent selon le mode.

---

## 9. Algorithmes et choix techniques

## 9.1 Generation du labyrinthe

Le package `mazegenerator` renvoie une grille de cellules.

Probleme: une cellule de labyrinthe n'est pas directement une tile Pac-Man.

Si on affichait une cellule = une case, on ne pourrait pas representer les murs
entre deux cellules correctement.

Solution:

```text
grille brute: W x H cellules
grille jouable: (2W + 1) x (2H + 1) tiles
```

Exemple pour une cellule `(cx, cy)`:

```text
cellule (cx, cy) -> tile (2cx + 1, 2cy + 1)
```

Pourquoi `+1`?

Parce que la ligne 0 et la colonne 0 servent de bordure de murs.

### Exemple visuel

Une grille brute 2x2 devient une grille jouable 5x5:

```text
#####
#.#.#
#####
#.#.#
#####
```

Ensuite, si deux cellules sont connectees, le mur entre elles devient un couloir.

### Pourquoi pas utiliser directement la grille du generateur?

Parce que le generateur encode les murs avec des bits dans chaque cellule.
Pac-Man, lui, a besoin de savoir si la case suivante est un mur ou un couloir.

La conversion rend les collisions beaucoup plus simples.

---

## 9.2 Detection des murs

La fonction `_is_blocked()` existe dans `player.py` et `ghost.py`.

Elle repond a une question simple:

> Si je suis en `(x, y)` et que je veux aller dans la direction `(dx, dy)`,
> est-ce bloque?

Elle gere deux formats:

- une grille de strings (`WALL`, `PACGUM`, etc.);
- une grille de bitmasks entiers, utile pour rester compatible avec le format
  du generateur.

Pourquoi garder les deux?

Parce que les tests et certains cas peuvent manipuler directement une grille
simple, et le code reste robuste si on lui donne des entiers.

---

## 9.3 Mouvement par interpolation

Pac-Man et les fantomes ont:

- une position logique entiere: `(x, y)`;
- une progression visuelle: `_move_progress`;
- une position visuelle flottante: `visual_pos`.

La position logique dit:

> Je suis sur la case `(5, 7)`.

La progression dit:

> Je suis a 40% du trajet vers la prochaine case.

La position visuelle dit:

> Pour dessiner, utilise `(5.4, 7.0)`.

Pourquoi faire ca?

Sans interpolation, Pac-Man sauterait de case en case. Avec interpolation, il
glisse visuellement entre les cases, ce qui rend le mouvement fluide.

---

## 9.4 Direction buffer

Dans Pac-Man, le joueur appuie souvent un peu avant l'intersection.

Exemple:

- Pac-Man va a droite.
- Le joueur appuie sur haut avant d'arriver au croisement.
- Le jeu garde cette direction en memoire.
- Des que la case du haut est possible, Pac-Man tourne.

Dans `Player`, ce mecanisme est fait avec:

- `buffered_x`;
- `buffered_y`.

Pourquoi c'est important?

Parce que ca rend le controle plus agreable et plus proche du vrai Pac-Man.

---

## 9.5 BFS pour les fantomes

BFS signifie Breadth-First Search, ou parcours en largeur.

Il sert ici a trouver le premier pas du plus court chemin entre un fantome et
une cible.

Dans `ghost.py`, la fonction importante est:

```python
_bfs_next_step(grid, start, target, forbid=None)
```

Elle renvoie une direction:

- `(1, 0)` pour droite;
- `(-1, 0)` pour gauche;
- `(0, 1)` pour bas;
- `(0, -1)` pour haut;
- `None` si aucun chemin n'existe.

### Pourquoi BFS?

Le labyrinthe est une grille non ponderee:

- chaque deplacement coute 1;
- aller a droite, gauche, haut ou bas a le meme cout.

Dans une grille non ponderee, BFS donne le plus court chemin.

### Complexite

Si `V` est le nombre de cases et `E` le nombre de connexions:

```text
BFS = O(V + E)
```

Dans une grille, c'est acceptable, car le labyrinthe est petit.

### Pourquoi pas Dijkstra?

Dijkstra sert quand les deplacements ont des couts differents.

Ici, toutes les cases coutent pareil. Dijkstra marcherait, mais serait plus
lourd que necessaire.

### Pourquoi pas A*?

A* est tres utile avec une heuristique, par exemple la distance de Manhattan.

Mais pour ce projet:

- la grille est petite;
- BFS est plus simple a expliquer;
- BFS garantit le plus court chemin sans heuristique;
- BFS suffit largement.

A* aurait ete possible, mais pas necessaire.

### Pourquoi pas DFS?

DFS explore en profondeur. Il peut trouver un chemin, mais pas forcement le plus
court.

Pour un fantome qui poursuit Pac-Man, on veut un deplacement coherent, donc BFS
est meilleur.

### Pourquoi pas uniquement greedy?

Un choix greedy prend la case qui semble la plus proche de la cible.

Probleme: dans un labyrinthe, une case qui semble proche peut mener a un mur ou
a un cul-de-sac.

BFS voit les vrais chemins disponibles.

---

## 9.6 Regle "no reverse" des fantomes

Dans Pac-Man classique, les fantomes ne font pas demi-tour n'importe quand.
Ils continuent dans leur direction sauf:

- s'ils sont bloques;
- s'ils changent d'etat;
- s'il n'y a pas d'autre choix.

Dans ce projet, `_neighbors()` retire la direction inverse quand c'est possible.

Exemple:

- le fantome va a droite `(1, 0)`;
- la direction inverse est gauche `(-1, 0)`;
- si d'autres chemins existent, gauche est evitee.

Pourquoi?

Ca donne un mouvement plus naturel et moins chaotique.

---

## 9.7 Comportements des fantomes

Il y a quatre comportements:

| Comportement | Idee |
|---|---|
| `CHASE` | viser directement Pac-Man |
| `AMBUSH` | viser quelques cases devant Pac-Man |
| `RANDOM` | choisir une direction aleatoire |
| `SCATTER` | viser un coin du labyrinthe |

### `CHASE`

Le fantome cible la position exacte de Pac-Man.

Simple a expliquer:

> Il poursuit le joueur.

### `AMBUSH`

Le fantome vise 4 cases devant Pac-Man.

But:

> Ne pas aller sur Pac-Man, mais essayer de l'intercepter.

### `RANDOM`

Le fantome choisit une direction ouverte au hasard.

But:

> Ajouter de l'imprevisibilite.

### `SCATTER`

Le fantome vise un coin attribue.

But:

> Reproduire l'idee de Pac-Man classique ou certains fantomes repartent vers
> leur zone.

---

## 9.8 Etat frightened

Quand Pac-Man mange une super-pacgum:

1. Tous les fantomes passent en `FRIGHTENED`.
2. Ils ralentissent.
3. Ils essaient de s'eloigner du joueur.
4. Pac-Man peut les manger.

Dans le code:

- `GhostState.FRIGHTENED`;
- timer `_state_timer`;
- vitesse multipliee par `0.6`;
- couleur bleue/clignotante dans le renderer;
- scoring bonus.

L'algorithme de fuite:

- calculer les voisins possibles;
- choisir majoritairement celui qui maximise la distance de Manhattan avec
  Pac-Man;
- garder un petit hasard pour eviter un comportement trop mecanique.

Distance de Manhattan:

```text
abs(x1 - x2) + abs(y1 - y2)
```

Pourquoi Manhattan?

Parce qu'on bouge sur une grille en haut/bas/gauche/droite, pas en diagonale.

---

## 9.9 Etat eaten

Quand Pac-Man mange un fantome frightened:

1. Le joueur gagne des points.
2. Le fantome passe en `EATEN`.
3. Il ne tue plus Pac-Man.
4. Apres un delai, il respawn.

Dans ce projet, un fantome `EATEN` ne bouge pas visuellement vers la base; il
attend son timer puis respawn.

C'est une simplification acceptable a expliquer honnetement:

> On a implemente l'etat mange et le respawn avec timer; on n'a pas implemente
> le retour anime des yeux a la maison des fantomes.

---

## 9.10 Scoring

Le scoring est dans `pacman/scoring.py`.

Regles:

- pacgum: `points_per_pacgum`;
- super-pacgum: `points_per_super_pacgum`;
- fantome: `points_per_ghost * ghost_multiplier`;
- le multiplicateur de fantome fait `1 -> 2 -> 4 -> 8`;
- il se reset apres la fin de la chaine.

Avec la config par defaut:

```text
fantome 1 = 200
fantome 2 = 400
fantome 3 = 800
fantome 4 = 1600
```

Pourquoi cette logique?

Elle reproduit l'esprit de Pac-Man: manger plusieurs fantomes pendant le meme
power-up donne de plus en plus de points.

---

## 9.11 Validation de config

`config.py` ne fait pas confiance au fichier JSON.

Il gere:

- fichier manquant;
- JSON invalide;
- mauvaise racine JSON;
- cle manquante;
- cle inconnue;
- mauvaise couleur;
- nombre trop petit ou trop grand.

Pourquoi?

Parce qu'un projet robuste ne doit pas crasher juste parce qu'une config est
mal ecrite.

---

## 9.12 Highscores robustes

`highscore.py` protege contre:

- fichier absent;
- JSON corrompu;
- mauvais format;
- score negatif;
- nom invalide;
- trop d'entrees.

Il garde seulement le top 10.

Pourquoi?

Parce qu'un fichier de score est facilement modifiable ou corruptible. Le jeu
doit continuer a fonctionner.

---

## 9.13 Cache de rendu

Dans `renderer.py`, les murs sont pre-rendus dans `_wall_cache`.

Pourquoi?

Les murs ne changent presque jamais pendant un niveau.

Donc au lieu de redessiner chaque mur a chaque frame:

1. on dessine une surface de murs une fois;
2. on la reutilise avec `blit`;
3. on redessine seulement les elements qui changent.

C'est une optimisation simple.

---

## 9.14 Clamp du `dt`

Dans `GameWindow.tick()`:

```python
return min(self.clock.tick(self.fps) / 1000.0, 1.0 / 30.0)
```

Ca evite qu'un gros freeze provoque un enorme mouvement d'un coup.

Exemple:

- la fenetre freeze 2 secondes;
- sans clamp, `dt = 2.0`;
- Pac-Man pourrait traverser beaucoup de cases d'un coup.

Avec le clamp:

- `dt` maximum vaut `1/30`;
- le jeu reste stable.

---

## 10. Lecture detaillee du code

Cette partie explique les fichiers dans l'ordre. Pour rester lisible, elle
explique les lignes et blocs dans l'ordre exact du code, avec le sens de chaque
instruction importante.

---

# 10.1 `pac-man.py`

## Role du fichier

`pac-man.py` est le point d'entree du programme.

Il fait trois choses:

1. verifier les arguments;
2. charger la config;
3. lancer la boucle principale avec menus, jeu, pause et highscores.

Il est volontairement au niveau "orchestrateur": il connecte les modules sans
mettre toute la logique dedans.

## Lecture dans l'ordre

`#!/usr/bin/env python3`

Cette ligne est le shebang. Sur Unix/Linux/macOS, elle indique que le fichier
doit etre execute avec `python3`.

Docstring du haut:

Elle explique que ce fichier est le point d'entree et montre l'utilisation:

```text
python3 pac-man.py [config.json]
```

`from __future__ import annotations`

Permet de reporter l'evaluation des annotations de type. C'est pratique pour
eviter certains problemes de references circulaires et rendre les types plus
souples.

Imports:

- `sys`: lire les arguments et sortir avec un code d'erreur;
- `traceback`: afficher la stack trace seulement en mode debug;
- `Any`, `Dict`, `Optional`: annotations de type.

### `_log(message)`

Cette fonction affiche un message d'erreur clair sur `stderr`.

Pourquoi `stderr`?

Parce que les erreurs et logs doivent aller dans la sortie d'erreur, pas dans
la sortie standard.

Format:

```text
[pac-man] message
```

Le prefixe aide a savoir d'ou vient l'erreur.

### `_load_config(path)`

Cette fonction importe `parse_config` depuis `pacman.config`.

Pourquoi importer ici et pas tout en haut?

Ca garde le point d'entree leger au demarrage et permet de mieux isoler les
erreurs.

Elle retourne le dictionnaire de config valide.

### `_run(config)`

C'est la fonction qui lance vraiment le jeu.

Elle importe `pygame` et tous les composants necessaires:

- `Game`;
- `GameMode`;
- `HighscoreManager`;
- `MainMenu`;
- `MenuItem`;
- `Renderer`;
- les ecrans;
- `GameWindow`.

Elle cree ensuite:

- `window`: la fenetre pygame;
- `renderer`: l'objet qui dessine le jeu;
- `menu`: menu principal;
- `highscores`: gestionnaire du top 10;
- `instructions`: ecran d'instructions;
- `scores_screen`: ecran des highscores.

Variables importantes:

- `state`: etat global de l'application;
- `game`: instance de `Game` ou `None`;
- `pause_screen`: ecran de pause;
- `game_over`: ecran de fin;
- `name_entry`: ecran pour entrer le nom;
- `running`: controle la boucle principale.

### Boucle `while running`

A chaque iteration:

- `dt = window.tick()` calcule le temps ecoule;
- `window.handle_events()` recupere les evenements;
- si la fenetre est fermee, `running` passe a `False`;
- `events = window.events` stocke les evenements de cette frame.

### Etat `menu`

Le menu lit les evenements avec `menu.handle_event(event)`.

Si le choix est:

- `START_GAME`: on cree `Game(config)` et on passe a `play`;
- `HIGHSCORES`: on cree un ecran highscores a jour;
- `INSTRUCTIONS`: on affiche les instructions;
- `EXIT`: on quitte.

Ensuite `menu.render()` dessine le menu.

### Etat `play`

Si le jeu existe:

- `ESC` cree un `PauseScreen` et passe a `pause`;
- les touches `i`, `l`, `f`, `+`, `s`, `p` declenchent les cheats;
- `window.get_input()` lit la direction;
- `game.update(dt, direction)` met a jour le moteur;
- `game.get_state()` recupere l'etat;
- `renderer.render_game()` dessine;
- `renderer.render_cheat_overlay()` affiche les cheats actifs;
- si le mode devient `GAMEOVER` ou `WIN`, on cree `GameOverScreen`.

### Etat `pause`

On transmet les evenements a `pause_screen.handle_event()`.

Actions possibles:

- `"resume"`: retour au jeu;
- `"menu"`: abandon de la partie et retour menu;
- `"quit"`: quitter l'application.

Le jeu est dessine en arriere-plan avec `renderer.render_game(game.get_state(), 0.0)`,
puis le menu pause est dessine au-dessus.

### Etat `gameover`

L'ecran de fin attend:

- `continue`: si le score est positif, on passe a l'ecran de saisie de nom;
- `menu`: retour menu.

### Etat `name_entry`

Le joueur tape son nom.

Quand `handle_event()` retourne un nom:

1. le score est ajoute;
2. le menu met a jour sa preview des highscores;
3. on revient au menu.

### Etat `instructions`

N'importe quelle touche renvoie au menu.

### Etat `highscores`

N'importe quelle touche renvoie au menu.

### `renderer.flip()`

A la fin de chaque frame, on appelle `flip()` pour afficher ce qui a ete dessine
dans le back buffer.

### `window.close()`

Quand la boucle se termine, on ferme proprement `pygame`.

### `main(argv=None)`

Cette fonction:

1. recupere les arguments;
2. detecte `--debug`;
3. verifie le nombre d'arguments;
4. verifie l'extension `.json`;
5. charge la config;
6. lance `_run(config)`;
7. gere les exceptions.

Important:

- sans `--debug`, l'utilisateur ne voit pas de stack trace;
- avec `--debug`, `traceback.print_exc()` aide a deboguer.

### `if __name__ == "__main__"`

Cette condition signifie:

> Si ce fichier est lance directement, execute `main()`.

Si le fichier est importe depuis un autre module, `main()` n'est pas lance
automatiquement.

---

# 10.2 `pacman/config.py`

## Role du fichier

Ce fichier lit et valide la configuration.

Il transforme un fichier externe potentiellement faux en dictionnaire propre et
utilisable par le jeu.

## Lecture dans l'ordre

Docstring:

Elle indique que le fichier contient le parser de configuration.

`from __future__ import annotations`

Meme raison que dans `pac-man.py`: annotations de type plus souples.

Imports:

- `json`: parser le JSON;
- `sys`: ecrire les warnings sur `stderr`;
- `Path`: manipuler le chemin du fichier;
- `Any`, `Dict`: types.

### `DEFAULT_CONFIG`

C'est le dictionnaire de valeurs par defaut.

Il contient:

- fichier highscore;
- taille du labyrinthe;
- seed;
- vies;
- vitesses;
- duree de niveau;
- scoring;
- taille fenetre;
- couleurs.

Pourquoi un default complet?

Parce que si la config est incomplete, le jeu doit quand meme tourner.

### `_INT_KEYS`

Ensemble des cles qui doivent etre converties en entiers.

Exemples:

- `width`;
- `height`;
- `seed`;
- `lives`;
- `fps`.

### `_FLOAT_KEYS`

Ensemble des cles qui doivent etre converties en flottants.

Exemples:

- `player_speed`;
- `ghost_speed`;
- `frightened_duration`;
- `respawn_delay`.

### `_log(message)`

Affiche un warning avec le prefixe `[config]`.

### `_strip_comments(raw_text)`

Cette fonction retire les lignes qui commencent par `#`.

Pourquoi?

Le JSON standard ne supporte pas les commentaires. Cette fonction permet
d'ecrire une config plus lisible avec des lignes commentees.

Attention:

Elle retire seulement les lignes dont le premier caractere non espace est `#`.

### `_clamp_int(value, default, minimum, maximum)`

Cette fonction:

1. essaie de convertir `value` en `int`;
2. si ca echoue, retourne `default`;
3. sinon limite le nombre entre `minimum` et `maximum`.

Exemple:

- valeur `-5`, minimum `1` -> `1`;
- valeur `999999`, maximum `10000` -> `10000`;
- valeur `"abc"` -> default.

### `_clamp_float(...)`

Meme idee que `_clamp_int`, mais pour les nombres flottants.

### `_normalize_color(value, default)`

Cette fonction valide une couleur RGB.

Une couleur valide doit etre:

- une liste;
- de longueur 3;
- avec des valeurs convertibles en entiers;
- chaque canal est limite entre 0 et 255.

Si la couleur est mauvaise, on retourne la couleur par defaut.

### `validate_config(config)`

Fonction centrale de validation.

Etapes:

1. Copier `DEFAULT_CONFIG` dans `validated`.
2. Parcourir chaque cle attendue.
3. Si la cle manque, log warning et garder le default.
4. Si la cle est entiere, utiliser `_clamp_int`.
5. Si la cle est flottante, utiliser `_clamp_float`.
6. Si c'est `perfect_maze`, convertir en bool.
7. Si c'est une couleur, utiliser `_normalize_color`.
8. Si c'est `highscore_filename`, convertir en string non vide.
9. Sinon, recopier la valeur.
10. Parcourir les cles inconnues et les signaler.
11. Reforcer certaines limites minimales importantes.

Pourquoi deux niveaux de limites?

- `_clamp_int` evite les valeurs absurdes;
- les corrections finales garantissent des regles metier, par exemple au moins
  1 vie.

### `parse_config(filepath)`

Cette fonction lit le fichier.

Etapes:

1. Convertir `filepath` en `Path`.
2. Si le fichier n'existe pas, log warning et retourner les defaults.
3. Lire le texte.
4. Retirer les lignes de commentaire.
5. Parser le JSON.
6. Si JSON invalide, retourner les defaults.
7. Si erreur de lecture, retourner les defaults.
8. Verifier que la racine est un objet JSON, donc un dict Python.
9. Appeler `validate_config`.

Point defense important:

> La config est une frontiere externe. On ne lui fait pas confiance.

---

# 10.3 `pacman/maze_loader.py`

## Role du fichier

Ce fichier fait le lien entre le package externe `mazegenerator` et notre jeu.

Il:

- importe `MazeGenerator`;
- genere une grille brute de bitmasks;
- convertit cette grille en tiles jouables;
- choisit les spawns.

## Lecture dans l'ordre

Imports:

- `sys`: warnings;
- `List`, `Tuple`: types;
- `MazeGenerator`: package externe.

Le `try/except` autour de l'import:

Si `mazegenerator` n'est pas disponible, `MazeGenerator = None`.

Pourquoi?

Le jeu peut utiliser un labyrinthe de fallback au lieu de crasher au chargement.

### Constantes de tiles

```python
WALL = "WALL"
WALL_42 = "WALL_42"
CORRIDOR = "CORRIDOR"
PACGUM = "PACGUM"
SUPER_PACGUM = "SUPER_PACGUM"
SPAWN_PACMAN = "SPAWN_PACMAN"
SPAWN_GHOST = "SPAWN_GHOST"
```

Ces constantes evitent d'ecrire des strings magiques partout.

### Constantes de bits

```python
_NORTH, _EAST, _SOUTH, _WEST = 1, 2, 4, 8
```

Elles rendent le bitmask lisible.

Au lieu de se demander "que veut dire 2?", on lit `_EAST`.

### `_log(message)`

Affiche un warning avec `[maze_loader]`.

### `_fallback_maze(width, height)`

Cette fonction cree un labyrinthe tres simple:

- pas de murs internes;
- seulement des murs autour.

Elle parcourt chaque cellule `(x, y)`:

- si `y == 0`, ajoute un mur nord;
- si `x == width - 1`, ajoute un mur est;
- si `y == height - 1`, ajoute un mur sud;
- si `x == 0`, ajoute un mur ouest.

Elle retourne une liste de listes d'entiers.

Pourquoi?

Si le generateur externe echoue, le jeu reste jouable.

### `generate_maze(width, height, seed, perfect=False)`

Cette fonction essaie d'utiliser `MazeGenerator`.

Si `MazeGenerator is None`, elle utilise `_fallback_maze`.

Sinon:

1. creer `MazeGenerator(size=(width, height), perfect=..., seed=...)`;
2. lire l'attribut `.maze`;
3. verifier que c'est une liste de listes;
4. retourner la grille.

Si une erreur arrive, elle log et retourne le fallback.

### `convert_maze_to_tiles(maze)`

Fonction tres importante.

But:

> Transformer les cellules bitmask en vraie grille de jeu.

Etapes:

1. Si le maze est vide, retourner deux listes vides.
2. Calculer `cells_h` et `cells_w`.
3. Calculer `grid_w = 2 * cells_w + 1`.
4. Calculer `grid_h = 2 * cells_h + 1`.
5. Creer une grille remplie de `WALL`.
6. Parcourir chaque cellule brute.
7. Convertir `(cx, cy)` en `(tx, ty) = (2cx + 1, 2cy + 1)`.
8. Lire le mask.
9. Si `mask == 15`, mettre `WALL_42`.
10. Sinon mettre `PACGUM`.
11. Si l'ouverture est vers l'est, mettre une pacgum entre la cellule et sa voisine.
12. Si l'ouverture est vers le sud, mettre une pacgum entre la cellule et sa voisine.

Pourquoi seulement est et sud?

Parce qu'en parcourant toutes les cellules, regarder est et sud suffit pour
poser tous les couloirs internes une seule fois. Ouest et nord seraient des
doublons vus depuis les cellules voisines.

### Super-pacgums

Les super-pacgums sont placees aux quatre coins jouables.

Pourquoi apres la grille?

Parce qu'on veut remplacer certaines pacgums normales par des super-pacgums.

### Spawn Pac-Man

Pac-Man spawn au centre du labyrinthe.

Si le centre est bloque, `_nearest_open_cell()` cherche la cellule ouverte la
plus proche.

### Spawn fantomes

Les fantomes spawn pres des quatre coins.

La liste `spawn_positions` contient:

1. spawn Pac-Man en index 0;
2. puis les quatre spawns de fantomes.

### `_nearest_open_cell(maze, cx, cy)`

Cette fonction cherche une cellule pas completement bloquee pres d'un point.

Elle augmente progressivement un rayon:

```text
rayon 0, puis 1, puis 2, ...
```

Des qu'elle trouve une cellule dont le mask n'est pas `15`, elle la retourne.

### `_ghost_corner_cells(maze)`

Cette fonction part des quatre coins bruts:

- haut gauche;
- haut droit;
- bas gauche;
- bas droit.

Pour chaque coin, elle appelle `_nearest_open_cell`.

---

# 10.4 `pacman/scoring.py`

## Role du fichier

Ce fichier gere uniquement les points.

C'est bien separe: le jeu demande "ajoute une pacgum" ou "ajoute un fantome",
et `Scoring` decide combien ca vaut.

## Lecture dans l'ordre

Imports:

- `Dict`: type pour la config.

### Classe `Scoring`

Le constructeur lit:

- `points_per_pacgum`;
- `points_per_super_pacgum`;
- `points_per_ghost`.

Il initialise:

- `score = 0`;
- `ghost_multiplier = 1`.

### `add_pacgum()`

Ajoute les points d'une pacgum normale.

Important:

Elle ne reset pas le multiplicateur fantome.

### `add_super_pacgum()`

Ajoute les points d'une super-pacgum.

Puis reset le multiplicateur fantome.

Pourquoi?

Une nouvelle super-pacgum demarre une nouvelle chaine de fantomes.

### `add_ghost()`

Calcule:

```python
points = points_per_ghost * ghost_multiplier
```

Puis:

- ajoute les points au score;
- double le multiplicateur;
- le limite a `8`.

Avec base `200`, on obtient:

```text
200, 400, 800, 1600
```

### `reset_ghost_multiplier()`

Remet le multiplicateur a 1.

---

# 10.5 `pacman/cheat.py`

## Role du fichier

Ce fichier gere les cheats demandes pour faciliter les tests et la defense.

## Lecture dans l'ordre

### Classe `CheatMode`

Le constructeur initialise:

- `invincible = False`;
- `ghosts_frozen = False`;
- `speed_multiplier = 1.0`;
- `pending_skip = False`;
- `extra_lives = 0`;
- `pending_power_up = False`.

### `toggle_invincibility()`

Inverse `invincible`.

Si c'etait `False`, ca devient `True`.
Si c'etait `True`, ca devient `False`.

### `skip_level()`

Ne change pas directement le niveau.

Elle met `pending_skip = True`.

Pourquoi?

Parce que le niveau doit etre change proprement dans `Game.update()`, au bon
moment de la boucle moteur.

### `freeze_ghosts()`

Inverse `ghosts_frozen`.

Si actif, les fantomes ne sont plus mis a jour.

### `add_life()`

Incremente `extra_lives`.

La vie sera appliquee dans `_apply_cheats()`.

### `double_speed()`

Alterne:

- `1.0`;
- `2.0`.

La vitesse joueur et fantomes sera multipliee par cette valeur.

### `trigger_power_up()`

Met `pending_power_up = True`.

Ce cheat simule une super-pacgum.

### `consume_power_up_request()`

Si une demande de power-up existe:

1. retourne `True`;
2. remet `pending_power_up` a `False`.

Sinon retourne `False`.

Le mot "consume" signifie "lire et vider".

### `get_active_cheats()`

Retourne un dictionnaire indiquant quels cheats sont actifs.

Le renderer l'utilise pour afficher l'overlay.

### `toggle_cheat_by_key(key)`

Associe une touche a une fonction:

| Touche | Action |
|---|---|
| `i` | invincibilite |
| `l` | skip level |
| `f` | freeze ghosts |
| `+` | +1 vie |
| `s` | vitesse x2 |
| `p` | power-up |

### `consume_skip_request()`

Meme idee que `consume_power_up_request`, mais pour le skip level.

---

# 10.6 `pacman/entities/player.py`

## Role du fichier

Ce fichier contient Pac-Man.

Il gere:

- position;
- direction;
- direction bufferisee;
- mouvement;
- collisions avec les murs;
- vies;
- respawn.

## Lecture dans l'ordre

Imports:

- `Sequence`: type pour une grille lisible sans la modifier;
- `Tuple`: type pour les positions.

### `_is_blocked(grid, current_x, current_y, dx, dy)`

Cette fonction regarde si un mouvement est possible.

Etapes:

1. Calculer la case cible:
   - `target_x = current_x + dx`;
   - `target_y = current_y + dy`.
2. Si la cible est hors grille, retourner `True`.
3. Lire `current_cell` et `target_cell`.
4. Si `current_cell` est un entier, utiliser les bits de mur.
5. Sinon, verifier si `target_cell` est `WALL` ou `WALL_42`.

Pourquoi regarder `current_cell` pour les entiers?

Parce qu'avec le format bitmask, les murs sont stockes dans la cellule actuelle.
Exemple: si je veux aller a droite, je regarde si le bit est est present.

### Classe `Player`

Le constructeur recoit:

- `x`;
- `y`;
- `lives`.

Il stocke:

- position actuelle;
- position de spawn;
- vies;
- direction actuelle;
- direction bufferisee;
- progression de mouvement.

### Propriete `pos`

Retourne `(self.x, self.y)`.

Elle evite d'ecrire ce tuple partout.

### Propriete `dir`

Retourne `(direction_x, direction_y)`.

Le renderer et les fantomes peuvent connaitre la direction actuelle.

### Propriete `visual_pos`

Retourne une position flottante.

Elle limite `_move_progress` entre `0.0` et `0.999`.

Pourquoi pas `1.0`?

Parce que `1.0` correspond deja a la case suivante. Garder `0.999` evite un
dessin ambigu pile sur la limite.

### `set_direction(dx, dy)`

Cette fonction recoit une direction.

Elle accepte seulement une direction cardinale:

- droite: `(1, 0)`;
- gauche: `(-1, 0)`;
- bas: `(0, 1)`;
- haut: `(0, -1)`.

Le test:

```python
abs(dx) + abs(dy) != 1
```

refuse:

- `(0, 0)`;
- diagonales comme `(1, 1)`;
- valeurs invalides.

Si valide, la direction est stockee dans le buffer.

### `update(dt, grid, config)`

C'est la fonction principale du joueur.

Etapes:

1. Si la grille est vide, ne rien faire.
2. Si une direction est bufferisee, tester si elle est possible.
3. Si possible, changer la direction actuelle.
4. Lire la vitesse depuis la config.
5. Augmenter `_move_progress` avec `speed * dt`.
6. Limiter `_move_progress` a `1.0`.
7. Si la progression atteint 1 case:
   - tester si la direction est bloquee;
   - si bloquee, stopper;
   - sinon avancer `x` et `y`;
   - retirer `1.0` a la progression.
8. Si la prochaine case est un mur, arreter la direction pour eviter un
   glissement visuel dans le mur.

Point important:

Le code separe mouvement logique et mouvement visuel. La position entiere ne
change que quand une case complete est traversee.

### `lose_life()`

Retire une vie sans descendre sous 0.

Retourne `True` si le joueur n'a plus de vies.

### `respawn(spawn_pos)`

Replace Pac-Man au spawn.

Reset:

- direction;
- buffer;
- progression.

Pourquoi reset la progression?

Sinon Pac-Man pourrait respawn en etant deja a moitie entre deux cases.

---

# 10.7 `pacman/entities/ghost.py`

## Role du fichier

Ce fichier contient les fantomes et leur IA.

Il gere:

- comportements;
- BFS;
- etats;
- deplacements;
- timers;
- respawn.

## Lecture dans l'ordre

Imports:

- `random`: hasard;
- `deque`: file BFS;
- `Enum`: comportements/etats;
- types.

### `_is_blocked(...)`

Meme idee que dans `player.py`.

Elle permet aux fantomes de savoir si une direction est possible.

### `_bfs_next_step(grid, start, target, forbid=None)`

Fonction importante.

But:

> Trouver le premier pas du plus court chemin vers `target`.

Etapes:

1. Si `start == target`, retourner `None`.
2. Verifier que la grille et le depart sont valides.
3. Creer `visited` avec `start`.
4. Creer une `queue`.
5. Definir les directions candidates.
6. Pour chaque direction autour du depart:
   - ignorer `forbid`;
   - ignorer les murs;
   - ajouter la case voisine dans la queue;
   - memoriser le premier pas.
7. Tant que la queue n'est pas vide:
   - prendre le premier element;
   - si c'est la cible, retourner `first_step`;
   - sinon explorer ses voisins.
8. Si rien n'est trouve, retourner `None`.

Pourquoi stocker `first_step`?

Le fantome n'a pas besoin du chemin entier. Il a seulement besoin de savoir quel
premier mouvement faire maintenant.

### `GhostBehavior`

Enum des comportements:

- `CHASE`;
- `AMBUSH`;
- `RANDOM`;
- `SCATTER`.

### `GhostState`

Enum des etats:

- `NORMAL`;
- `FRIGHTENED`;
- `EATEN`.

### Classe `Ghost`

Le constructeur recoit:

- `x`;
- `y`;
- `ghost_id`;
- `behavior`.

Il initialise:

- position actuelle;
- position de spawn;
- id;
- comportement;
- etat normal;
- direction;
- progression;
- timer d'etat;
- generateur aleatoire prive;
- cible scatter.

Pourquoi un random prive?

Chaque fantome a son propre generateur. Cela rend le comportement plus stable
et reproductible que d'utiliser le random global partout.

### Propriete `pos`

Retourne la position entiere.

### Propriete `dir`

Retourne la direction actuelle.

### Propriete `visual_pos`

Retourne la position flottante pour le rendu.

### Propriete `state_time_left`

Retourne le temps restant de l'etat courant, minimum 0.

### `set_state(state, duration=0.0)`

Change l'etat du fantome.

Etapes:

1. Memoriser l'etat precedent.
2. Changer `self.state`.
3. Stocker le timer.
4. Si retour a `NORMAL`, reset la direction.
5. Si `EATEN` sans duree, mettre au moins `0.1`.
6. Si passage en `FRIGHTENED`, inverser la direction.

Pourquoi inverser la direction en frightened?

C'est une regle classique de Pac-Man: quand les fantomes deviennent effrayes,
ils font demi-tour.

### `_neighbors(grid, forbid_reverse=True)`

Retourne les directions ouvertes autour du fantome.

Etapes:

1. Lister les quatre directions.
2. Garder celles qui ne sont pas bloquees.
3. Si pas de direction actuelle, retourner toutes les directions ouvertes.
4. Calculer la direction inverse.
5. Retirer cette direction inverse.
6. Si tout a ete retire, revenir a la liste complete.

Pourquoi revenir a la liste complete?

Parce qu'a un cul-de-sac, le fantome doit pouvoir faire demi-tour.

### `_pick_direction(grid, player_pos, player_dir)`

Fonction centrale de l'IA.

Elle choisit une direction selon:

- l'etat du fantome;
- son comportement;
- la position du joueur;
- la direction du joueur.

Etapes:

1. Recuperer les voisins ouverts.
2. Si aucun voisin, retourner `(0, 0)`.
3. Si `FRIGHTENED`, choisir une direction qui eloigne du joueur.
4. Si `EATEN`, cibler le spawn.
5. Si `RANDOM`, choisir un voisin au hasard.
6. Si `SCATTER`, cibler le coin.
7. Si `AMBUSH`, cibler 4 cases devant Pac-Man.
8. Sinon `CHASE`, cibler Pac-Man.
9. Calculer la direction interdite si on veut eviter le demi-tour.
10. Appeler BFS.
11. Si BFS donne un bon pas, l'utiliser.
12. Sinon choisir le voisin le plus proche de la cible par distance au carre.

Pourquoi fallback par distance au carre?

Si la cible est inaccessible ou dans un mur, on veut quand meme un mouvement
raisonnable.

Distance au carre:

```text
dx*dx + dy*dy
```

Pas besoin de racine car comparer les carres donne le meme ordre.

### `update(dt, grid, player_pos, config, player_dir=(0, 0))`

Met a jour le fantome.

Etapes:

1. Diminuer le timer d'etat.
2. Si timer fini et etat `EATEN`, respawn et retourner.
3. Si timer fini et etat `FRIGHTENED`, revenir a `NORMAL`.
4. Si etat `EATEN`, ne pas bouger.
5. Lire la vitesse depuis la config.
6. Si frightened, reduire la vitesse a 60%.
7. Si aucune direction, en choisir une.
8. Augmenter `_move_progress`.
9. Si une case complete est traversee:
   - avancer si pas bloque;
   - sinon reset la progression;
   - choisir une nouvelle direction au centre de la case.

Point tres important:

Le fantome change de direction seulement au centre d'une case. Cela evite les
trajectoires visuelles bizarres.

### `respawn(spawn_pos)`

Replace le fantome au spawn.

Reset:

- position;
- spawn;
- etat;
- direction;
- progression;
- timer.

### `get_all_ghosts()`

Methode statique qui cree les quatre fantomes:

- fantome 0: `CHASE`;
- fantome 1: `AMBUSH`;
- fantome 2: `RANDOM`;
- fantome 3: `SCATTER`.

---

# 10.8 `pacman/game.py`

## Role du fichier

`game.py` est le coeur du moteur.

Il relie:

- config;
- scoring;
- cheats;
- labyrinthe;
- joueur;
- fantomes;
- collisions;
- niveaux;
- etat du jeu.

## Lecture dans l'ordre

Imports:

- `random`: seeds des niveaux;
- `dataclass`, `field`: structures de donnees;
- `Enum`: modes de jeu;
- types;
- modules internes.

### `GameMode`

Enum:

- `PLAY`;
- `PAUSE`;
- `GAMEOVER`;
- `WIN`.

Il indique l'etat logique de la partie.

### `FloatingEffect`

Dataclass pour un effet visuel court.

Champs:

- `text`: texte affiche, par exemple `+200`;
- `x`, `y`: position;
- `color`: couleur RGB;
- `time_left`: temps restant;
- `lifetime`: duree totale.

### `GameState`

Dataclass frozen, donc pensee comme lecture seule.

Champs:

- `score`;
- `lives`;
- `level`;
- `time_left`;
- `pacman`;
- `ghosts`;
- `grid`;
- `mode`;
- `ready_time_left`;
- `frightened_time_left`;
- `effects`;
- `eat_freeze`.

Pourquoi `field(default_factory=...)`?

Pour eviter les valeurs mutables partagees entre instances, par exemple une
liste unique partagee accidentellement.

### Classe `Game`

Le constructeur recoit `config`.

Il initialise:

- `Scoring`;
- `CheatMode`;
- nombre max de niveaux;
- niveau courant;
- mode;
- temps restant;
- generateur aleatoire;
- seed courante;
- grille;
- labyrinthe brut;
- nombre de pacgums restantes;
- spawns;
- joueur;
- fantomes;
- grace period;
- effets;
- eat freeze.

Puis il appelle `_load_level()`.

### Propriete `score`

Retourne `self.scoring.score`.

Ca expose le score sans laisser l'exterieur manipuler directement le scoring.

### `_load_level(level, seed)`

Charge ou recharge un niveau.

Etapes:

1. Lire largeur et hauteur depuis la config.
2. Garder les vies actuelles du joueur.
3. Appeler `generate_maze`.
4. Convertir le maze en tiles.
5. En cas d'erreur, utiliser une grille vide.
6. Choisir le spawn joueur.
7. Recréer le joueur au spawn avec ses vies.
8. Creer les fantomes.
9. Calculer les coins de scatter.
10. Donner une cible scatter a chaque fantome.
11. Respawn les fantomes aux positions prevues.
12. Reset le temps.
13. Compter les pacgums.
14. Mettre 2 secondes de grace period.
15. Mettre le mode en `PLAY`.

Pourquoi garder les vies?

Quand on change de niveau, le joueur ne doit pas revenir au nombre initial de
vies.

### `_count_pacgums()`

Parcourt toute la grille et compte:

- `PACGUM`;
- `SUPER_PACGUM`.

### `_tile_at(x, y)`

Retourne le type de tile.

Si la position est hors grille, retourne `"WALL"`.

Pourquoi?

Hors grille doit etre considere comme bloque.

### `_apply_cheats()`

Applique les cheats qui modifient directement l'etat moteur.

Actuellement:

- si `extra_lives > 0`, ajouter ces vies au joueur;
- remettre `extra_lives` a 0.

### `_apply_pacgum_pickup()`

Regarde la tile sous Pac-Man.

Si c'est `PACGUM`:

1. remplacer par `CORRIDOR`;
2. ajouter les points;
3. diminuer le nombre de pacgums restantes.

Si c'est `SUPER_PACGUM`:

1. remplacer par `CORRIDOR`;
2. ajouter les points;
3. diminuer le nombre de pacgums restantes;
4. passer tous les fantomes en `FRIGHTENED`.

### `_handle_collisions()`

Parcourt tous les fantomes.

Si un fantome n'est pas sur la meme case que Pac-Man, continuer.

Si le fantome est `EATEN`, il ne fait rien.

Si le fantome est `FRIGHTENED`:

1. ajouter le score de fantome;
2. passer le fantome en `EATEN`;
3. afficher un effet `+points`;
4. mettre un petit freeze pour que le joueur voie le score.

Si Pac-Man est invincible ou en grace period, collision ignoree.

Sinon:

1. Pac-Man perd une vie;
2. s'il n'a plus de vies, mode `GAMEOVER`;
3. sinon Pac-Man et les fantomes respawn;
4. grace period de 2 secondes.

### `_spawn_eat_effect(pos, points)`

Ajoute un `FloatingEffect` dans la liste.

Le renderer l'affichera.

### `_update_effects(dt)`

Met a jour les effets:

- baisse `time_left`;
- fait monter le texte (`y -= dt * 1.5`);
- supprime les effets termines.

### `_handle_level_complete()`

Si des pacgums restent, rien.

Sinon:

- appeler `next_level()`;
- si `next_level()` retourne `False`, mettre le mode `WIN`.

### `get_state()`

Construit un `GameState`.

Il calcule d'abord le temps frightened restant maximum parmi les fantomes.

Puis il retourne:

- score;
- vies;
- niveau;
- temps;
- joueur;
- fantomes;
- grille;
- mode;
- timers;
- effets.

Pourquoi copier `effects` avec `list(self._effects)`?

Pour donner une copie de la liste a l'UI, pas la liste interne exacte.

### `update(dt, input_dir=(0,0))`

Fonction la plus importante du moteur.

Etapes completes:

1. Si le mode n'est pas `PLAY`, retourner.
2. Si un skip level est demande, appeler `next_level()` et retourner.
3. Si un power-up cheat est demande, passer tous les fantomes en frightened.
4. Appliquer les cheats.
5. Si `eat_freeze` est actif:
   - diminuer le freeze;
   - animer les effets;
   - retourner.
6. Si une direction existe, l'envoyer au joueur.
7. Copier la config dans `update_config`.
8. Calculer le scaling de difficulte.
9. Ajuster vitesse joueur et fantomes.
10. Ajuster la duree frightened.
11. Mettre a jour le joueur.
12. Diminuer la grace period.
13. Si les fantomes ne sont pas freezes et la grace period est finie:
    - mettre a jour chaque fantome.
14. Appliquer les pacgums.
15. Gerer les collisions.
16. Mettre a jour les effets.
17. Reset le multiplicateur fantome si tous les fantomes sont normaux.
18. Diminuer le temps.
19. Si temps a 0, restart level.
20. Verifier si le niveau est termine.

### Scaling de difficulte

```python
level_factor = 1.0 + 0.05 * min(self.level - 1, 8)
```

Les fantomes gagnent 5% de vitesse par niveau, plafonne apres 8 niveaux.

La duree frightened diminue aussi un peu, mais ne descend pas sous 2 secondes.

### `set_mode(mode)`

Change le mode du jeu.

### `next_level()`

Si le niveau courant est deja le dernier:

- retourner `False`.

Sinon:

1. incrementer le niveau;
2. generer une nouvelle seed;
3. appeler `_load_level`;
4. retourner `True`.

### `restart_level()`

Recharge le niveau actuel avec la meme seed.

Pourquoi la meme seed?

Pour que le niveau redemarre identique quand le temps expire.

---

# 10.9 `pacman/highscore.py`

## Role du fichier

Ce fichier gere le top 10 persistant.

## Lecture dans l'ordre

Imports:

- `json`: lire/ecrire le fichier;
- `string`: caracteres autorises;
- `sys`: warnings;
- `Path`: chemin;
- types.

Constantes:

- `_MAX_ENTRIES = 10`;
- `_NAME_MAX = 10`;
- `_ALLOWED`: lettres, chiffres, espace.

### `_log(message)`

Affiche `[highscore] message`.

### Classe `HighscoreManager`

Le constructeur stocke le nom de fichier et appelle `load()`.

### `load()`

Etapes:

1. Si le fichier n'existe pas, retourner une liste vide.
2. Lire le JSON.
3. Si erreur, warning et liste vide.
4. Verifier que la racine est une liste.
5. Parcourir les entrees.
6. Garder seulement les listes `[name, score]`.
7. Convertir score en int.
8. Ignorer score negatif.
9. Nettoyer le nom avec `validate_name`.
10. Trier par score decroissant.
11. Garder top 10.

### `save(highscores=None)`

Sauvegarde en JSON.

Si une liste est fournie, elle remplace `_entries`.

Elle retourne:

- `True` si l'ecriture reussit;
- `False` sinon.

Elle ne leve pas d'exception.

### `add_score(name, score)`

Etapes:

1. Nettoyer le nom.
2. Convertir le score en int.
3. Refuser les scores negatifs.
4. Ajouter la nouvelle entree.
5. Trier.
6. Garder top 10.
7. Trouver le rang.
8. Sauvegarder.
9. Retourner le rang ou `None`.

### `get_top_10()`

Retourne une copie de la liste.

Pourquoi une copie?

Pour eviter que l'appelant modifie `_entries` directement.

### `validate_name(name)`

Etapes:

1. Si ce n'est pas une string, retourner `"Player"`.
2. Garder seulement les caracteres autorises.
3. Supprimer les espaces debut/fin.
4. Couper a 10 caracteres.
5. Si vide, retourner `"Player"`.

---

# 10.10 `pacman/ui/window.py`

## Role du fichier

Ce fichier encapsule la fenetre `pygame`.

Il gere:

- initialisation;
- taille;
- titre;
- FPS;
- clavier;
- evenements;
- fermeture.

## Lecture dans l'ordre

Imports:

- `sys`: message si pygame manque;
- `Callable`, `Optional`, `Tuple`: types;
- `pygame`: bibliotheque graphique.

Le `try/except` autour de `pygame`:

Si `pygame` n'est pas installe, le message est clair.

### `_DIRECTION_KEYS`

Dictionnaire qui mappe les touches vers des directions.

Exemples:

- fleche haut et `W`: `(0, -1)`;
- fleche bas et `S`: `(0, 1)`;
- fleche gauche et `A`: `(-1, 0)`;
- fleche droite et `D`: `(1, 0)`.

### Classe `GameWindow`

Le constructeur:

1. appelle `pygame.init()`;
2. met le titre;
3. cree la fenetre;
4. cree l'horloge;
5. stocke le FPS;
6. initialise direction et buffer;
7. initialise quit flag;
8. initialise liste d'evenements.

### `get_input()`

Retourne la direction a envoyer au moteur.

Priorite:

1. direction bufferisee par un `KEYDOWN`;
2. sinon touche actuellement maintenue.

Pourquoi les deux?

- Le buffer capture un appui court.
- `get_pressed()` permet de continuer si la touche reste maintenue.

### `handle_events(...)`

Parcourt `pygame.event.get()`.

Pour chaque evenement:

- l'ajoute a `_pending_events`;
- si `QUIT`, demander fermeture;
- si `KEYDOWN`, gerer pause, direction, callback clavier.

Retourne `False` si la fenetre doit fermer.

### Propriete `events`

Retourne une copie des evenements de la derniere frame.

`pac-man.py` les utilise pour les menus/ecrans.

### `set_fps(fps)`

Change la limite de FPS.

### `tick()`

Attend selon le FPS, retourne `dt` en secondes, puis clamp a `1/30`.

### `update(dt=0.0)`

Alias historique de `tick()`.

### `close()`

Appelle `pygame.quit()` dans un `try/except`.

---

# 10.11 `pacman/ui/renderer.py`

## Role du fichier

Ce fichier dessine le jeu.

Il ne decide pas les regles. Il transforme un `GameState` en pixels.

## Lecture dans l'ordre

Imports:

- `math`: animations;
- types;
- `pygame`;
- classes internes.

### `_color(config, key, default)`

Lit une couleur depuis la config.

Si la valeur est une liste/tuple de 3 elements, elle la convertit en tuple
d'entiers.

Sinon, elle utilise la couleur par defaut.

### Classe `Renderer`

Constante:

```python
HUD_HEIGHT = 56
```

Elle reserve 56 pixels en haut pour le HUD.

Le constructeur:

- stocke screen et config;
- cree les polices;
- initialise le temps d'animation;
- lit les couleurs des fantomes;
- prepare un cache de murs;
- prepare un cache de sprites fantomes.

### `_tile_size(grid)`

Calcule la taille d'une tile en pixels.

Elle prend le minimum entre:

- largeur disponible / nombre de colonnes;
- hauteur disponible / nombre de lignes.

Pourquoi?

Pour que le labyrinthe tienne dans la fenetre sans deborder.

### `_offset(grid, tile)`

Calcule le decalage pour centrer le labyrinthe sous le HUD.

Retourne `(ox, oy)`.

### `render_game(state, dt=0.0)`

Fonction principale de rendu.

Etapes:

1. Ajouter `dt` au temps d'animation.
2. Remplir l'ecran avec le fond.
3. Si la grille est vide, retourner.
4. Calculer taille de tile et offset.
5. Dessiner la grille.
6. Dessiner Pac-Man.
7. Dessiner les fantomes.
8. Dessiner le HUD.
9. Dessiner la barre frightened si active.
10. Dessiner les effets.
11. Dessiner READY si grace period active.
12. Dessiner pause overlay si mode pause.

### `_rebuild_wall_cache(grid, tile)`

Cree une surface contenant les murs.

Elle:

- calcule taille pixel;
- lit couleurs;
- cree une surface;
- remplit le fond corridor;
- parcourt la grille;
- dessine les `WALL` et `WALL_42`.

Pourquoi cache?

Les murs sont statiques pendant un niveau. Les pre-dessiner evite du travail a
chaque frame.

### `render_grid(grid, tile, ox, oy)`

Dessine:

- le cache de murs;
- les pacgums;
- les super-pacgums.

Le cache est reconstruit si:

- la grille change;
- la taille de tile change.

Les super-pacgums clignotent avec `math.sin`.

### `render_pacman(x, y, direction, tile, ox, oy)`

Dessine Pac-Man.

Etapes:

1. Lire la couleur.
2. Calculer le centre en pixels.
3. Calculer le rayon.
4. Si trop petit, dessiner un simple cercle.
5. Calculer l'ouverture de bouche avec `sin`.
6. Choisir l'angle selon la direction.
7. Construire une liste de points.
8. Dessiner un polygone.

Pourquoi un polygone?

Parce qu'un cercle avec une bouche ouverte peut etre represente comme un
secteur de disque.

### `_build_ghost_sprite(color, tile)`

Cree une surface transparente pour un fantome.

Elle dessine:

- corps arrondi;
- bas ondule;
- yeux blancs;
- pupilles.

La surface est ensuite reutilisee.

### `_get_ghost_sprite(color, tile)`

Regarde si le sprite existe deja dans le cache.

Si non, elle le cree.

Si la taille de tile change, elle vide le cache.

### `render_ghosts(ghosts, tile, ox, oy)`

Parcourt les fantomes.

Si un fantome est `EATEN`, il n'est pas dessine.

Si `FRIGHTENED`, il alterne entre bleu et blanc.

Sinon, il utilise sa couleur normale.

Puis:

- recupere le sprite;
- lit `visual_pos`;
- convertit en pixels;
- blit le sprite.

### `render_hud(score, lives, level, time_left)`

Dessine la barre du haut:

- fond;
- ligne de separation;
- score;
- icones de vies;
- niveau;
- temps.

### `_render_effects(effects, tile, ox, oy)`

Dessine les textes flottants comme `+200`.

Le texte devient transparent quand `time_left` diminue.

### `_render_ready_overlay(time_left)`

Affiche `READY!` au centre pendant la grace period.

### `_render_frightened_bar(time_left, total)`

Affiche une petite barre sous le HUD indiquant le temps de power-up restant.

### `render_pause_overlay()`

Affiche un overlay sombre et le texte `PAUSED`.

### `render_cheat_overlay(active_cheats)`

Affiche les cheats actifs en haut a gauche.

Il n'affiche pas les cheats instantanes deja consommes, comme skip level.

### `flip()`

Appelle:

```python
pygame.display.flip()
```

Cela affiche la frame.

---

# 10.12 `pacman/ui/menu.py`

## Role du fichier

Ce fichier gere le menu principal.

## Lecture dans l'ordre

Imports:

- `Enum`: items du menu;
- types;
- `pygame`.

### `MenuItem`

Enum:

- `START_GAME`;
- `HIGHSCORES`;
- `INSTRUCTIONS`;
- `EXIT`.

### `_LABELS`

Dictionnaire qui associe chaque enum a un texte affiche.

### Classe `MainMenu`

Le constructeur:

- stocke screen et config;
- cree la liste des items;
- selectionne le premier item;
- prepare highscores;
- cree les polices.

### `set_highscores(highscores)`

Met a jour la liste de scores affichee sur le menu.

### `move(delta)`

Bouge la selection.

Utilise modulo:

```python
self.selection = (self.selection + delta) % len(self.items)
```

Pourquoi modulo?

Pour faire le wrap:

- si on monte depuis le premier, on arrive au dernier;
- si on descend depuis le dernier, on revient au premier.

### `handle_event(event)`

Si ce n'est pas un `KEYDOWN`, retourne `None`.

Sinon:

- haut/W: selection precedente;
- bas/S: selection suivante;
- enter/espace: retourne l'item choisi;
- escape: retourne `EXIT`.

### `handle_input(direction)`

Methode legacy basee sur direction.

Elle est gardee pour compatibilite mais le menu utilise surtout les events.

### `render()`

Dessine:

- fond;
- titre `PAC-MAN`;
- options;
- curseur `>`;
- preview des highscores;
- hint en bas.

---

# 10.13 `pacman/ui/screens.py`

## Role du fichier

Ce fichier regroupe les ecrans secondaires:

- pause;
- saisie du nom;
- game over/victoire;
- instructions;
- highscores.

## Lecture dans l'ordre

Imports:

- types;
- `pygame`;
- `HighscoreManager`.

### Classe `_ScreenBase`

Classe de base partagee.

Le constructeur prepare:

- screen;
- config;
- polices.

### `_draw_centered_text(...)`

Dessine un texte centre horizontalement a une position `y`.

### `_fill_overlay(alpha=200)`

Cree une surface transparente noire et la dessine par-dessus l'ecran.

Utilisee pour pause.

### `PauseScreen`

Options:

- Resume;
- Return to Menu;
- Quit.

Le constructeur met `selection = 0`.

`handle_event()`:

- haut/W: option precedente;
- bas/S: option suivante;
- ESC: resume;
- enter/espace: retourne l'action choisie.

`render()`:

- overlay sombre;
- titre `PAUSED`;
- options.

### `NameEntryScreen`

Sert a entrer le nom pour le highscore.

Le constructeur stocke:

- score;
- buffer de texte vide.

`handle_event()`:

- enter: retourne le nom valide;
- backspace: supprime un caractere;
- escape: retourne `"Player"` si vide;
- caractere alphanumerique ou espace: ajoute au buffer si moins de 10 chars.

`render()`:

- titre;
- score;
- prompt;
- nom en cours;
- consigne.

### `GameOverScreen`

Affiche game over ou victoire.

`handle_event()`:

- enter/espace: continue;
- escape: menu.

`render()`:

- fond;
- titre `YOU WIN!` ou `GAME OVER`;
- score final;
- instruction.

### `InstructionsScreen`

Contient `LINES`, un tuple de lignes de texte.

`handle_event()`:

- n'importe quel `KEYDOWN` retourne menu.

`render()`:

- fond;
- titre;
- lignes d'instructions;
- indication de retour.

### `HighscoresScreen`

Affiche top 10.

Le constructeur recoit la liste de highscores.

`handle_event()`:

- n'importe quelle touche retourne menu.

`render()`:

- fond;
- titre;
- message si aucun score;
- sinon liste formatee;
- instruction de retour.

---

# 10.14 `pacman/ui/hud.py`

## Role du fichier

Ce fichier contient une classe `HUD` simple.

Dans le projet actuel, `Renderer.render_hud()` fait deja le travail principal.
`HUD` reste comme wrapper/ancienne separation possible.

## Lecture dans l'ordre

Imports:

- `pygame`.

### Classe `HUD`

Le constructeur stocke:

- screen;
- config;
- font.

### `render(score, lives, level, time_left)`

Dessine:

- rectangle du haut;
- ligne de separation;
- texte score/vies/niveau/temps.

---

# 10.15 `pacman/__init__.py`

Ce fichier marque `pacman` comme package Python.

Il contient:

```python
__version__ = "1.0.0"
```

Cela permet de connaitre la version du package.

---

# 10.16 `pacman/entities/__init__.py`

Ce fichier marque `pacman/entities` comme sous-package.

Il contient seulement une docstring.

---

# 10.17 `pacman/assets/__init__.py`

Ce fichier marque `pacman/assets` comme package.

Il documente le fait que la version actuelle n'a pas besoin d'assets externes.

Actuellement, le jeu dessine les sprites et le texte avec `pygame` plutot que de
charger des images, des sons ou des polices depuis ce dossier.

---

# 10.18 `Makefile`

## Role

Le `Makefile` donne des raccourcis.

### Variables

`PYTHON := python3`

Permet de changer facilement l'interpreteur.

`VENV_DIR := venv`

Nom potentiel de virtualenv, meme si pas vraiment utilise dans les targets.

`MYPY_FLAGS`

Options strictes pour `mypy`.

### Target `help`

Affiche les commandes disponibles.

### Target `install`

Installe:

1. le wheel `mazegenerator`;
2. les dependances de `requirements.txt`.

### Target `run`

Lance:

```bash
python3 pac-man.py config.json
```

### Target `debug`

Lance le jeu sous `pdb`, le debugger Python.

### Target `clean`

Supprime:

- `__pycache__`;
- `.pyc`;
- `.mypy_cache`;
- `.pytest_cache`.

### Target `lint`

Lance:

- `flake8`;
- `mypy`.

### Target `lint-strict`

Lance `mypy --strict`.

### Target `test`

Lance les tests en mode:

```bash
SDL_VIDEODRIVER=dummy
```

Pourquoi?

Pour tester `pygame` sans vraie fenetre graphique.

---

# 10.19 `pyproject.toml`

## Role

Ce fichier donne des informations de packaging et configure les outils.

### `[build-system]`

Indique que le projet utilise `setuptools` et `wheel`.

### `[project]`

Contient:

- nom;
- version;
- description;
- auteurs;
- version Python;
- dependances.

### `[project.optional-dependencies]`

Dependances de dev:

- `pytest`;
- `flake8`;
- `mypy`;
- `pyinstaller`.

### `[tool.mypy]`

Config du type checker.

Points importants:

- Python 3.10;
- warnings sur retours `Any`;
- ignore missing imports;
- typed defs obligatoires.

### `[tool.pytest.ini_options]`

Indique a pytest:

- dossier de tests;
- pattern des fichiers.

---

# 10.20 `requirements.txt`

Liste les dependances installees par `make install`.

Contenu:

- `pygame`;
- `pytest`;
- `flake8`;
- `mypy`;
- `pyinstaller`.

`mazegenerator` est installe depuis le wheel local, pas depuis PyPI.

---

# 10.21 `config.json`

## Role

Fichier modifiable pour regler le jeu sans changer le code.

Sections:

- highscore;
- maze generation;
- player;
- level progression;
- scoring;
- ghosts;
- display;
- UI colors.

Les fausses cles qui commencent par `"# ..."` servent de commentaires visuels.

Le parser les ignore.

Valeurs importantes:

- `width`: largeur brute du maze;
- `height`: hauteur brute du maze;
- `seed`: seed du niveau 1;
- `lives`: vies de depart;
- `player_speed`: vitesse joueur;
- `ghost_speed`: vitesse fantomes;
- `frightened_duration`: duree du power-up;
- `respawn_delay`: delai de respawn fantome mange;
- `fps`: frames par seconde.

---

# 10.22 `pac-man.spec`

## Role

Fichier pour PyInstaller.

Il dit comment construire l'executable.

Elements importants:

- script principal: `pac-man.py`;
- datas: `config.json` et `pacman/assets`;
- hiddenimports: `mazegenerator`;
- nom de l'executable: `pac-man`;
- `console=False`: pas de console ouverte avec l'application graphique.

---

# 10.23 `tests/test_engine.py`

## Role

Tests de la logique moteur.

Ils verifient:

- parsing config;
- defaults;
- JSON invalide;
- scoring;
- cheats;
- conversion maze;
- collisions murs;
- fantomes;
- update global;
- collecte pacgum;
- fantome eaten qui ne tue pas.

Pourquoi c'est utile pour la defense?

Ca prouve qu'on a teste les comportements critiques sans avoir besoin de jouer
manuellement a chaque fois.

---

# 10.24 `tests/test_ui.py`

## Role

Tests de l'UI et des highscores sans interaction.

Il force:

```python
SDL_VIDEODRIVER=dummy
```

Cela permet a `pygame` de fonctionner sans vraie fenetre.

Tests importants:

- validation de nom;
- persistence highscore;
- recovery fichier corrompu;
- top 10;
- import/creation des classes UI.

---

## 11. Questions probables en defense et reponses

### Pourquoi avoir separe moteur et UI?

Pour garder un code testable et propre.

Le moteur calcule les regles du jeu. L'UI dessine seulement. Comme ca, les tests
peuvent verifier `Game`, `Player`, `Ghost`, `Scoring` sans ouvrir une fenetre.

### Pourquoi BFS pour les fantomes?

Parce que le labyrinthe est une grille non ponderee. Chaque mouvement coute 1.
BFS donne donc le plus court chemin simplement et sans heuristique.

### Pourquoi pas A*?

A* aurait marche, mais BFS suffit:

- labyrinthe petit;
- couts uniformes;
- plus simple;
- plus facile a expliquer;
- garantit le plus court chemin.

### Pourquoi pas Dijkstra?

Dijkstra est utile quand les couts sont differents. Ici, tous les deplacements
ont le meme cout. BFS est plus adapte.

### Pourquoi convertir le maze en `(2W+1)x(2H+1)`?

Parce que le generateur donne des cellules avec des murs encodes en bits.
Pour un Pac-Man, il faut des murs physiques entre les cellules. Le scaling
`2W+1` permet de representer les cellules, les couloirs entre cellules et la
bordure.

### Comment les collisions fonctionnent?

On compare la position entiere de Pac-Man avec chaque fantome.

- Si positions differentes: rien.
- Si fantome frightened: Pac-Man mange le fantome.
- Si fantome eaten: il ne tue pas.
- Si invincible ou grace period: collision ignoree.
- Sinon Pac-Man perd une vie.

### Pourquoi une grace period?

Pour eviter une mort immediate au spawn ou apres respawn.

Sans ca, un fantome proche pourrait tuer le joueur instantanement.

### Comment le score des fantomes marche?

Un multiplicateur commence a 1.

Chaque fantome mange donne:

```text
points_per_ghost * multiplicateur
```

Puis le multiplicateur double jusqu'a 8.

Donc avec 200 points de base:

```text
200, 400, 800, 1600
```

### Comment le jeu sait qu'un niveau est fini?

`Game` garde `_remaining_pacgums`.

Quand Pac-Man mange une pacgum ou super-pacgum, ce compteur diminue.

Quand il atteint 0:

- si niveau suivant existe, `next_level()`;
- sinon `WIN`.

### Que se passe-t-il si `config.json` est faux?

Le parser log un warning et utilise les valeurs par defaut.

Le but est de ne pas crasher.

### Que se passe-t-il si le highscore JSON est corrompu?

`HighscoreManager.load()` attrape l'erreur, log un warning, et recommence avec
une liste vide.

### Pourquoi utiliser des enums?

Pour eviter les strings magiques et rendre les etats lisibles:

- `GameMode.PLAY`;
- `GhostState.FRIGHTENED`;
- `MenuItem.START_GAME`.

### Pourquoi les fantomes ont plusieurs comportements?

Pour eviter que tous les fantomes fassent exactement la meme chose.

Cela rend le jeu plus interessant:

- un poursuit;
- un anticipe;
- un est aleatoire;
- un va vers son coin.

### Que fait le cheat `p`?

Il declenche un power-up sans manger de super-pacgum.

Utile en defense pour montrer rapidement:

- frightened mode;
- fantomes bleus;
- score 200/400/800/1600.

### Pourquoi le renderer cache les murs?

Les murs ne bougent pas pendant un niveau.

Les dessiner une fois dans une surface cachee est plus efficace que les
redessiner entierement a chaque frame.

### Pourquoi `dt` est clamp?

Pour eviter les gros sauts de mouvement si le jeu freeze ou si la fenetre perd
le focus.

### Pourquoi `GameState` est utile?

Il sert de contrat entre moteur et UI.

Le moteur expose l'etat, l'UI le lit.

### Pourquoi il y a des tests?

Pour verifier automatiquement les cas critiques:

- config mauvaise;
- scoring;
- collisions;
- maze;
- highscores;
- import UI.

---

## 12. Scenarios de demo pendant la defense

### Scenario 1: lancement normal

1. Lancer `make run`.
2. Montrer le menu.
3. Aller dans instructions.
4. Revenir au menu.
5. Lancer une partie.

Ce que tu expliques:

> `pac-man.py` gere les etats menu/instructions/play. Le menu est dans
> `pacman/ui/menu.py`, le jeu dans `pacman/game.py`.

### Scenario 2: mouvement et score

1. Deplacer Pac-Man.
2. Manger des pacgums.
3. Montrer que le score augmente.

Ce que tu expliques:

> Le clavier donne une direction a `Game.update()`. `Player.update()` bouge
> Pac-Man, puis `_apply_pacgum_pickup()` remplace la pacgum par un couloir et
> ajoute les points via `Scoring`.

### Scenario 3: super-pacgum

1. Utiliser le cheat `p` si besoin.
2. Montrer que les fantomes deviennent bleus.
3. Manger un fantome.

Ce que tu expliques:

> Tous les fantomes passent en `GhostState.FRIGHTENED`. S'ils entrent en
> collision avec Pac-Man, ils passent en `EATEN` et le score augmente avec le
> multiplicateur.

### Scenario 4: pause

1. Appuyer sur `ESC`.
2. Montrer pause.
3. Reprendre.

Ce que tu expliques:

> L'etat global dans `pac-man.py` passe de `play` a `pause`. Le moteur ne
> continue pas a avancer pendant que l'ecran pause traite les evenements.

### Scenario 5: highscore

1. Finir une partie ou perdre.
2. Entrer un nom.
3. Montrer le menu/highscores.

Ce que tu expliques:

> `HighscoreManager` valide le nom, garde le top 10, trie les scores et
> sauvegarde dans un fichier JSON.

### Scenario 6: tests

1. Lancer `make test`.
2. Montrer les tests qui passent.

Ce que tu expliques:

> Les tests moteur ne dependent pas de la fenetre. Les tests UI utilisent
> `SDL_VIDEODRIVER=dummy`.

---

## 13. Explication simple des structures de donnees

### Liste de listes

La grille est une liste de lignes.

Exemple:

```python
grid[y][x]
```

Pourquoi `y` avant `x`?

Parce que la premiere dimension est la ligne, donc l'axe vertical.

### Tuple position

Une position est souvent:

```python
(x, y)
```

Un tuple est pratique car il est immuable et facile a comparer.

### Dictionnaire config

La config est un dictionnaire:

```python
config["lives"]
config.get("player_speed", 5.0)
```

`get` permet de donner une valeur par defaut si la cle manque.

### Enum

Un enum donne un ensemble ferme de valeurs.

Exemple:

```python
GhostState.FRIGHTENED
```

C'est plus clair que:

```python
"frightened"
```

---

## 14. Explication de la grille et des coordonnees

Dans le jeu:

- `x` augmente vers la droite;
- `y` augmente vers le bas.

Directions:

| Direction | Tuple |
|---|---|
| droite | `(1, 0)` |
| gauche | `(-1, 0)` |
| bas | `(0, 1)` |
| haut | `(0, -1)` |

Pour avancer:

```python
new_x = x + dx
new_y = y + dy
```

Pour lire une tile:

```python
tile = grid[y][x]
```

---

## 15. Ordre important dans `Game.update()`

L'ordre n'est pas au hasard.

1. Cheats de skip/power-up avant mouvement.
2. Extra lives avant collisions.
3. Eat freeze avant mouvement.
4. Input joueur avant update joueur.
5. Update joueur avant fantomes.
6. Pickup pacgum apres mouvement joueur.
7. Collisions apres update des entites.
8. Temps et fin de niveau a la fin.

Pourquoi cet ordre?

Parce qu'il evite des comportements incoherents.

Exemple:

- Si on verifiait les collisions avant de bouger Pac-Man, on raterait une
  collision qui arrive pendant la frame.
- Si on mangeait la pacgum avant de bouger, Pac-Man mangerait la case d'avant.
- Si on changeait de niveau au milieu sans retourner, on risquerait d'utiliser
  une grille remplacee dans la meme frame.

---

## 16. Points forts a mettre en avant

- Architecture propre: moteur separe de l'UI.
- Gestion robuste des erreurs.
- Config validee et clamp.
- Maze converti correctement en vraie grille jouable.
- Fantomes avec plusieurs comportements.
- BFS justifie par grille non ponderee.
- Score avec multiplicateur classique.
- Highscores persistants et nettoyes.
- Tests automatises.
- Cheats utiles pour l'evaluation.
- Rendu optimise avec cache de murs et sprites fantomes.

---

## 17. Limites connues a assumer

Il vaut mieux etre honnete en defense.

Limites possibles:

- Pas d'audio.
- Les fantomes `EATEN` ne retournent pas visuellement a la maison; ils respawn
  apres un timer.
- Les sprites sont dessines avec primitives `pygame`, pas avec des images.
- Le labyrinthe est procedural et peut differer d'un Pac-Man arcade exact.
- `hud.py` est un wrapper simple alors que le renderer a sa propre methode HUD.

Formulation utile:

> On a privilegie une architecture claire, testable et robuste. Certaines
> features cosmetiques comme l'audio ou les assets externes ont ete laissees de
> cote pour garder le scope maitrise.

---

## 18. Checklist avant defense

Avant la defense:

- lancer `make test`;
- lancer `make run`;
- verifier que le menu s'affiche;
- tester une partie;
- tester `ESC`;
- tester `p` pour frightened mode;
- tester `i` invincible;
- tester `l` skip level;
- ouvrir `config.json` et connaitre les cles importantes;
- savoir expliquer BFS;
- savoir expliquer `(2W+1)x(2H+1)`;
- savoir expliquer `GameState`;
- savoir expliquer pourquoi le moteur ne depend pas de `pygame`;
- savoir montrer les tests.

---

## 19. Mini script oral possible

Tu peux dire:

> Le projet est organise autour d'une separation moteur/UI. Le moteur contient
> toute la logique: generation du labyrinthe, joueur, fantomes, collisions,
> score et niveaux. L'UI utilise pygame pour dessiner un snapshot `GameState`.
>
> Le labyrinthe vient d'une bibliotheque externe qui renvoie des cellules avec
> des murs encodes par bitmask. On convertit ca en grille `(2W+1)x(2H+1)` pour
> avoir de vrais murs entre les cellules. Cette grille est ensuite utilisee par
> Pac-Man et les fantomes.
>
> Pour les fantomes, on a plusieurs comportements. Les fantomes qui poursuivent
> utilisent BFS, parce que la grille n'est pas ponderee et BFS donne le plus
> court chemin. En frightened mode, ils ralentissent et cherchent plutot a
> s'eloigner de Pac-Man.
>
> Le projet gere aussi les highscores persistants, la config robuste, les
> erreurs sans traceback utilisateur, et des tests automatises.

---

## 20. Resume ultra court des algorithmes

| Probleme | Solution | Pourquoi |
|---|---|---|
| Labyrinthe brut pas directement jouable | Conversion `(2W+1)x(2H+1)` | murs entre cellules representes |
| Trouver chemin fantome -> Pac-Man | BFS | plus court chemin en grille non ponderee |
| Fantome effraye | maximiser distance Manhattan + hasard | fuit le joueur sans etre trop robotique |
| Mouvement fluide | `_move_progress` + `visual_pos` | evite les sauts case par case |
| Input agreable | direction bufferisee | permet d'anticiper un virage |
| Config invalide | defaults + clamp | evite crash |
| Highscore corrompu | validation + recovery | evite crash |
| Rendu performant | wall cache + sprite cache | evite de redessiner statique |

---

## 21. Ce qu'il faut savoir expliquer si on te montre une ligne au hasard

### Si on te montre `config.get("x", default)`

Ca lit une valeur dans la config. Si elle n'existe pas, on utilise `default`.

### Si on te montre `max(0.0, value)`

Ca evite d'avoir une valeur negative.

### Si on te montre `min(a, b)`

Ca prend la plus petite valeur.

### Si on te montre `Enum`

Ca represente un ensemble fixe d'etats ou options.

### Si on te montre `@dataclass`

Ca cree automatiquement une classe simple pour stocker des donnees.

### Si on te montre `field(default_factory=list)`

Ca cree une nouvelle liste pour chaque instance, au lieu de partager une liste.

### Si on te montre `pygame.Surface`

C'est une image ou zone de dessin en memoire.

### Si on te montre `blit`

Ca copie une surface sur une autre.

### Si on te montre `pygame.draw.rect`

Ca dessine un rectangle.

### Si on te montre `pygame.draw.circle`

Ca dessine un cercle.

### Si on te montre `pygame.display.flip()`

Ca affiche la frame dessinee.

### Si on te montre `deque`

C'est une file efficace, utilisee pour BFS.

### Si on te montre `visited`

C'est l'ensemble des cases deja vues par BFS, pour eviter les boucles infinies.

### Si on te montre `return None`

Ca veut dire "pas de resultat".

### Si on te montre `Optional[...]`

Ca veut dire que la valeur peut etre du type donne ou `None`.

---

## 22. Ordre de lecture recommande pour reviser

Si tu revises le code, lis dans cet ordre:

1. `README.md`
2. `config.json`
3. `pac-man.py`
4. `pacman/config.py`
5. `pacman/maze_loader.py`
6. `pacman/entities/player.py`
7. `pacman/entities/ghost.py`
8. `pacman/scoring.py`
9. `pacman/game.py`
10. `pacman/ui/window.py`
11. `pacman/ui/renderer.py`
12. `pacman/ui/menu.py`
13. `pacman/ui/screens.py`
14. `pacman/highscore.py`
15. `tests/test_engine.py`
16. `tests/test_ui.py`

Pourquoi cet ordre?

Parce qu'il commence par le contexte, puis le moteur, puis l'UI, puis les tests.

---

## 23. Reponses rapides aux questions pieges

### Est-ce que le moteur importe pygame?

Non. `pygame` est limite a l'UI et au point d'entree.

### Est-ce que le renderer change le score?

Non. Le renderer lit le `GameState` et dessine.

### Est-ce que BFS est recalcule souvent?

Oui, au moment ou le fantome choisit sa direction. La grille est petite, donc
c'est acceptable.

### Est-ce que les fantomes peuvent traverser les murs?

Non, ils utilisent `_is_blocked()` comme Pac-Man.

### Est-ce que Pac-Man peut aller en diagonale?

Non, `set_direction()` refuse les directions dont `abs(dx) + abs(dy) != 1`.

### Est-ce que le score peut devenir negatif?

Non, on ajoute seulement des points. Les highscores refusent aussi les scores
negatifs.

### Est-ce que le highscore crash si le fichier est mauvais?

Non, il repart avec une liste vide.

### Est-ce que la config crash si une cle manque?

Non, elle utilise les valeurs par defaut.

### Pourquoi `WALL_42`?

Le generateur peut produire des cellules speciales completement fermees. Le
renderer les colore differemment pour montrer une decoration liee a 42.

### Pourquoi les spawns sont dans une liste?

Parce que la fonction de conversion retourne:

- index 0: Pac-Man;
- index 1 a 4: fantomes.

---

## 24. Conclusion

Le projet est defendable autour de trois idees principales:

1. Une architecture claire: moteur separe de l'UI.
2. Des algorithmes adaptes: conversion de grille, BFS, machines a etats,
   interpolation.
3. De la robustesse: config validee, highscores securises, tests, erreurs
   propres.

Si tu dois retenir une phrase:

> Le jeu fonctionne parce que le moteur calcule proprement un etat de jeu, l'UI
> se contente de l'afficher, et les fantomes prennent leurs decisions avec des
> algorithmes simples mais adaptes a une grille de Pac-Man.
