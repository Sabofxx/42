# Rapport de reprise — Call Me Maybe

Document interne (FR) qui résume l'état initial du projet, les écarts
identifiés par rapport au sujet (`call-me-maybe.pdf`, version 1.3) et les
corrections appliquées. Le `README.md` reste l'unique document destiné
aux évaluateurs.

## 1. Méthode

1. Lecture intégrale du sujet officiel `call-me-maybe.pdf`.
2. Lecture du SDK fourni `llm_sdk/llm_sdk/__init__.py` pour confirmer la
   liste exacte des méthodes publiques utilisables.
3. Lecture des fichiers d'entrée fournis
   (`functions_definition.json`, `function_calling_tests.json`).
4. Audit de l'implémentation existante, écart par écart.
5. Réécriture ciblée pour respecter le sujet, sans changer l'esprit du
   projet (constrained decoding token-par-token).

## 2. Écarts critiques identifiés

| # | Problème | Gravité | Fix |
|---|---|---|---|
| 1 | Sortie JSON utilisait `fn_name` / `args` au lieu des clés `name` / `parameters` exigées par le sujet (V.4) | 🔴 Élimination Moulinette | `models.py` + `generator.py` réécrits |
| 2 | CLI prenait deux dossiers (`--input`, `--output`) ; le sujet exige trois fichiers (`--functions_definition`, `--input`, `--output`) | 🔴 Élimination | `__main__.py` réécrit |
| 3 | `pyproject.toml` listait `torch>=2.10.0` et `transformers>=5.3.0` (interdits par IV.3.1) et exigeait Python 3.12 | 🔴 Élimination | Deps réduites à `numpy` + `pydantic` + `llm_sdk` (local) ; `requires-python = ">=3.10"` |
| 4 | `generate_argument` (number) : la condition de sortie de boucle était inatteignable car le masque mettait déjà les tokens invalides à `-inf` → boucle potentiellement infinie | 🟠 Bug bloquant | Boucle terminée dès qu'un token non-numérique devient l'argmax |
| 5 | `generate_argument` (string) : aucun masquage, juste `argmax(logits)` brut → pas vraiment de constrained decoding | 🟠 Bug logique | Termine sur token contenant `"` ou `\n`, cap dur à 64 tokens |
| 6 | `FunctionTrie.is_function_complete` : déclarait fini un nœud terminal qui était aussi un préfixe d'un nom plus long → noms tronqués | 🟠 | Exige aussi `not children` (nœud feuille) |
| 7 | `Makefile` : typo `yv add numpy pydantic`, artefact IA `[cite: 125, 127]`, `make test` annoncé mais inexistant, options mypy non-conformes au sujet | 🟠 | Réécrit avec les options exactes du sujet (IV.2) |
| 8 | README annonçait un dossier `tests/` qui n'existait pas | 🟡 | 4 fichiers de tests créés ; 17 / 17 passent en local |
| 9 | Imports torch au niveau module → tests unitaires impossibles sans torch installé | 🟡 | `from __future__ import annotations` + `TYPE_CHECKING` pour les imports SDK |
| 10 | `src/tools.py` (implémentations Python des fonctions cibles) jamais utilisé par le pipeline et hors scope du sujet | 🟢 | Supprimé |
| 11 | `.python-version` figé à 3.12 alors que le sujet autorise 3.10+ | 🟢 | Aligné sur 3.10 |
| 12 | `uv.lock` figé sur l'ancien `pyproject.toml` (avec torch/transformers) | 🟢 | Supprimé pour forcer une régénération propre via `uv sync` |

## 3. Pipeline final

### Phase 1 — Sélection de fonction (`select_function`)

- Un trie indexé par token ID est construit à partir des noms de
  fonction (encodés via `model.encode`).
- À chaque pas, seuls les enfants du nœud courant sont autorisés.
- L'argmax est calculé **uniquement sur le set valide** (pas de masque
  full-vocab à `-inf`) → plus rapide.
