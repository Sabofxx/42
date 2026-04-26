def hamming_distance(a, b):
    return sum(x != y for x, y in zip(a, b))


def restricted_decode(received, codewords, t):
    for c in codewords:
        if hamming_distance(received, c) <= t:
            return c
    return None


code = [
    "0000",
    "1111",
    "0011",
    "1100"
]

received = "0010"
t = 1

decoded = restricted_decode(received, code, t)

if decoded:
    print("Decodificado: ", decoded)
else:
    print("Error: too erros")
