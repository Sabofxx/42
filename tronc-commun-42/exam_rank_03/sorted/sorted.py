#!/usr/bin/env python3


def main() -> None:
    words = ["banana", "kiwi", "apple", "fig"]
    students = [("Ana", 8.5), ("Luis", 6.0), ("Marta", 9.2)]
    data = [("Ana", 20), ("Luis", 20), ("Marta", 18)]

    class Student:
        def __init__(self, name, grade):
            self.name = name
            self.grade = grade

    sorted_students = [
        Student("Ana", 8), Student("Luis", 6), Student("Marta", 9)]

    print(sorted(words, key=lambda x: len(x)))
    print(sorted(students, key=lambda x: x[1], reverse=True))
    print(sorted(data, key=lambda x: (x[1], x[0])))

    sorted(sorted_students, key=lambda s: s.grade)


if __name__ == "__main__":
    main()
