# 🔬 Explication ligne par ligne du projet

On suit le **flot d'exécution réel** : ce qui se passe quand tu tapes une
commande, dans l'ordre où le programme rentre dans chaque fichier.

> Convention : `path/fichier.py:NN` indique le numéro de ligne dans ce fichier.

---

## 0. Point d'entrée : `uv run python -m student ...`

Quand tu lances `python -m student index ...`, Python :
1. Localise le **package** `student` (le dossier `src/student/`).
2. Exécute son fichier `__main__.py`.

### 📄 `src/student/__main__.py`

```python
from .cli import main

if __name__ == "__main__":
    main()
```

- **Ligne 1** : import relatif. Le `.` veut dire « depuis le même
  package ». On importe la fonction `main()` définie dans `cli.py`.
- **Ligne 3** : le test classique « est-ce que ce fichier est lancé
  directement ? ». Vrai dans le cas de `python -m student`. → on appelle
  `main()`.

---

## 1. `src/student/cli.py` — l'orchestrateur

### 1.1 Les imports (lignes 1-25)

```python
from __future__ import annotations
```
Active la syntaxe moderne pour les annotations (`list[int]` au lieu de
`List[int]`) même en Python 3.10. **Doit être en première ligne**.

```python
import json
import os
from typing import Optional
from tqdm import tqdm
```
- `json` : lecture/écriture des fichiers JSON.
- `os` : manipulation de chemins, création de dossiers.
- `Optional` : type `X | None`.
- `tqdm` : barres de progression.

```python
from .evaluate import evaluate as _evaluate
from .generator import get_generator
from .index import KnowledgeBase
from .models import (...)
```
On importe **uniquement** ce dont on a besoin depuis nos sous-modules.
Le `as _evaluate` renomme `evaluate` pour ne pas entrer en collision avec
la méthode `CLI.evaluate`.

### 1.2 Constantes (lignes 27-29)

```python
DEFAULT_RAW_DIR = "data/raw/vllm-0.10.1"
DEFAULT_INDEX_DIR = "data/processed"
DEFAULT_OUTPUT_DIR = "data/output"
```
Chemins par défaut. Permet à l'utilisateur de ne pas les retaper à chaque
commande.

### 1.3 Helper `_resolve_repo` (lignes 32-46)

