def sliding_window_maximum(nums: list[int], k: int) -> list[int]:
    if not nums or k <= 0 or k > len(nums):
        return []
    result = []
    dq = []
    for i, n in enumerate(nums):
        while dq and dq[0] <= i - k:
            dq.pop(0)
        while dq and nums[dq[-1]] < n:
            dq.pop()
        dq.append(i)
        if i >= k - 1:
            result.append(nums[dq[0]])
    return result