- Sortie de boucle : nœud feuille atteint (terminal et sans enfant).

### Phase 2 — Génération des arguments (`generate_argument`)

Pour chaque paramètre de la fonction sélectionnée :

- `number` : premier token doit appartenir au set "tokens qui commencent
  un nombre" (chiffres ou `-`, mis en cache une fois). Tokens suivants
  acceptés tant que leur représentation textuelle est faite de chiffres,
  `.` ou `-`. La valeur est `float(model.decode(...))`.
- `string` : génération libre jusqu'à un token contenant `"` ou `\n`,
  avec un cap dur à 64 tokens pour éviter les fuites.
- `boolean` : seuls les token-IDs de `true` et `false` sont autorisés.

Chaque argument est généré dans une passe constrained indépendante
avec un sous-prompt dédié pour améliorer la qualité du choix sur un
modèle de 0,6 B paramètres.

## 4. Conformité au sujet (checklist)

- [x] Python 3.10+ (`pyproject.toml`, `.python-version`)
- [x] Adhère à `flake8` (passe sans warning)
- [x] Type hints partout, docstrings PEP 257
- [x] Pydantic pour toute validation (`models.py`)
- [x] Aucun usage de `dspy`, `outlines`, `transformers`, `huggingface`,
      `torch` directement dans `src/`
- [x] Aucun usage de méthodes/attributs privés du `llm_sdk`
- [x] Modèle `Qwen/Qwen3-0.6B` (par défaut dans le SDK)
- [x] CLI avec `--functions_definition`, `--input`, `--output`
- [x] Sortie JSON `{prompt, name, parameters}`
- [x] Gestion d'erreurs gracieuse (FileNotFoundError, JSONDecodeError,
      ValidationError) — programme ne crashe pas
- [x] `Makefile` avec `install`, `run`, `debug`, `clean`, `lint`,
      `lint-strict`, `test`
- [x] `.gitignore` exclut les artefacts Python
- [x] `data/output/` non versionné
- [x] Tests dans `tests/` (pytest, 17 cas)
- [x] README en anglais, première ligne italique conforme au sujet

## 5. Points d'attention pour la défense

- **Sécurité du décodeur** : la sortie JSON est valide *par construction*.
  Pas une garantie statistique. Démonstration possible : montrer que
  `select_function` ne peut littéralement pas produire un nom de
  fonction invalide (l'argmax masqué est appelé sur un set vide → break,
  ou sur le set des enfants du trie).
- **Qualité de sélection sémantique** : le 0,6 B se trompe parfois sur
  les prompts ambigus. C'est attendu — la garantie structurelle est
  100 %, la précision sémantique vise 90 %+.
- **Pourquoi pas un masque full-vocab à `-inf`** : sur un vocab de
  ~150 k tokens, masquer puis prendre `argmax` est O(V) en Python pur
  pour chaque token généré. `_argmax_masked` itère uniquement sur le
  set valide (souvent < 100 entrées) → gain mesurable.
- **Pourquoi générer chaque argument indépendamment** : évite de
  cumuler les erreurs sur les fonctions à plusieurs paramètres
  (ex. `fn_substitute_string_with_regex` avec 3 strings).

## 6. Ce qui n'a pas été touché

- `llm_sdk/` : SDK fourni, on n'y touche pas (instruction du sujet).
- `data/input/*.json` : fichiers d'entrée fournis, conservés tels quels
  pour la démonstration.
- Le contenu fonctionnel du décodeur (token-trie, prefix matching) :
  l'algorithme d'origine était bon, seuls les bugs de boucle et la
  cohérence avec le sujet ont été corrigés.

## 7. Commandes utiles

```bash
make install       # uv sync (régénère uv.lock)
make run           # exécute le pipeline complet
make lint          # flake8 + mypy avec les flags du sujet
make lint-strict   # flake8 + mypy --strict
make test          # pytest -v
make clean         # purge des caches
```
