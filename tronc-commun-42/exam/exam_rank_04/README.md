# Exam Rank 04 — Python

42 Common Core **Milestone 4** exam (Python). The exam is organized as a
sequence of **4 pools** of increasing difficulty; passing a pool unlocks the
next one. Each pool draws one assignment at random — the goal is to ship a
working `solution.py` against the official test grid within the time limit.

This folder contains my passing solutions, organized by pool.

## Solutions

Each exercise lives in `poolN/<name>/<name>.py` next to its subject
(`subject.en.txt` / `subject.es.txt`).

### Pool 1 — warm-up

| Exercise | Problem |
|---|---|
| [`py_array_rotation_detector`](pool1/py_array_rotation_detector) | Detect whether one array is a circular rotation (left or right) of another |
| [`py_constellation_mapper`](pool1/py_constellation_mapper) | Map points to constellation groups based on adjacency |

### Pool 2 — lists & search

| Exercise | Problem |
|---|---|
| [`py_list_intersection_finder`](pool2/py_list_intersection_finder) | Find common elements between two lists (set-like intersection) |
| [`py_merge_sorted_lists`](pool2/py_merge_sorted_lists) | Merge two sorted lists into one sorted list in linear time |

### Pool 3 — algorithms

| Exercise | Problem |
|---|---|
| [`py_palindrome_partitioner`](pool3/py_palindrome_partitioner) | Partition a string into the minimum number of palindromic substrings |
| [`py_package_dependency_resolver`](pool3/py_package_dependency_resolver) | Topological sort (Kahn's algorithm) for a package dependency graph; returns `[]` on cycles |

### Pool 4 — advanced

| Exercise | Problem |
|---|---|
| [`py_sliding_window_maximum`](pool4/py_sliding_window_maximum) | Return the max element of every window of size `k` in `nums` |

## Running a single exercise

```bash
cd tronc-commun-42/exam/exam_rank_04/pool1/py_array_rotation_detector
python3 py_array_rotation_detector.py
```

Each subject file (`subject.en.txt`) defines the expected function signature,
the edge cases, and the example inputs/outputs the grader checks.

## Topics covered

- **Array manipulation** — circular rotations, sliding windows
- **Graph algorithms** — topological sort (Kahn), cycle detection,
  adjacency-based grouping (constellation mapping)
- **Dynamic programming** — minimum palindrome partition
- **Two-pointer / merge** — linear-time merging of sorted lists, set
  intersection
- **Edge cases by contract** — empty inputs, invalid `k`, mismatched lengths,
  circular dependencies; every solution returns the spec'd sentinel
  (`False`, `[]`, etc.) rather than raising

---

*42 Luxembourg — Common Core · Python · Milestone 4 · 100/100*
