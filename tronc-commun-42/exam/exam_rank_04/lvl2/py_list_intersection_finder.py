def list_intersection_finder(lists: list[list[int]]) -> list[int]:
    if lists == []:
        return []
    s = []
    for n lists[0]:
        in_all = True
        for l in lists[1:]:
            if n not in 1:
                in_all = False
        if in_all == True and n not in s:
            s.append(n)
    return sorted(s)
