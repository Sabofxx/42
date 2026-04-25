class Plant:
    def __init__(self, name: str, height_cm: int, age_days: int) -> None:
        self.name = name
        self.height_cm = height_cm
        self.age_days = age_days

    def get_info(self) -> str:
        return f"{self.name} ({self.height_cm}cm, {self.age_days} days)"


def main() -> None:
    print("=== Plant Factory Output ===")

    plants: list[Plant] = [
        Plant("Rose", 25, 30),
        Plant("Oak", 200, 365),
        Plant("Cactus", 5, 90),
        Plant("Sunflower", 80, 45),
        Plant("Fern", 15, 120),
    ]

    for plant in plants:
        print(f"Created: {plant.get_info()}")

    print()
    print(f"Total plants created: {len(plants)}")


if __name__ == "__main__":
    main()
