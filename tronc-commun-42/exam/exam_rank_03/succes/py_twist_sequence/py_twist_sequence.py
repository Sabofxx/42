def py_twist_sequence(arr: list[int], k: int) -> list[int]:
    if not arr:
        return []
    k = k % len(arr)
    if k == 0:
        return list(arr)
    return arr[-k:] + arr[:-k]
