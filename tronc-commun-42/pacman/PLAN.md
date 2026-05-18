# Plan Pacman — Binôme A / B

Plan A→Z pour faire le projet à deux. **A** = moteur (logique, données, IA), **B** = présentation (rendu, menus, packaging). Les zones partagées ont un owner clair.

---

## Stack
- **Python 3.10+**, `pygame` (le sujet dit "MLX ou similaire" — pygame est le choix raisonnable en Python).
- Package maze imposé : `mazegenerator.MazeGenerator(size=(w,h), perfect=False, seed=...)` → retourne `maze` : grille `list[list[int]]` où chaque cellule est un bitmask de murs (N=1, E=2, S=4, W=8). Le loader doit traduire ça en cellules `WALL / CORRIDOR / PACGUM / SUPER_PACGUM / SPAWN`.
- `flake8` + `mypy` (les deux règles sont obligatoires dans le Makefile).
- `itch.io` pour la livraison packagée (plus simple que Steam) via `pyinstaller`.

---

## Phase 0 — Setup commun (Jour 1, en pair)

- Créer repo + structure :
  ```
  pacman/
    pac-man.py              # entrypoint
    pacman/
      __init__.py
      config.py             # A
      maze_loader.py        # A
      entities/             # A (player, ghost, pacgum)
      game.py               # A (game loop, états)
      scoring.py            # A
      highscore.py          # B
      ui/                   # B (menus, hud, screens)
      assets/               # B (sprites, sons, fonts)
      cheat.py              # partagé
    tests/
    project_management/     # docs Gantt, risques, etc.
    Makefile
    config.json
    README.md
    .gitignore
    pyproject.toml          # deps + pyinstaller spec
  ```
- Écrire `Makefile` (install/run/debug/clean/lint/lint-strict).
- Définir le schéma `config.json` ensemble (clés, valeurs par défaut).
- Définir l'interface entre moteur et UI : un objet `GameState` (read-only depuis l'UI) avec `score`, `lives`, `level`, `time_left`, `pacman.pos/dir`, `ghosts[]`, `grid`, `mode` (PLAY/PAUSE/GAMEOVER/WIN).
- Choisir outil de PM (Trello/GitHub Projects) + faire un Gantt rapide.

**Livrable** : repo bootstrap, `make lint` passe sur un squelette vide.

---

## Phase 1 — Cœur jouable (Jours 2–5)

### Personne A — Moteur de jeu
1. **`config.py`** : parser JSON avec commentaires (strip des lignes `#` avant `json.loads`), validation, clamp aux défauts, jamais de traceback. Messages d'erreur clairs.
2. **`maze_loader.py`** : appeler `MazeGenerator(size=(w,h), perfect=False, seed=cfg.seed)`, convertir le bitmask en grille de tiles jouables. Placer 4 super-pacgums aux coins, pacgums dans les corridors restants, spawn joueur au centre, 4 spawns fantômes aux coins. Seed fixe pour level 1, aléatoire ensuite.
3. **`entities/player.py`** : position, direction, vitesse, vies, demande de changement de direction (input bufferisé).
4. **`entities/ghost.py`** : 4 fantômes avec comportements distincts (chase = direction du joueur, ambush = devant le joueur, random, scatter coin). États : CHASE / FRIGHTENED / EATEN. Respawn coin après 5–10s.
5. **`game.py`** : boucle `update(dt)` : collisions murs, pickup pacgum/super-pacgum, collisions joueur/fantôme, timer niveau, transition de niveau, fin de partie.
6. **`scoring.py`** : score, vies, multiplicateur fantômes consécutifs.
7. **`cheat.py`** : touches secrètes — invincibilité, skip niveau, freeze fantômes, +1 vie, vitesse x2.
8. Tests pytest sur : parsing config, conversion maze, mouvement bloqué par mur, pickup, transition niveau.

### Personne B — Présentation & persistance
1. **`ui/window.py`** : fenêtre pygame, horloge, gestion événements clavier, dispatch vers le moteur.
2. **`ui/renderer.py`** : dessine la grille (mur/corridor/pacgum), pacman animé (waka), 4 fantômes colorés, mode frightened (bleu clignotant).
3. **`ui/menu.py`** : main menu (Start / Highscores / Instructions / Exit) navigable au clavier.
4. **`ui/hud.py`** : score, vies, niveau, timer toujours visibles.
5. **`ui/screens.py`** : pause, game over, victory, saisie de nom (10 chars, alphanum + espace).
6. **`highscore.py`** : load/save JSON, top 10, robust aux fichiers corrompus/absents, validation nom + score.
7. Assets : sprites simples (peu importe la qualité), font, éventuellement sons.
8. Tests pytest sur : highscore (corruption, troncature top 10, validation nom).

**Synchro de fin de phase** : pacman bouge dans un maze, mange les pacgums, fantômes le poursuivent, vies/score affichés, on peut perdre/gagner un niveau.

---

## Phase 2 — Intégration & polish (Jours 6–7)

| Tâche | Owner |
|---|---|
| Brancher menu → start game → game over → enter name → highscore → menu | B |
| Brancher pause (ESC) | B |
| Enchaînement 10 niveaux + difficulté (vitesse fantômes ↑) | A |
| Comportements fantômes différenciés finalisés | A |
| Cheat mode visible à l'écran (overlay quand actif) | partagé |
| Gestion timer niveau dépassé (choix : reset niveau) | A |
| Tester avec **un autre** package A-Maze-ing (un binôme voisin) | ensemble |
| Faire crasher volontairement la config pour vérifier 0 traceback | ensemble |

---

## Phase 3 — Livraison (Jour 8)

### Personne A — Qualité & doc technique
- `make lint` et `make lint-strict` propres.
- Type hints partout, docstrings PEP 257.
- README sections : Description, Instructions, Configuration, Highscore, **Maze Generation**, Implementation, **General Software Architecture** (diagramme modules/classes), Resources (+ usage IA).
- Plan de test d'acceptation dans `project_management/`.

### Personne B — Packaging & déploiement
- Script `pyinstaller` → exécutable Linux (et Windows si possible).
- Push sur **itch.io** en *unlisted/private*, build téléchargeable et lançable.
- README sections : Resources, instructions d'install/lancement du package itch.
- Capture d'écran / preview sur la page itch.

### Ensemble
- `project_management/` : Gantt vs réel, qui a fait quoi, risques + mitigations, blocages, décisions clés.
- README première ligne : *This project has been created as part of the 42 curriculum by <login_A>, <login_B>.*
- Relecture croisée du code de l'autre → chacun doit pouvoir défendre **tout** le projet (le sujet insiste : si vous ne savez pas expliquer, vous échouez).

---

## Risques à surveiller
- **Couplage moteur/UI** : si B touche au `GameState` ou A touche au rendu, vous allez vous marcher dessus. Tenir la frontière.
- **Package maze imposé** : il sera **réinstallé** au peer-review → ne jamais modifier le wheel, adapter le loader.
- **No traceback** : envelopper tous les entrypoints I/O dans try/except avec message clair.
- **Itch.io** : préparer le build 2 jours avant la deadline, pas la veille.
