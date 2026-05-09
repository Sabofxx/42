def sliding_window_maximum(nums: list[int], k: int) -> list[int]:
    if not nums or k <= 0 or k > len(nums):
        return []
    return [max(nums[i:i+k]) for i in range(len(nums) - k + 1)]


# print("excepted: [3, 3, 5, 5, 6, 7]")
# print("got:", sliding_window_maximum([1, 3, -1, -3, 5, 3, 6, 7], 3), "\n")

# print("excepted: [2, 3, 4, 5]")
# print("got:", sliding_window_maximum([1, 2, 3, 4, 5], 2), "\n")

# print("excepted: [5, 4, 3, 2, 1]")
# print("got:", sliding_window_maximum([5, 4, 3, 2, 1], 1), "\n")

# print("excepted: [3]")
# print("got:", sliding_window_maximum([1, 2, 3], 3), "\n")

# print("excepted: []")
# print("got:", sliding_window_maximum([1, 2, 3], 4), "\n")

# print("excepted: []")
# print("got:", sliding_window_maximum([], 2), "\n")

# print("excepted: []")
# print("got:", sliding_window_maximum([1, 2, 3], 0), "\n")
