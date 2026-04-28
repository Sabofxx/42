VALID_ELEMENTS = {"fire", "water", "earth", "air"}


def validate_ingredients(ingredients: str) -> str:
    words = ingredients.lower().split()
    for word in words:
        if word in VALID_ELEMENTS:
            return f"{ingredients} - VALID"
    return f"{ingredients} - INVALID"
