#!/usr/bin/env python3

def merge_and_sort_desc(list1: list[int], list2: list[int]) -> list[int]:
    merged = list1 + list2
    merged.sort(reverse=True)
    return merged


def main() -> None:
    print(merge_and_sort_desc([1, 3, 5], [2, 4, 6]))      # [6, 5, 4, 3, 2, 1]
    print(merge_and_sort_desc([10, 2], [3, 7, 2]))        # [10, 7, 3, 2, 2]
    print(merge_and_sort_desc([], [1, 2, 3]))             # [3, 2, 1]
    print(merge_and_sort_desc([], []))                    # []


if __name__ == "__main__":
    main()
