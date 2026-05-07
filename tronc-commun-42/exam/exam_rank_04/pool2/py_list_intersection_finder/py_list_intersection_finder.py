def list_intersection_finder(lists: list[list[int]]) -> list[int]:
    if lists == []:
        return []
    s = []
    for n in lists[0]:
        in_all = True
        for l in lists[1:]:
            if n not in l:
                in_all = False
        if in_all == True and n not in s:
            s.append(n)
    return sorted(s)

# res = list_intersection_finder([[1, 2, 3], [2, 3, 4], [2, 3, 5]])
# print(f"excepted: [2, 3]")
# print(f"got: {res}\n")

# res = list_intersection_finder([[1, 2, 3, 4], [2, 4, 6, 8], [4, 8, 12]])
# print(f"excepted: [4]")
# print(f"got: {res}\n")

# res = list_intersection_finder([[1, 2, 3], [4, 5, 6]])
# print(f"excepted: []")
# print(f"got: {res}\n")

# res = list_intersection_finder([[1, 1, 2, 3], [1, 2, 2, 3], [1, 2, 3, 3]])
# print(f"excepted: [1, 2, 3]")
# print(f"got: {res}\n")

# res = list_intersection_finder([])
# print(f"excepted: []")
# print(f"got: {res}\n")

# res = list_intersection_finder([[1, 2, 3], []])
# print(f"excepted: []")
# print(f"got: {res}\n")

# res = list_intersection_finder([[5]])
# print(f"excepted: [5]")
# print(f"got: {res}\n")

def list_intersection_finder(lists: list[list[int]]) -> list[int]:
    if lists == []:
        return []
    s = []
    for n in lists:
        in_all = True
        for l in lists:
            if n not in l:
                in_all = False
        if in_all == True and n not in s:
                s.append(n)
    return sorted(s)
