# Exam Rank 03 — Python

42 Common Core **Milestone 3** exam (Python). One assignment is drawn at random
from a pool; the goal is to solve it within the allotted time, with a passing
test suite, from a clean clone in the exam environment.

The `succes/` directory contains my passing solutions for the exercises I drew
during practice / actual attempts.

## Solutions

Each exercise lives in `succes/<name>/<name>.py` with a `main()` that prints
the expected outputs for the official test cases.

| Exercise | What it does |
|---|---|
| [`py_bracket_validator`](succes/py_bracket_validator) | Stack-based check that `()`, `[]`, `{}` brackets are correctly nested |
| [`py_cryptic_sorter`](succes/py_cryptic_sorter) | Sort strings by (length, case-insensitive value, vowel count) |
| [`py_echo_validator`](succes/py_echo_validator) | Palindrome check ignoring case and non-alphabetic characters |
| [`py_mirror_matrix`](succes/py_mirror_matrix) | Horizontally mirror a 2D matrix |
| [`py_number_base_converter`](succes/py_number_base_converter) | Convert a string from base 2–36 to base 2–36, with input validation |
| [`py_pattern_tracker`](succes/py_pattern_tracker) | Count pairs of adjacent digits where `b == a + 1` |
| [`py_shadow_merge`](succes/py_shadow_merge) | Merge two integer lists and return the sorted result |
| [`py_string_permutation_checker`](succes/py_string_permutation_checker) | Detect whether two strings are permutations of each other |
| [`py_string_sculptor`](succes/py_string_sculptor) | Alternate lower/upper case per word, preserving non-letters |
| [`py_twist_sequence`](succes/py_twist_sequence) | Rotate a list by `k` positions, modulo length |
| [`py_whisper_cipher`](succes/py_whisper_cipher) | Custom character-shifting cipher |

## Running a single exercise

```bash
cd tronc-commun-42/exam/exam_rank_03/succes/py_bracket_validator
python3 py_bracket_validator.py
```

Each script prints the expected outputs from its embedded test cases — no
external test runner required.

## Practice setup

`42ExamRank03_Simulator/` contains the local simulator used to draw a random
assignment and reproduce the exam loop (clone → solve → grade) without an
internet connection. See `EXAM_RANK_03_SIMULATOR_GUIDE.md` for usage.

## Topics covered

- String manipulation (case folding, filtering, ciphers)
- 2D matrices (rotation, mirroring)
- Stack-based parsing (balanced brackets)
- Base conversion (integer ↔ arbitrary base 2–36)
- Sorting with multi-key `key=lambda`
- List rotation and merging

---

*42 Luxembourg — Common Core · Python · Milestone 3 · 100/100*
