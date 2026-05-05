def merge_sorted_lists(lists: list[list[int]]) -> list[int]:
    return sorted(n for l in lists for n in l)