```python
def _resolve_repo(raw_dir: str) -> str:
```
Quand on dézippe `vllm-0.10.1.zip`, on se retrouve avec
`data/raw/vllm-0.10.1/...`. Cette fonction est tolérante : si tu passes
`data/raw/` (qui ne contient qu'un sous-dossier), elle descend
automatiquement dans ce sous-dossier.

- `os.listdir(raw_dir)` : liste les entrées (fichiers + dossiers).
- `entries = [e for e in ... if not e.startswith(".")]` : filtre les
  fichiers cachés (`.git`, `.DS_Store`).
- On vérifie qu'il n'y a *qu'un* sous-dossier *et* aucun `.py`/`.md` à la
  racine → c'est probablement le wrapper du zip → on descend.

### 1.4 La classe `CLI`

C'est l'**objet exposé à Fire**. Chaque méthode publique devient une
commande shell.

#### 1.4.1 `CLI.index` (lignes 51-72)

```python
def index(
    self,
    repo_path: str = DEFAULT_RAW_DIR,
    save_directory: str = DEFAULT_INDEX_DIR,
    max_chunk_size: int = 2000,
    use_embeddings: bool = False,
    embedder_name: str = "sentence-transformers/all-MiniLM-L6-v2",
) -> str:
```

Quand on tape :
```
uv run python -m student index --max_chunk_size 2000
```
Fire mappe automatiquement `--max_chunk_size 2000` → `max_chunk_size=2000`.

Étapes internes :
1. `repo = _resolve_repo(repo_path)` → descend dans le bon sous-dossier.
2. Si le chemin n'existe pas → `FileNotFoundError` clair.
3. `kb = KnowledgeBase.build(...)` → c'est ici qu'on bascule dans
   `index.py` (voir §3).
4. `kb.save(save_directory)` → persiste l'index.
5. Imprime le message et le retourne (Fire affiche les valeurs de retour).

#### 1.4.2 `CLI.search` (lignes 74-91)

```python
kb = KnowledgeBase.load(index_directory)
chunks = kb.search(query, k=k, mode=mode)
```

- On **recharge** l'index sans le reconstruire (caching).
- `kb.search` dispatche entre BM25, dense, ou hybrid (cf §3.5).
- On transforme chaque `Chunk` interne en `MinimalSource` (le format
  imposé par le sujet) avant d'imprimer en JSON.

#### 1.4.3 `CLI.search_dataset` (lignes 93-127)

Le cœur de l'évaluation. Pour chaque question du dataset on lance une
recherche.

```python
for q in tqdm(dataset.rag_questions, desc="Searching", unit="q"):
    chunks = kb.search(q.question, k=k, mode=mode)
    retrieved = [MinimalSource(...) for c in chunks]
    results.append(MinimalSearchResults(...))
```
- `tqdm(...)` : affiche une barre de progression.
- À la fin on construit le `StudentSearchResults` (modèle pydantic) et
  on l'écrit en JSON avec `.model_dump_json(indent=2)` — c'est la forme
  exigée par le sujet (cf V.9).

#### 1.4.4 `CLI.answer` (lignes 129-141)

Une seule question : retrieve → générer la réponse.
- `gen = get_generator(...)` → singleton (cf §5).

#### 1.4.5 `CLI.answer_dataset` (lignes 143-184)

Variante batch. La subtilité : pour chaque source retournée par la
recherche, on **re-récupère le `Chunk` complet** (avec son texte) depuis
`kb.chunks_by_offset`, parce que `MinimalSource` ne contient *que* les
offsets, pas le texte.

```python
chunks_by_offset = {
    (c.file_path, c.first_character_index, c.last_character_index): c
    for c in kb.chunks
}
```
Un dict pour retrouver chaque chunk en O(1) par ses 3 coordonnées.

#### 1.4.6 `CLI.evaluate` (lignes 186-196)

Wrapper qui appelle `evaluate.evaluate(...)` et imprime le rapport.

### 1.5 `main()` (lignes 199-203)

```python
def main() -> None:
    import fire
    fire.Fire(CLI)
```
- L'import de Fire est *à l'intérieur* de `main()` : on évite l'import
  lourd quand on importe `cli` pour autre chose (tests).
- `fire.Fire(CLI)` lit `sys.argv`, instancie `CLI()`, et appelle la
  méthode demandée avec les bons arguments. Magie.

---

## 2. `src/student/models.py` — les contrats de données

Ces classes valident automatiquement les JSON qui entrent/sortent.

### 2.1 `MinimalSource` (lignes 11-15)

```python
class MinimalSource(BaseModel):
    file_path: str
    first_character_index: int
    last_character_index: int
```
- Hérite de `BaseModel` (pydantic). Le `BaseModel` génère :
  - `__init__` qui vérifie les types.
  - `.model_validate_json(...)` pour parser un JSON.
  - `.model_dump_json(...)` pour sérialiser.
- Si tu passes `first_character_index="abc"` → exception claire.

### 2.2 `UnansweredQuestion` (lignes 18-22)

```python
question_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
question: str
```
- `Field(default_factory=...)` : si `question_id` n'est pas fourni, on
  génère un UUID aléatoire. C'est `default_factory` (pas `default=`)
  parce que sinon **toutes les instances** partageraient le même UUID.

### 2.3 `AnsweredQuestion(UnansweredQuestion)` (lignes 25-28)

Hérite — donc a `question_id` et `question`, plus :
- `sources: List[MinimalSource]` : la vérité terrain pour le recall.
- `answer: str` : la réponse attendue.

### 2.4 `RagDataset` (lignes 31-33)

```python
rag_questions: List[Union[AnsweredQuestion, UnansweredQuestion]]
```
La liste peut contenir des deux types. Pydantic essaie d'abord
`AnsweredQuestion` (avec `sources`+`answer`), sinon `UnansweredQuestion`.

### 2.5 `MinimalSearchResults`, `MinimalAnswer` (lignes 36-43)

- `MinimalSearchResults` : ce que renvoie la **recherche**.
- `MinimalAnswer(MinimalSearchResults)` : recherche **+ réponse** générée.

### 2.6 `StudentSearchResults`, `StudentSearchResultsAndAnswer` (lignes 46-54)

Les enveloppes top-level que tu sauvegardes :
```python
class StudentSearchResults(BaseModel):
    search_results: List[MinimalSearchResults]
    k: int
```

---

## 3. `src/student/index.py` — le cœur du retrieval

C'est ici que les choses sérieuses se passent.

### 3.1 La classe `KnowledgeBase` (ligne 30)

Elle encapsule :
- `self.chunks` : la liste de tous les `Chunk`.
- `self.bm25` : l'objet `bm25s.BM25` indexé.
- `self.dense_embeddings` : matrice numpy (N_chunks × dim) ou `None`.
- `self.embedder_name` : nom du modèle d'embedding (pour reload).
- `self._embedder = None` : lazy — chargé à la première recherche dense.

### 3.2 `KnowledgeBase.build()` (lignes 47-68) — INDEXATION

C'est le cas chemin quand tu fais `python -m student index`.

```python
files = collect_files(repo_root, relative_to=repo_root)
```
→ entre dans `ingest.py:collect_files` (§4) qui retourne
`[(rel_path, content), ...]`.

```python
chunks = []
for rel_path, text in tqdm(files, desc="Chunking", unit="file"):
    chunks.extend(chunk_file(rel_path, text, max_chunk_size))
```
→ entre dans `chunking.py:chunk_file` (§5) pour chaque fichier.
`chunks.extend(...)` ajoute les chunks d'un fichier à la liste globale.

```python
corpus_tokens = tokenize_batch([c.text for c in chunks])
bm25 = bm25s.BM25()
bm25.index(corpus_tokens, show_progress=True)
```
- `tokenize_batch` (`tokenizer.py`) transforme chaque chunk en
  `["liste", "de", "tokens"]`.
- `bm25s.BM25().index(...)` calcule tous les TF, IDF, et longueurs
  moyennes. C'est l'étape la plus rapide grâce à `bm25s`.

```python
if use_embeddings:
    dense = _encode_corpus(chunks, embedder_name)
```
Bonus : encode tous les chunks avec sentence-transformers.

### 3.3 `_encode_corpus` (lignes 188-205)

```python
model = SentenceTransformer(model_name)
vectors = model.encode(texts, batch_size=64,
                       normalize_embeddings=True,
                       convert_to_numpy=True)
```
- `normalize_embeddings=True` → vecteurs de norme 1 → la similarité
  cosinus se calcule par simple produit scalaire.

### 3.4 Persistance : `save()` et `load()`

#### `save()` (lignes 72-91)
- Sauvegarde les chunks en JSON (texte + offsets).
- `self.bm25.save(bm25_dir)` : `bm25s` sait se sérialiser tout seul.
- `meta.json` retient le nom de l'embedder (pour le rechargement).
- `embeddings.npy` : matrice numpy.

#### `load()` (lignes 94-114)
Le miroir : recharge tout depuis le disque. **Pas de re-chunking.**

### 3.5 Les recherches

#### `search_bm25` (lignes 118-130)
```python
tokens = tokenize(query)
docs, scores = self.bm25.retrieve([tokens], k=min(k, len(self.chunks)))
```
- Le `[tokens]` est une **liste de queries** (batch). On en passe une
  seule, on récupère `docs[0]` et `scores[0]`.

#### `search_dense` (lignes 140-150)
```python
q_vec = embedder.encode([query], normalize_embeddings=True)
sims = self.dense_embeddings @ q_vec[0]
top_n = min(k, len(self.chunks))
idxs = np.argpartition(-sims, top_n - 1)[:top_n]
idxs = idxs[np.argsort(-sims[idxs])]
```
- `@` = produit matriciel numpy. Sur des vecteurs normalisés, c'est la
  cosine similarity.
- `np.argpartition(-sims, top_n-1)[:top_n]` : trouve les `top_n` plus
  grands scores en **O(N)** (plus rapide qu'un tri complet).
- Puis on trie *seulement* ces `top_n` par score décroissant.

#### `search_hybrid` (lignes 152-170) — **bonus**
RRF (Reciprocal Rank Fusion) :
```python
for rank, (idx, _) in enumerate(bm25_hits):
    scores[idx] = scores.get(idx, 0.0) + 1.0 / (rrf_k + rank + 1)
```
- Chaque chunk reçoit une contribution `1/(60 + rank)` de chacune des
  deux listes (BM25 et dense).
- Avantage : pas besoin de normaliser les scores BM25 vs cosinus.

#### `search` (lignes 172-186) — dispatcher
```python
if mode == "auto":
    mode = "hybrid" if self.dense_embeddings is not None else "bm25"
```
Choisit la méthode et retourne les **objets Chunk** complets (pas juste
les indices).

---

## 4. `src/student/ingest.py` — lecture des fichiers

### 4.1 Constantes (lignes 7-21)
- `ALLOWED_EXTENSIONS` : extensions à indexer.
- `SKIP_DIRS` : dossiers à ignorer (`.git`, `__pycache__`, etc.).

### 4.2 `iter_files(root)` (lignes 24-31)
```python
for dirpath, dirnames, filenames in os.walk(root):
    dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
```
- `os.walk` parcourt récursivement l'arbo.
- `dirnames[:] = ...` modifie la liste **en place** → c'est la
  technique standard pour dire à `os.walk` « n'entre pas dans ces
  sous-dossiers ».

### 4.3 `read_file_safely` (lignes 34-40)
```python
with open(path, "r", encoding="utf-8", errors="ignore") as fh:
    return fh.read()
```
- `errors="ignore"` : si le fichier n'est pas du vrai UTF-8 (rare), on
  ignore les octets invalides plutôt que crasher.
- `try/except OSError` : permission refusée, fichier disparu, etc.

### 4.4 `collect_files` (lignes 43-53)
Combine `iter_files` + `read_file_safely`. Retourne des **chemins
relatifs** (à `relative_to`) — c'est important : les ground truths du
sujet utilisent des chemins relatifs comme `"vllm/entrypoints/openai/api_server.py"`.

---

## 5. `src/student/chunking.py` — découpe intelligente

### 5.1 `Chunk` (lignes 14-22)
Dataclass qui contient texte + offsets + chemin.

### 5.2 `_split_oversized` (lignes 25-46)
Fenêtre glissante quand un chunk dépasse `max_chunk_size` :
```python
overlap = max_chunk_size // 10
step = max_chunk_size - overlap
pos = start
while pos < end:
    sub_end = min(pos + max_chunk_size, end)
    chunks.append(Chunk(file_path, pos, sub_end, text[pos:sub_end]))
    if sub_end >= end:
        break
    pos += step
```
- `overlap = 10 %` du max → on évite de couper une phrase en deux.
- À chaque itération on avance de `step = max - overlap`.

### 5.3 `chunk_python` (lignes 49-99) — la pièce maîtresse

```python
tree = ast.parse(text)
```
Parse Python en AST. Si la syntaxe est cassée → fallback texte.

```python
line_offsets = [0]
for line in lines:
    line_offsets.append(line_offsets[-1] + len(line) + 1)
```
- On précalcule **l'offset cumulé** de chaque ligne (en caractères, pas
  octets). Permet de convertir `(lineno, col)` → offset absolu en O(1).
- Le `+1` correspond au `\n`.

```python
top_level = [node for node in tree.body
             if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]
```
On ne garde **que** les fonctions et classes de premier niveau.

```python
for node in top_level:
    start = lc_to_offset(node.lineno, node.col_offset)
    end_lineno = getattr(node, "end_lineno", node.lineno) or node.lineno
    end = lc_to_offset(end_lineno, end_col)
    if start > cursor:
        # le "préambule" : tout ce qui était entre la fin du bloc
        # précédent et le début de celui-ci (imports, constantes, etc.)
        pre = text[cursor:start].strip()
        if pre:
            chunks.extend(_split_oversized(file_path, text, cursor, start, max_chunk_size))
    chunks.extend(_split_oversized(file_path, text, start, end, max_chunk_size))
    cursor = end
```
Une boucle "ratisse" tout le fichier : préambule + bloc, préambule +
bloc, ..., et un éventuel "post-ambule" final.

### 5.4 `chunk_markdown` (lignes 102-130)
Découpe par headers `#`, `##`, ... :
```python
section_starts = []
for i, line in enumerate(lines):
    if line.lstrip().startswith("#"):
        section_starts.append(line_offsets[i])
```
Si aucun header → on a quand même un chunk (le fichier entier, ou
sub-splitté).

### 5.5 `chunk_text` / `chunk_file`
- `chunk_text` : fallback sliding window pur.
- `chunk_file` : dispatcher par extension.

---

## 6. `src/student/tokenizer.py` — séparer le code

```python
_CAMEL_RE = re.compile(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])")
```
Cette regex matche les **frontières** dans `getUserName` →
`["get", "User", "Name"]` (et `HTTPServer` → `["HTTP", "Server"]`).

```python
_SPLIT_RE = re.compile(r"[^A-Za-z0-9]+")
```
Sépare sur tout ce qui n'est pas alphanumérique (espaces, ponctuation,
underscores, etc.).

