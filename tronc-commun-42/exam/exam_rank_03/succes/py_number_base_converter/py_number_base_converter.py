def py_number_base_converter(number: str, from_base: int, to_base: int) -> str:
    if from_base < 2 or from_base > 36 or to_base < 2 or to_base > 36:
        return 'ERROR'
    if not number:
        return 'ERROR'

    digits = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    value = 0
    for char in number:
        if char not in digits:
            return 'ERROR'
        d = digits.index(char)
        if d >= from_base:
            return 'ERROR'
        value = value * from_base + d

    if value == 0:
        return '0'

    result = ''
    while value > 0:
        result = digits[value % to_base] + result
        value //= to_base
    return result
