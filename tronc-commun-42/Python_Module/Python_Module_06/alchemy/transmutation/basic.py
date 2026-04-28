from alchemy.elements import create_fire, create_earth


def lead_to_gold() -> str:
    fire = create_fire()
    return f"Lead transmuted to gold using {fire}"


def stone_to_gem() -> str:
    earth = create_earth()
    return f"Stone transmuted to gem using {earth}"
