#!/usr/bin/env python3

def shadow_merge(list1: list[int], list2: list[int]) -> list[int]:
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


def main() -> None:
    print(shadow_merge([1, 3, 5], [2, 4, 6]))   # [1, 2, 3, 4, 5, 6]
    print(shadow_merge([1, 2, 3], [4, 5, 6]))   # [1, 2, 3, 4, 5, 6]
    print(shadow_merge([1], [2, 3, 4]))         # [1, 2, 3, 4]
    print(shadow_merge([], [1, 2, 3]))          # [1, 2, 3]
    print(shadow_merge([1, 1, 2], [1, 3, 3]))   # [1, 1, 1, 2, 3, 3]


if __name__ == "__main__":
    main()
