# sorted
---
This exercise is not a single function — it's a concept you must master. You will be asked to sort lists of strings, tuples, or objects by a custom criterion using sorted() with a key=lambda argument. No external libraries allowed. You must be able to sort by length, by a specific field, in reverse order, or by multiple criteria at once.

```
sorted(["banana", "kiwi", "fig"], key=lambda x: len(x))
→ ["fig", "kiwi", "banana"]

sorted([("Ana", 8.5), ("Luis", 6.0)], key=lambda x: x[1], reverse=True)
→ [("Ana", 8.5), ("Luis", 6.0)]

sorted([("Ana", 20), ("Luis", 20), ("Marta", 18)], key=lambda x: (x[1], x[0]))
→ [("Marta", 18), ("Ana", 20), ("Luis", 20)]
```