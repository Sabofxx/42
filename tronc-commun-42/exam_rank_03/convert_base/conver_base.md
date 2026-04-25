# convert_base
---
Write a function:
```def convert_base(number: str, from_base: int, to_base: int) -> None:```
that converts a number represented as a string from base from_base to base to_base.

#### Requirements
* Bases are in the range [2, 36].

#### The function must
* print the result (do not return it).
* print "ERROR" if any error occurs.

```
Input:
convert_base("ff", 16, 2)
Output:
11111111

Input:
convert_base("10", 2, 10)
Output:
2

Input:
convert_base("z", 36, 10)
Output:
35

Input:
convert_base("1g", 16, 10)
Output:
ERROR
```