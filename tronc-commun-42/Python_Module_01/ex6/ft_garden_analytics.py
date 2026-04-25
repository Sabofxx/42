#!/usr/bin/env python3


class Plant:
    def __init__(self, name: str, height: int) -> None:
        self.name = name
        self.height = height

    def grow(self) -> None:
        self.height += 1
        print(f"{self.name} grew 1cm")

    def get_info(self) -> str:
        return f"- {self.name}: {self.height}cm"


class FloweringPlant(Plant):
    def __init__(self, name: str, height: int, flower_color: str) -> None:
        super().__init__(name, height)
        self.flower_color = flower_color
        self.is_blooming = True

    def get_info(self) -> str:
        bloom_state = "blooming" if self.is_blooming else "not blooming"
        return (
            f"- {self.name}: {self.height}cm, {self.flower_color} flowers "
            f"({bloom_state})"
        )


class PrizeFlower(FloweringPlant):
    def __init__(
        self,
        name: str,
        height: int,
        flower_color: str,
        prize_points: int
    ) -> None:
        super().__init__(name, height, flower_color)
        self.prize_points = prize_points

    def get_info(self) -> str:
        bloom_state = "blooming" if self.is_blooming else "not blooming"
        return (
            f"- {self.name}: {self.height}cm, {self.flower_color} flowers "
            f"({bloom_state}), Prize points: {self.prize_points}"
        )


class GardenManager:
    total_gardens = 0

    class GardenStats:
        def __init__(self) -> None:
            self.plants_added = 0
            self.total_growth = 0

        def record_plant_added(self) -> None:
            self.plants_added += 1

        def record_growth(self, amount: int) -> None:
            self.total_growth += amount

        def get_summary(self) -> str:
            return (
                f"Plants added: {self.plants_added}, "
                f"Total growth: {self.total_growth}cm"
            )

    def __init__(self, owner: str) -> None:
        self.owner = owner
        self.plants: list[Plant] = []
        self.stats = self.GardenStats()
        GardenManager.total_gardens += 1

    def add_plant(self, plant: Plant) -> None:
        self.plants.append(plant)
        self.stats.record_plant_added()
        print(f"Added {plant.name} to {self.owner}'s garden")

    def grow_all_plants(self) -> None:
        print(f"{self.owner} is helping all plants grow...")
        for plant in self.plants:
            plant.grow()
            self.stats.record_growth(1)

    def show_report(self) -> None:
        regular_count = 0
        flowering_count = 0
        prize_count = 0

        print("=== Alice's Garden Report ===")
        print("Plants in garden:")
        for plant in self.plants:
            print(plant.get_info())
            if isinstance(plant, PrizeFlower):
                prize_count += 1
            elif isinstance(plant, FloweringPlant):
                flowering_count += 1
            else:
                regular_count += 1
        print()
        print(self.stats.get_summary())
        print(
            f"Plant types: {regular_count} regular, "
            f"{flowering_count} flowering, {prize_count} prize flowers"
        )

    @classmethod
    def create_garden_network(cls) -> str:
        return f"Total gardens managed: {cls.total_gardens}"

    @staticmethod
    def validate_height(height: int) -> bool:
        return height >= 0

    @staticmethod
    def calculate_garden_score(manager: "GardenManager") -> int:
        score = 0

        for plant in manager.plants:
            score += plant.height
            if isinstance(plant, FloweringPlant):
                score += 15
            if isinstance(plant, PrizeFlower):
                score += plant.prize_points

        return score


def main() -> None:
    alice_garden = GardenManager("Alice")
    bob_garden = GardenManager("Bob")

    oak = Plant("Oak Tree", 100)
    rose = FloweringPlant("Rose", 25, "red")
    sunflower = PrizeFlower("Sunflower", 50, "yellow", 10)
    cactus = Plant("Cactus", 92)

    bob_garden.plants.append(cactus)

    print("=== Garden Management System Demo ===")
    print()
    alice_garden.add_plant(oak)
    alice_garden.add_plant(rose)
    alice_garden.add_plant(sunflower)
    print()
    alice_garden.grow_all_plants()
    print()
    alice_garden.show_report()
    print()
    print(f"Height validation test: {GardenManager.validate_height(10)}")
    alice_score = GardenManager.calculate_garden_score(alice_garden)
    bob_score = GardenManager.calculate_garden_score(bob_garden)
    print(f"Garden scores - Alice: {alice_score}, Bob: {bob_score}")
    print(GardenManager.create_garden_network())


if __name__ == "__main__":
    main()
