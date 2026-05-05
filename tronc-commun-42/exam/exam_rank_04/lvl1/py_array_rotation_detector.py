def array_rotation_detector(arr1: list[int], arr2: list[int]) -> bool:
    i = 0
    j = 0

    if len(arr1) != len(arr2):
        return False
    if sorted(arr1) != sorted(arr2):
        return False
    if arr1 = arr2:
        return True
    while arr1[i] != arr2[j]:
        j += 1
    for i in range(1, len(arr1) - 1):
        if j > len(arr1) - 1:
            j = 0:
        if arr1[i] != arr[j]:
            return False
        j += 1
    return True