```python
def tokenize(text: str) -> List[str]:
    parts = _SPLIT_RE.split(text)
    for part in parts:
        for sub in _CAMEL_RE.split(part):
            sub_lower = sub.lower()
            if len(sub_lower) < 2: continue
            if sub_lower in _STOPWORDS: continue
            tokens.append(sub_lower)
```
1. Split sur non-alphanum.
2. Pour chaque morceau, re-split sur camelCase.
3. Lowercase, filtre les tokens trop courts ou stopwords anglais.

**Pourquoi c'est important** : BM25 cherche des matches exacts. Sans
camelCase split, la requête `"openai server"` ne matcherait pas
`OpenAIServer`.

---

## 7. `src/student/generator.py` — le LLM

### 7.1 Lazy loading (lignes 22-39)
```python
def _load(self) -> None:
    if self._model is not None:
        return
    from transformers import AutoModelForCausalLM, AutoTokenizer
    import torch
    ...
```
- L'import lourd est **dans la méthode**, pas en haut du fichier → la
  CLI démarre vite si tu fais juste `search` (sans `answer`).
- Détection GPU :
  ```python
  dtype = torch.float16 if torch.cuda.is_available() else torch.float32
  ```
  Float16 sur GPU divise la mémoire par 2.

### 7.2 `_format_context` (lignes 41-51)
Compose le contexte qu'on passe au LLM :
```
[Source 1] vllm/foo.py (123-456):
def foo(): ...

[Source 2] docs/bar.md (0-200):
...
```
- Le préfixe `[Source 1] path (offsets):` aide le modèle à *citer*.
- Chaque chunk est tronqué à `max_context_length` caractères.

