def alternate_case(s: str) -> str:
    result = ""
    upper = True

    for c in s:
        if c.isalpha():
            if upper:
                result += c.upper()
            else:
                result += c.lower()
            upper = not upper
        else:
            result += c
    return result


def main() -> None:
    print(alternate_case("hello world"))  # "HeLlO WoRlD"
    print(alternate_case("42madrid"))  # "42MaDrId"
    print(alternate_case("python3.9 rocks!"))  # "PyThOn3.9 RoCkS!"
    print(alternate_case("a!b?c"))  # "A!b?C"


if __name__ == "__main__":
    main()
