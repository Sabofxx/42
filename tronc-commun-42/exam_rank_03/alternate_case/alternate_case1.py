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
    print(alternate_case("Hello world"))
    print(alternate_case("42madrid"))
    print(alternate_case("python3.9 rocks!"))
    print(alternate_case("a?b.c"))


if __name__ == "__main__":
    main()
