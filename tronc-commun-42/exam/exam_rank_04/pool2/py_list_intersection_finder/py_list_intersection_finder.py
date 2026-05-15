def list_intersection_finder(lists: list[list[int]]) -> list[int]:
    if not lists or any(not lst for lst in lists):
        return []
    return sorted(set.intersection(*map(set, lists)))
