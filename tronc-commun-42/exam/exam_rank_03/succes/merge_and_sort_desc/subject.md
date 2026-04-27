# merge_and_sort_desc
---

Write a function:
```
def merge_and_sort_desc(list1: list[int], list2: list[int]) -> list[int]:
```
that takes two lists of integers, merges them into a single list, and returns the list sorted from largest to smallest.

#### Rules
The input lists may be empty.
Duplicates are allowed.
The original lists should not be modified.

#### Examples
```
merge_and_sort_desc([1, 3, 5], [2, 4, 6])      → [6, 5, 4, 3, 2, 1]
merge_and_sort_desc([10, 2], [3, 7, 2])        → [10, 7, 3, 2, 2]
merge_and_sort_desc([], [1, 2, 3])             → [3, 2, 1]
merge_and_sort_desc([], [])                     → []
```
