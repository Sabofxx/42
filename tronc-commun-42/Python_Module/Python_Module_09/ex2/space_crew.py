from datetime import datetime
from enum import Enum
from typing import List

from pydantic import BaseModel, Field, model_validator


class Rank(str, Enum):
    """Crew member ranks."""
    CADET = "cadet"
    OFFICER = "officer"
    LIEUTENANT = "lieutenant"
    CAPTAIN = "captain"
    COMMANDER = "commander"


class CrewMember(BaseModel):
    """Individual crew member model."""

    member_id: str = Field(
        ..., min_length=3, max_length=10
    )
    name: str = Field(
        ..., min_length=2, max_length=50
    )
    rank: Rank
    age: int = Field(..., ge=18, le=80)
    specialization: str = Field(
        ..., min_length=3, max_length=30
    )
    years_experience: int = Field(
        ..., ge=0, le=50
    )
    is_active: bool = True


class SpaceMission(BaseModel):
    """Space mission model with crew."""

    mission_id: str = Field(
        ..., min_length=5, max_length=15
    )
    mission_name: str = Field(
        ..., min_length=3, max_length=100
    )
    destination: str = Field(
        ..., min_length=3, max_length=50
    )
    launch_date: datetime
    duration_days: int = Field(
        ..., ge=1, le=3650
    )
    crew: List[CrewMember] = Field(
        ..., min_length=1, max_length=12
    )
    mission_status: str = "planned"
    budget_millions: float = Field(
        ..., ge=1.0, le=10000.0
    )

    @model_validator(mode="after")
    def validate_mission(self) -> "SpaceMission":
        """Mission safety validation."""
        if not self.mission_id.startswith("M"):
            raise ValueError(
                "Mission ID must start with 'M'"
            )
        has_leader = any(
            m.rank in (Rank.COMMANDER, Rank.CAPTAIN)
            for m in self.crew
        )
        if not has_leader:
            raise ValueError(
                "Mission must have at least one"
                " Commander or Captain"
            )
        if self.duration_days > 365:
            experienced = sum(
                1 for m in self.crew
                if m.years_experience >= 5
            )
            ratio = experienced / len(self.crew)
            if ratio < 0.5:
                raise ValueError(
                    "Long missions (> 365 days)"
                    " need 50% experienced crew"
                    " (5+ years)"
                )
        inactive = [
            m.name for m in self.crew
            if not m.is_active
        ]
        if inactive:
            raise ValueError(
                "All crew members must be active"
            )
        return self


def main() -> None:
    print("Space Mission Crew Validation")
    print("=" * 40)

    crew = [
        CrewMember(
            member_id="SC001",
            name="Sarah Connor",
            rank=Rank.COMMANDER,
            age=45,
            specialization="Mission Command",
            years_experience=20,
        ),
        CrewMember(
            member_id="SC002",
            name="John Smith",
            rank=Rank.LIEUTENANT,
            age=35,
            specialization="Navigation",
            years_experience=10,
        ),
        CrewMember(
            member_id="SC003",
            name="Alice Johnson",
            rank=Rank.OFFICER,
            age=28,
            specialization="Engineering",
            years_experience=6,
        ),
    ]

    mission = SpaceMission(
        mission_id="M2024_MARS",
        mission_name="Mars Colony Establishment",
        destination="Mars",
        launch_date="2024-12-01T06:00:00",
        duration_days=900,
        crew=crew,
        budget_millions=2500.0,
    )

    print("Valid mission created:")
    print(f"  Mission: {mission.mission_name}")
    print(f"  ID: {mission.mission_id}")
    print(f"  Destination: {mission.destination}")
    print(
        f"  Duration: {mission.duration_days} days"
    )
    print(
        f"  Budget: ${mission.budget_millions}M"
    )
    print(f"  Crew size: {len(mission.crew)}")
    print("  Crew members:")
    for m in mission.crew:
        print(
            f"    - {m.name} ({m.rank.value})"
            f" - {m.specialization}"
        )

    print("=" * 40)
    print("Expected validation error:")
    try:
        bad_crew = [
            CrewMember(
                member_id="BC001",
                name="Rookie",
                rank=Rank.CADET,
                age=20,
                specialization="Training",
                years_experience=0,
            ),
        ]
        SpaceMission(
            mission_id="M2024_BAD",
            mission_name="Bad Mission",
            destination="Moon",
            launch_date="2024-06-01T08:00:00",
            duration_days=30,
            crew=bad_crew,
            budget_millions=100.0,
        )
    except Exception as e:
        for error in e.errors():  # type: ignore
            print(f"  {error['msg']}")


if __name__ == "__main__":
    main()
