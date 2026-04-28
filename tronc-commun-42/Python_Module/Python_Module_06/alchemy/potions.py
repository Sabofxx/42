from .elements import (
    create_fire,
    create_water,
    create_earth,
    create_air,
)


def healing_potion() -> str:
    fire = create_fire()
    water = create_water()
    return (
        f"Healing potion brewed with {fire}"
        f" and {water}"
    )


def strength_potion() -> str:
    earth = create_earth()
    fire = create_fire()
    return (
        f"Strength potion brewed with {earth}"
        f" and {fire}"
    )


def invisibility_potion() -> str:
    air = create_air()
    water = create_water()
    return (
        f"Invisibility potion brewed with {air}"
        f" and {water}"
    )


def wisdom_potion() -> str:
    results = ", ".join([
        create_fire(),
        create_water(),
        create_earth(),
        create_air(),
    ])
    return (
        "Wisdom potion brewed with"
        f" all elements: {results}"
    )