### 7.3 `generate` (lignes 53-89)
```python
messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}\n\n..."},
]
prompt = self._tokenizer.apply_chat_template(messages, tokenize=False,
                                             add_generation_prompt=True,
                                             enable_thinking=False)
```
- `apply_chat_template` insère les balises spéciales de Qwen.
- `enable_thinking=False` : Qwen3 peut faire du "thinking" (chaîne de
  réflexion interne) ; on coupe pour rester rapide et déterministe.

```python
with torch.no_grad():
    output = self._model.generate(**inputs, max_new_tokens=256,
                                  do_sample=False, temperature=0.0,
                                  pad_token_id=self._tokenizer.eos_token_id)
```
- `torch.no_grad()` : on n'entraîne pas → pas besoin de calculer les
  gradients → économie de RAM.
- `do_sample=False` : génération gloutonne déterministe.

```python
generated = output[0][inputs["input_ids"].shape[-1]:]
text = self._tokenizer.decode(generated, skip_special_tokens=True).strip()
```
`output` contient `prompt_tokens + generated_tokens`. On ne décode que
la partie générée.

### 7.4 `get_generator` (lignes 92-101)
Singleton : on ne charge le modèle qu'**une fois** par processus.

---

## 8. `src/student/evaluate.py` — la métrique recall@k

