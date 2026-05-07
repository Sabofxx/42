def merge_sorted_lists(lists: list[list[int]]) -> list[int]:
    new = []
    for list in lists:
        for n in list:
            new.append(n)
    return sorted(new)

# print("excepted: [1, 2, 3, 4, 5, 6]")
# print("got:", merge_sorted_lists([[1, 3, 5], [2, 4, 6]]), "\n")

# print("excepted: [1, 2, 3, 4, 5, 6, 7, 8, 9]")
# print("got:", merge_sorted_lists([[1, 5, 9], [2, 3, 8], [4, 6, 7]]), "\n")

# print("excepted: [1, 2, 3, 4, 5]")
# print("got:", merge_sorted_lists([[5], [1, 3], [2, 4]]), "\n")

# print("excepted: [1, 1, 2, 2, 3, 3]")
# print("got:", merge_sorted_lists([[1, 1, 2], [2, 3, 3]]), "\n")

# print("excepted: [1, 2, 3]")
# print("got:", merge_sorted_lists([[], [1, 2, 3]]), "\n")

# print("excepted: []")
# print("got:", merge_sorted_lists([]))

# print("excepted: [-5, -3, -1, 0, 2, 4]")
# print("got:", merge_sorted_lists([[-5, -1, 0], [-3, 2, 4]]), "\n")

# print("excepted: [10, 10, 10]")
# print("got:", merge_sorted_lists([[10], [10], [10]]), "\n")

def merge_sorted_lists(lists: list[list[int]]) -> list[int]:
    new = []
    for n in lists:
        for l in n:
            new.append(l)
    return sorted(new)
