def palindrome_partitioner(s: str) -> int:
    n = len(s)
    if n == 0:
        return 0
    dp = [i for i in range(n)]
    for i in range(n):
        for j in range(i + 1):
            if s[j:i + 1] == s[j:i + 1][::-1]:
                if j == 0:
                    dp[i] = 0
                else:
                    dp[i] = min(dp[i], dp[j - 1] + 1)
    return dp[-1]

# res = palindrome_partitioner("aab")
# print(f"excepted: 1")
# print(f"got: {res}\n")

# res = palindrome_partitioner("aba")
# print(f"excepted: 0")
# print(f"got: {res}\n")

# res = palindrome_partitioner("abcba")
# print(f"excepted: 0")
# print(f"got: {res}\n")

# res = palindrome_partitioner("abcd")
# print(f"excepted: 3")
# print(f"got: {res}\n")

# res = palindrome_partitioner("aabaa")
# print(f"excepted: 0")
# print(f"got: {res}\n")

# res = palindrome_partitioner("abac")
# print(f"excepted: 1")
# print(f"got: {res}\n")

# res = palindrome_partitioner("")
# print(f"excepted: 0")
# print(f"got: {res}\n")