### 8.1 `overlap_ratio` (lignes 36-44)
```python
truth_len = max(1, truth.last_character_index - truth.first_character_index)
lo = max(retrieved.first_character_index, truth.first_character_index)
hi = min(retrieved.last_character_index, truth.last_character_index)
inter = max(0, hi - lo)
return inter / truth_len
```
- `[lo, hi]` = intervalle d'intersection.
- `inter` = longueur d'intersection (≥ 0).
- Ratio = `inter / longueur_de_la_truth`.

### 8.2 `question_recall` (lignes 47-58)
```python
for t in truth:
    for r in top:
        if overlap_ratio(r, t) >= OVERLAP_THRESHOLD:  # 0.05
            found += 1
            break
return found / len(truth)
```
Pour chaque source de vérité, on cherche au moins UN chunk retrouvé qui
la couvre à ≥ 5 %. Si oui → trouvé.

### 8.3 `evaluate` (lignes 61-87)
- Charge `student_results.json` et `dataset.json` via pydantic.
- Construit un dict `truth_by_id` qui mappe `question_id → sources`.
- Boucle sur les réponses du student → calcule recall@1/3/5/10.
- Retourne un `EvalReport` (dataclass).

### 8.4 `EvalReport.pretty()` (lignes 24-32)
Formatage texte attendu par le sujet :
```
Evaluation Results
========================================
Questions evaluated: 100
Recall@ 1: 0.450
Recall@ 3: 0.590
Recall@ 5: 0.650
Recall@10: 0.720
```

