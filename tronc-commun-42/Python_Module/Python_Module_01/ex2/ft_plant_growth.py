class Plant:
    def __init__(self, name: str, height: int, age: int) -> None:
        self.name = name
        self.height = height
        self.age = age

    def grow(self) -> None:
        self.height += 1

    def age_one_day(self) -> None:
        self.age += 1

    def get_info(self) -> str:
        return f"{self.name}: {self.height}cm, {self.age} days old"


if __name__ == "__main__":
    plant = Plant("Rose", 25, 30)

    print("=== Day 1 ===")
    print(plant.get_info())

    for _ in range(6):
        plant.grow()
        plant.age_one_day()

    print("=== Day 7 ===")
    print(plant.get_info())
    print("Growth this week: +6cm")
