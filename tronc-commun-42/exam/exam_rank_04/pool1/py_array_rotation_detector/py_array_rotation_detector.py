def array_rotation_detector(arr1: list[int], arr2: list[int]) -> bool:
    if len(arr1) != len(arr2):
        return False
    doubled = arr1 + arr1
    return any(doubled[i:i+len(arr1)] == arr2 for i in range(len(arr1)))


# print(array_rotation_detector([1, 2, 3, 4, 5], [3, 4, 5, 1, 2])) #True
# print(array_rotation_detector([1, 2, 3, 4, 5], [4, 5, 1, 2, 3])) #True
# print(array_rotation_detector([1, 2, 3, 4, 5], [1, 2, 3, 4, 5])) #True
# print(array_rotation_detector([1, 2, 3, 4, 5], [2, 3, 4, 5, 1])) #True
# print(array_rotation_detector([1, 2, 3], [1, 3, 2])) #False
# print(array_rotation_detector([1, 2, 3], [1, 2])) #False
# print(array_rotation_detector([], [])) #True
# print(array_rotation_detector([1, 1, 1], [1, 1, 1])) #True
# print(array_rotation_detector([1, 1, 1], [11111111])) #False