---

## 9. Récapitulatif du flux complet

### Cas 1 : `python -m student index --use_embeddings True`
```
__main__.py
  → cli.main()
    → fire.Fire(CLI)
      → CLI.index(repo_path=..., max_chunk_size=2000, use_embeddings=True)
        → _resolve_repo(...)
        → KnowledgeBase.build(...)
          → ingest.collect_files(...)            # lit tous les fichiers
            → ingest.iter_files(...)             # parcourt l'arbo
            → ingest.read_file_safely(...)       # lit chaque fichier
          → chunking.chunk_file(...) ×N          # découpe chaque fichier
            → chunking.chunk_python / chunk_markdown
              → chunking._split_oversized        # fenêtre glissante si trop long
          → tokenizer.tokenize_batch(...)        # transforme les chunks en tokens
          → bm25s.BM25().index(...)              # construit l'index BM25
          → index._encode_corpus(...)            # bonus : embeddings denses
        → KnowledgeBase.save(...)                # persiste sur disque
```

### Cas 2 : `python -m student search "openai server" --k 5`
```
__main__.py → cli.main() → fire.Fire(CLI)
  → CLI.search(query="openai server", k=5)
    → KnowledgeBase.load(...)                    # depuis data/processed/
    → kb.search(query, k=5, mode="auto")
      → mode = "hybrid" (car embeddings présents)
      → kb.search_hybrid(query, k=5)
        → kb.search_bm25(query, k=20)
          → tokenizer.tokenize(query)
          → bm25.retrieve([tokens], k=20)
        → kb.search_dense(query, k=20)
          → kb._get_embedder() (lazy)
          → embedder.encode([query])
          → cosine via produit matriciel
        → fusion RRF
      → return [Chunk, Chunk, ...]
    → format MinimalSource → print
```

### Cas 3 : `python -m student evaluate ...`
```
CLI.evaluate(student_results_path, dataset_path)
  → evaluate.evaluate(...)
    → StudentSearchResults.model_validate_json(...)
    → RagDataset.model_validate_json(...)
    → for each question:
        → evaluate.question_recall(retrieved, truth, k)
          → evaluate.overlap_ratio(...)
    → return EvalReport
  → print(report.pretty())
```

---

## 10. Pourquoi cette organisation ?

| Principe | Application dans le code |
|---|---|
| **Séparation des responsabilités** | Un fichier = une couche (ingest, chunk, index, generate, evaluate). |
| **Lazy loading** | `transformers` et `sentence-transformers` ne sont importés *que* si on en a besoin. La CLI démarre en < 1 s. |
| **Persistance / caching** | `KnowledgeBase.save`/`load` → on indexe une fois, on recherche autant qu'on veut. |
| **Validation centrée sur pydantic** | Tous les I/O JSON passent par les modèles. Un fichier corrompu → erreur claire au lieu d'un crash 10 fonctions plus loin. |
| **CLI auto-générée** | Fire transforme méthodes Python → commandes shell sans boilerplate `argparse`. |
| **Type hints partout** | mypy passe sans erreur (exigence du sujet). |

---

## 11. Pour aller plus loin

Une fois que tout ça est limpide, regarde :
- `bm25s` source code (extrêmement lisible) pour comprendre les
  internals de BM25.
- HuggingFace docs sur `generate()` (sampling, beam search, temperature).
- Papier "Reciprocal Rank Fusion outperforms Condorcet and individual
  Rank Learning Methods" (Cormack et al. 2009).
- Idées pour booster ton recall : **reranking** avec un cross-encoder,
  **query rewriting** par LLM, **chunk overlap** plus généreux.
