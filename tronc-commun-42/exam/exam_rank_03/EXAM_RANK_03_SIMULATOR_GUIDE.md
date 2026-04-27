# Exam Rank 03 — Guide A to Z (selon `42ExamRank03_Simulator`)

> Ce guide couvre les **11 exos** du simulateur Python d'IntRogerYT (`42ExamRank03_Simulator`). Pour chaque exo : sujet, signature, exemples, approche, code commenté, complexité, edge cases.
>
> Les solutions sont dans `succes/py_<nom>/py_<nom>.py`.

---

## Table des matières

1. [Comment marche le simulateur](#1-comment-marche-le-simulateur)
2. [Easy](#easy)
   - [py_mirror_matrix](#py_mirror_matrix)
   - [py_echo_validator](#py_echo_validator)
   - [py_whisper_cipher](#py_whisper_cipher)
   - [py_shadow_merge](#py_shadow_merge)
3. [Medium](#medium)
   - [py_number_base_converter](#py_number_base_converter)
   - [py_bracket_validator](#py_bracket_validator)
   - [py_pattern_tracker](#py_pattern_tracker)
   - [py_string_sculptor](#py_string_sculptor)
   - [py_twist_sequence](#py_twist_sequence)
4. [Hard](#hard)
   - [py_string_permutation_checker](#py_string_permutation_checker)
   - [py_cryptic_sorter](#py_cryptic_sorter)
5. [Tricks transverses pour l'exam](#tricks-transverses-pour-lexam)
6. [Modèle de réponse type](#modèle-de-réponse-type)

---

## 1. Comment marche le simulateur

### Fichiers
- `42ExamRank03_Simulator/exam.sh` — script bash qui pioche un exo, écrit le sujet dans `subjects/`, et grade ta réponse dans `rendu/<nom>/<nom>.py`.
- `42ExamRank03_Simulator/Makefile` — `make` (lance), `make grade` (test), `make re` (reset), `make clean`.
- `subjects/subject_en.txt` — le sujet du moment.
- `rendu/<nom>/<nom>.py` — où tu écris ta solution.
- `traces/` — logs des essais ratés.

### Niveaux
- **Easy 1 + Easy 2** : 2 exos pris au hasard parmi 4 (sans répétition).
- **Medium 1 + Medium 2** : ordre fixe parmi 5.
- **Hard 1 + Hard 2** : ordre fixe parmi 2.
- Total : 6 exos à passer pour valider la simu.

### Structure obligatoire de la solution
- Dossier : `rendu/py_<exo>/`
- Fichier : `py_<exo>.py`
- Fonction : `def py_<exo>(...)` — **le `py_` est obligatoire**, c'est ce que cherche le grader (`mod.py_${function_name}` dans `exam.sh:268`).

### Commandes utiles
```bash
make           # lance ou affiche l'exo courant
make grade     # teste ta solution
make re        # reset (revient au level 1)
make clean     # nettoie subjects/, traces/, et propose de virer rendu/
```

### Workflow type
1. `make` → tu lis `subjects/subject_en.txt`
2. `mkdir rendu/py_<nom> && touch rendu/py_<nom>/py_<nom>.py`
3. Tu codes
4. `make grade`
5. ✅ pass → niveau suivant ; ❌ fail → trace dans `traces/`

---

## EASY

### py_mirror_matrix

**Sujet** : Miroite une matrice 2D horizontalement en inversant chaque ligne.

**Signature** : `def py_mirror_matrix(matrix: list[list[int]]) -> list[list[int]]:`

**Exemples**
```python
py_mirror_matrix([[1, 2, 3], [4, 5, 6]])    # → [[3, 2, 1], [6, 5, 4]]
py_mirror_matrix([[1, 2], [3, 4], [5, 6]])  # → [[2, 1], [4, 3], [6, 5]]
py_mirror_matrix([[7]])                      # → [[7]]
py_mirror_matrix([[1, 2, 3, 4]])             # → [[4, 3, 2, 1]]
```

**Approche**
- Pour chaque ligne : `row[::-1]` (slice avec step négatif inverse).
- Une comprehension fait tout en 1 ligne.

**Code**
```python
def py_mirror_matrix(matrix: list[list[int]]) -> list[list[int]]:
    return [row[::-1] for row in matrix]
```

**Complexité** : O(n×m) où n = lignes, m = cols.

**Edge cases** : matrice vide `[]` (la comprehension retourne `[]`), ligne d'un seul élément (inversée = même).

---

### py_echo_validator

**Sujet** : Vérifie si une string est un palindrome, en ignorant espaces et casse, et en ne considérant **que les caractères alphabétiques**.

**Signature** : `def py_echo_validator(text: str) -> bool:`

**Exemples**
```python
py_echo_validator('racecar')                          # → True
py_echo_validator('A man a plan a canal Panama')      # → True
py_echo_validator('race a car')                       # → False
py_echo_validator('Was it a car or a cat I saw')      # → True
py_echo_validator('hello')                            # → False
py_echo_validator('Madam Im Adam')                    # → True
py_echo_validator('')                                 # → False  ← ATTENTION
```

**Approche**
1. Filtrer pour ne garder que les alphas, en lowercase.
2. Si vide → `False` (cas particulier explicite dans les tests).
3. Comparer la liste à son inverse.

**Code**
```python
def py_echo_validator(text: str) -> bool:
    filtered = [c.lower() for c in text if c.isalpha()]
    if not filtered:
        return False
    return filtered == filtered[::-1]
```

**Complexité** : O(n).

**Pièges**
- `''` doit retourner `False` (pas True, comme on pourrait penser pour une string vide).
- `c.isalpha()` rejette espaces, ponctuation, chiffres.
- `c.lower()` gère 'A' == 'a'.

---

### py_whisper_cipher

**Sujet** : Cipher de César — décale chaque lettre de `shift` positions. Les non-alphas restent intacts.

**Signature** : `def py_whisper_cipher(text: str, shift: int) -> str:`

**Exemples**
```python
py_whisper_cipher('hello', 3)            # → 'khoor'
py_whisper_cipher('Hello World!', 1)     # → 'Ifmmp Xpsme!'
py_whisper_cipher('xyz', 3)              # → 'abc'    ← wrap-around
py_whisper_cipher('ABC123def', 5)        # → 'FGH123ijk'
py_whisper_cipher('', 10)                # → ''
```

**Approche**
- Pour chaque char :
  - upper → décaler dans 'A'..'Z' avec `% 26`
  - lower → décaler dans 'a'..'z' avec `% 26`
  - sinon → garder tel quel

**Code**
```python
def py_whisper_cipher(text: str, shift: int) -> str:
    result = []
    for c in text:
        if c.isupper():
            result.append(chr((ord(c) - ord('A') + shift) % 26 + ord('A')))
        elif c.islower():
            result.append(chr((ord(c) - ord('a') + shift) % 26 + ord('a')))
        else:
            result.append(c)
    return ''.join(result)
```

**Complexité** : O(n).

**Pièges**
- Le `% 26` gère le wrap-around (`'z'` + 1 = `'a'`).
- La casse est préservée (`'H'` → `'I'`, pas `'i'`).
- Les chiffres et la ponctuation passent telles quelles.
- `shift` peut être > 26 ou négatif → `%` gère ça automatiquement... presque. **Attention** : en Python `(-1) % 26 == 25`, donc shift négatif fonctionne. Mais ce cas n'est pas testé.

---

### py_shadow_merge

**Sujet** : Merge 2 listes triées en une liste triée.

**Signature** : `def py_shadow_merge(list1: list[int], list2: list[int]) -> list[int]:`

**Exemples**
```python
py_shadow_merge([1, 3, 5], [2, 4, 6])    # → [1, 2, 3, 4, 5, 6]
py_shadow_merge([1, 2, 3], [4, 5, 6])    # → [1, 2, 3, 4, 5, 6]
py_shadow_merge([1], [2, 3, 4])          # → [1, 2, 3, 4]
py_shadow_merge([], [1, 2, 3])           # → [1, 2, 3]
py_shadow_merge([1, 1, 2], [1, 3, 3])    # → [1, 1, 1, 2, 3, 3]
```

**Approche** (deux pointeurs, classique du merge sort)
1. `i, j = 0, 0`
2. Tant que ni `list1` ni `list2` n'est épuisée : prendre le plus petit des deux fronts.
3. Étendre avec ce qui reste de la liste non-épuisée.

**Code**
```python
def py_shadow_merge(list1: list[int], list2: list[int]) -> list[int]:
    result: list[int] = []
    i, j = 0, 0
    while i < len(list1) and j < len(list2):
        if list1[i] <= list2[j]:
            result.append(list1[i])
            i += 1
        else:
            result.append(list2[j])
            j += 1
    result.extend(list1[i:])
    result.extend(list2[j:])
    return result
```

**Complexité** : O(n + m).

**Triche acceptée ?** : `return sorted(list1 + list2)` marche aussi (O((n+m)·log(n+m))). C'est plus court mais le 2-pointers est l'algo "officiel".

**Pièges**
- Le `<=` (et pas `<`) garantit la stabilité quand des doublons existent.
- N'oublie pas le `extend` final pour vider la liste restante.

---

## MEDIUM

### py_number_base_converter

**Sujet** : Convertit un nombre d'une base à une autre. Bases 2 à 36 inclus. Retourne `'ERROR'` pour entrées invalides.

**Signature** : `def py_number_base_converter(number: str, from_base: int, to_base: int) -> str:`

**Exemples**
```python
py_number_base_converter('1010', 2, 10)    # → '10'
py_number_base_converter('FF', 16, 10)     # → '255'
py_number_base_converter('255', 10, 16)    # → 'FF'
py_number_base_converter('123', 10, 2)     # → '1111011'
py_number_base_converter('Z', 36, 10)      # → '35'
py_number_base_converter('35', 10, 36)     # → 'Z'
py_number_base_converter('123', 1, 10)     # → 'ERROR'  ← base hors range
py_number_base_converter('G', 16, 10)      # → 'ERROR'  ← G > base 16
```

**Approche**
1. Valide les bases : `2 <= base <= 36`, sinon ERROR.
2. Convertit `number` (string) → `value` (int en base 10).
3. Convertit `value` → string en `to_base`.

**Code**
```python
def py_number_base_converter(number: str, from_base: int, to_base: int) -> str:
    if from_base < 2 or from_base > 36 or to_base < 2 or to_base > 36:
        return 'ERROR'
    if not number:
        return 'ERROR'

    digits = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    value = 0
    for char in number:
        if char not in digits:
            return 'ERROR'
        d = digits.index(char)
        if d >= from_base:
            return 'ERROR'
        value = value * from_base + d

    if value == 0:
        return '0'

    result = ''
    while value > 0:
        result = digits[value % to_base] + result
        value //= to_base
    return result
```

**Complexité** : O(longueur du nombre × log(base)).

**Pièges**
- **Toujours valider** : base hors [2,36], digit invalide pour la base, string vide.
- Le digit `'G'` a la valeur 16, donc invalide en base 16 (les digits valides sont 0..F = 0..15).
- Le digit `'Z'` a la valeur 35, donc valide en base 36 (digits 0..Z = 0..35).
- Cas spécial `value == 0` → retourner `'0'` (sinon la boucle while ne s'exécute pas et tu retournes `''`).

---

### py_bracket_validator

**Sujet** : Vérifie que `[]`, `()`, `{}` sont équilibrés et bien imbriqués. Tous les autres caractères sont ignorés.

**Signature** : `def py_bracket_validator(s: str) -> bool:`

**Exemples**
```python
py_bracket_validator('()')                              # → True
py_bracket_validator('()[]{}')                          # → True
py_bracket_validator('(]')                              # → False
py_bracket_validator('([)]')                            # → False  ← mal imbriqué
py_bracket_validator('{[]}')                            # → True
py_bracket_validator('hello(world)[test]{code}')        # → True   ← ignore les lettres
py_bracket_validator('((()))')                          # → True
py_bracket_validator('((())')                           # → False  ← parenthèse non fermée
py_bracket_validator('')                                # → True   ← vide = OK
```

**Approche** : la pile (stack) classique.
1. Pour chaque char :
   - Si c'est un opener `([{` → push.
   - Si c'est un closer `)]}` → vérifier que le top de la stack matche, sinon False, sinon pop.
   - Sinon → ignorer.
2. À la fin : stack doit être vide.

**Code**
```python
def py_bracket_validator(s: str) -> bool:
    pairs = {')': '(', ']': '[', '}': '{'}
    openers = set('([{')
    stack: list[str] = []
    for c in s:
        if c in openers:
            stack.append(c)
        elif c in pairs:
            if not stack or stack[-1] != pairs[c]:
                return False
            stack.pop()
    return len(stack) == 0
```

**Complexité** : O(n).

**Pièges**
- `'([)]'` doit retourner False : quand on rencontre `)`, le top de la stack est `[`, pas `(`.
- String vide → True (rien à valider).
- Closer en premier (`')abc'`) → False (stack vide quand on rencontre `)`).

---

### py_pattern_tracker

**Sujet** : Compte les paires de chiffres consécutifs où le second est exactement 1 de plus que le premier.

**Signature** : `def py_pattern_tracker(text: str) -> int:`

**Exemples**
```python
py_pattern_tracker('123')           # → 2  (12 et 23)
py_pattern_tracker('12a34')         # → 2  (12 et 34, mais pas 2a, a3)
py_pattern_tracker('987654321')     # → 0  (ordre décroissant)
py_pattern_tracker('01234567')      # → 7  (01,12,23,34,45,56,67)
py_pattern_tracker('abc')           # → 0
py_pattern_tracker('1a2b3c4')       # → 0  (jamais 2 chiffres adjacents)
py_pattern_tracker('112233')        # → 2  (12 et 23, mais pas 11/22/33)
```

**Approche** : itère sur les paires `(text[i], text[i+1])`, compte celles où les 2 sont des chiffres et `int(b) - int(a) == 1`.

**Code**
```python
def py_pattern_tracker(text: str) -> int:
    count = 0
    for i in range(len(text) - 1):
        a, b = text[i], text[i + 1]
        if a.isdigit() and b.isdigit() and int(b) - int(a) == 1:
            count += 1
    return count
```

**Complexité** : O(n).

**Pièges**
- Les chiffres doivent être **adjacents** dans la string (pas séparés par autre chose).
- `'1a2'` : 1 et a non-paire (a pas un digit), a et 2 non-paire (a pas un digit) → 0.
- Comparaison numérique, pas alphabétique : `'9' → '0'` n'est PAS valide (pas de wrap).

---

### py_string_sculptor

**Sujet** : Alterne la casse des caractères alphabétiques. Le 1er alpha en lower, le 2nd en upper, etc.

**Signature** : `def py_string_sculptor(text: str) -> str:`

**Exemples**
```python
py_string_sculptor('hello')        # → 'hElLo'
py_string_sculptor('Hello World')  # → 'hElLo wOrLd'    ← reset après l'espace
py_string_sculptor('aBc123def')    # → 'aBc123DeF'      ← les digits ne reset pas
py_string_sculptor('Python3.9!')   # → 'pYtHoN3.9!'
py_string_sculptor('')             # → ''
```

**Approche** — il y a un piège : le compteur d'alpha **se reset à chaque espace**, mais pas sur les autres non-alphas.
1. `alpha_index = 0`
2. Pour chaque char :
   - Si espace → `alpha_index = 0`, append le char.
   - Si alpha → append en lower si `alpha_index % 2 == 0`, sinon en upper. `alpha_index += 1`.
   - Sinon (digit, ponctuation) → append le char (pas de reset).

**Code**
```python
def py_string_sculptor(text: str) -> str:
    result = []
    alpha_index = 0
    for c in text:
        if c.isspace():
            alpha_index = 0
            result.append(c)
        elif c.isalpha():
            if alpha_index % 2 == 0:
                result.append(c.lower())
            else:
                result.append(c.upper())
            alpha_index += 1
        else:
            result.append(c)
    return ''.join(result)
```

**Complexité** : O(n).

**Le piège majeur**
- À première lecture, on coderait un compteur global. Ça échoue sur `'Hello World'` :
  - Sans reset : 5e alpha (W) = up → `'WoRlD'` (incorrect)
  - Avec reset : 'World' redémarre à l'index 0 → `'wOrLd'` (correct)
- Les digits ne resettent pas (`'aBc123def'` : `'aBc'` puis `'DeF'` = continuation, pas redémarrage).
- **Règle finale** : reset uniquement sur whitespace.

---

### py_twist_sequence

**Sujet** : Rotate un tableau de `k` positions vers la droite (les `k` derniers passent devant).

**Signature** : `def py_twist_sequence(arr: list[int], k: int) -> list[int]:`

**Exemples**
```python
py_twist_sequence([1, 2, 3, 4, 5], 2)    # → [4, 5, 1, 2, 3]
py_twist_sequence([1, 2, 3], 1)          # → [3, 1, 2]
py_twist_sequence([1, 2, 3, 4], 0)       # → [1, 2, 3, 4]   ← rotate de 0
py_twist_sequence([1, 2, 3], 5)          # → [2, 3, 1]      ← k > len, modulo
py_twist_sequence([], 3)                 # → []
```

**Approche** : `k = k % len(arr)`, puis `arr[-k:] + arr[:-k]`.

**Code**
```python
def py_twist_sequence(arr: list[int], k: int) -> list[int]:
    if not arr:
        return []
    k = k % len(arr)
    if k == 0:
        return list(arr)
    return arr[-k:] + arr[:-k]
```

**Complexité** : O(n).

**Pièges**
- `k > len(arr)` → modulo (rotate de 5 sur 3 éléments = rotate de 2).
- `k == 0` (ou `k % len == 0`) → retourner une copie, pas l'original (sécurité, on évite les aliases).
- Liste vide → return `[]` direct, sinon division par zéro sur `% 0`.
- `arr[-k:]` sur k=0 retournerait `arr[-0:]` = `arr[0:]` = toute la liste. C'est pour ça qu'on traite k==0 séparément.

---

## HARD

### py_string_permutation_checker

**Sujet** : Vérifie si 2 strings sont des permutations l'une de l'autre.

**Signature** : `def py_string_permutation_checker(s1: str, s2: str) -> bool:`

**Exemples**
```python
py_string_permutation_checker('abc', 'bca')                    # → True
py_string_permutation_checker('abc', 'def')                    # → False
py_string_permutation_checker('listen', 'silent')              # → True
py_string_permutation_checker('hello', 'bello')                # → False
py_string_permutation_checker('', '')                          # → True
py_string_permutation_checker('a', '')                         # → False
py_string_permutation_checker('Abc', 'abc')                    # → False  ← case-sensitive
py_string_permutation_checker('a gentleman', 'elegant man')    # → True   ← inclut l'espace
```

**Approche**
- Le plus court : `sorted(s1) == sorted(s2)`.
- Plus rapide en théorie : `Counter(s1) == Counter(s2)`. Mais sorted suffit.

**Code**
```python
def py_string_permutation_checker(s1: str, s2: str) -> bool:
    return sorted(s1) == sorted(s2)
```

**Complexité** : O(n log n) avec sorted, O(n) avec Counter.

**Pièges**
- **Case-sensitive** : `'Abc'` et `'abc'` sont différents.
- **L'espace compte** : `'a gentleman'` et `'elegant man'` ont chacun un espace, donc ça matche.
- Longueurs différentes → False (sorted produit deux listes de longueurs différentes, donc inégales).

---

### py_cryptic_sorter

**Sujet** : Tri une liste de strings selon 3 critères, dans cet ordre :
1. Par longueur (plus court d'abord).
2. ASCII order **case-insensitive**.
3. Par nombre de voyelles (ascendant).

**Signature** : `def py_cryptic_sorter(strings: list[str]) -> list[str]:`

**Exemples**
```python
py_cryptic_sorter(['apple', 'cat', 'banana', 'dog', 'elephant'])
# → ['cat', 'dog', 'apple', 'banana', 'elephant']

py_cryptic_sorter(['aaa', 'bbb', 'AAA', 'BBB'])
# → ['AAA', 'aaa', 'BBB', 'bbb']                  ← upper avant lower (ASCII)

py_cryptic_sorter(['hello', 'world', 'hi', 'test'])
# → ['hi', 'test', 'hello', 'world']

py_cryptic_sorter([])                              # → []
py_cryptic_sorter([''])                            # → ['']
```

**Approche** : `sorted` avec une **clé tuple** ordonnée par priorité : `(len, lower, vowels, raw)`.
- `len(s)` — critère 1
- `s.lower()` — critère 2 (ASCII case-insensitive)
- nombre de voyelles — critère 3
- `s` brut — pour départager les ties restants (comme `'AAA'` vs `'aaa'` : même lower, même nb voyelles, mais 'AAA' < 'aaa' en ASCII strict)

**Code**
```python
_VOWELS = set('aeiouAEIOU')


def _vowel_count(s: str) -> int:
    return sum(1 for c in s if c in _VOWELS)


def py_cryptic_sorter(strings: list[str]) -> list[str]:
    return sorted(strings, key=lambda s: (len(s), s.lower(), _vowel_count(s), s))
```

**Complexité** : O(n log n × max_len) — la comparaison de tuples + s.lower() coûte O(max_len).

**Pièges**
- Le tuple-key est l'idiome pythonic pour multi-critères.
- Le 4ème élément (`s` brut) résout le test `['aaa','bbb','AAA','BBB']` :
  - 'AAA' et 'aaa' ont (3, 'aaa', 3) en commun → départage par `s` brut → 'AAA' < 'aaa' (uppercase A=65, lowercase a=97).
- Sans le 4ème, le tri stable de Python conserverait l'ordre d'entrée → 'aaa' avant 'AAA' → faux.

---

## Tricks transverses pour l'exam

### Le préfixe `py_`
Toutes les fonctions doivent s'appeler `py_<exo>`. Si tu codes `def mirror_matrix(...)`, le grader ne trouvera pas `mod.py_mirror_matrix` et tu fail. **Toujours préfixer `py_`**.

### Le sujet est dans `subjects/subject_en.txt`
Le `make` réécrit ce fichier avec la signature transformée (`py_<nom>`) — copie-la directement, ne réinvente pas.

### Tester localement avant `make grade`
Au lieu de submit en aveugle, fais un fichier `test.py` dans `rendu/py_<nom>/` :
```python
from py_mirror_matrix import py_mirror_matrix
print(py_mirror_matrix([[1,2,3],[4,5,6]]))
```
Et lance `cd rendu && python3 -c "from py_mirror_matrix.py_mirror_matrix import py_mirror_matrix; ..."`

### `make clean` vs `make re`
- `make clean` : vire `subjects/`, `traces/` et te demande pour `rendu/`. Garde l'état de progression.
- `make re` : reset complet, repart au level 1.

### Ne pas hardcoder les test cases
Les tests sont fixés dans `exam.sh`, mais le moulinette officiel à 42 (rank 03 réel) utilise des inputs random. Si tu hardcodes `if matrix == [[1,2,3],[4,5,6]]: return [[3,2,1],[6,5,4]]`, ça passera la simu mais pas l'exam réel.

### Les imports interdits
Le sujet ne le mentionne pas explicitement, mais à 42 on évite généralement les libs externes. Pour l'exam Python rank 03 réel, les imports stdlib sont OK (`from collections import Counter` etc.).

### Type hints
Les signatures données utilisent `list[int]`, `list[list[int]]`, etc. (Python 3.9+). En Python 3.8 il faudrait `List[int]` avec `from typing import List`. Le simulateur tourne en Python 3.10+, donc OK.

### Structure du grading dans `exam.sh`
Le script :
1. Détecte le level depuis `.exam_state`.
2. Charge l'exo (random pour easy, fixe pour medium/hard).
3. Lance `python3 -c "import importlib... mod.py_<func>(args) == expected"`.
4. Si l'assert passe → next level.
5. Sinon → trace dans `traces/`.

### Les 3 trucs qui font fail le plus souvent
1. **Mauvais nom de fonction** (oublié le préfixe `py_`).
2. **Mauvais nom de fichier** (doit matcher exactement le folder).
3. **Edge cases ratés** : `''`, `[]`, `k > len`, valeurs négatives, etc.

---

## Modèle de réponse type

```python
# rendu/py_<nom>/py_<nom>.py

def py_<nom>(arg1: <type>, arg2: <type>) -> <type>:
    # 1. Validation des entrées (cas vides, hors range, etc.)
    if not arg1:
        return <valeur_par_défaut>

    # 2. Logique principale
    result = ...

    # 3. Retour
    return result
```

Garde toujours :
- Une **garde** pour les inputs vides/invalides.
- Une **boucle simple** plutôt qu'une comprehension complexe (plus facile à débugger sous stress).
- **Pas d'imports** sauf si vraiment nécessaire.

---

## Tableau récap

| Exo | Niveau | Signature | Difficulté | Idée clé |
|---|---|---|---|---|
| py_mirror_matrix | Easy | `(matrix) -> matrix` | ★ | `row[::-1]` |
| py_echo_validator | Easy | `(text) -> bool` | ★★ | filter alpha + lower + reverse |
| py_whisper_cipher | Easy | `(text, shift) -> str` | ★★ | `(ord(c) + shift) % 26` |
| py_shadow_merge | Easy | `(list1, list2) -> list` | ★★ | 2 pointeurs |
| py_number_base_converter | Medium | `(n, fb, tb) -> str` | ★★★ | int intermediate + validation |
| py_bracket_validator | Medium | `(s) -> bool` | ★★★ | stack |
| py_pattern_tracker | Medium | `(text) -> int` | ★★ | itère paires adjacentes |
| py_string_sculptor | Medium | `(text) -> str` | ★★★ | reset alpha_index sur space |
| py_twist_sequence | Medium | `(arr, k) -> list` | ★★ | `arr[-k:] + arr[:-k]` |
| py_string_permutation_checker | Hard | `(s1, s2) -> bool` | ★ | `sorted(s1) == sorted(s2)` |
| py_cryptic_sorter | Hard | `(strings) -> list` | ★★★ | tuple-key (len, lower, vowels, s) |

Les "Hard" sont plus simples que certains Medium. Le vrai piège est `py_string_sculptor` (le reset sur espace) et `py_number_base_converter` (toutes les validations).
