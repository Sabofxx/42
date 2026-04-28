import functools
import time
from collections.abc import Callable
from typing import Any


def spell_timer(func: Callable) -> Callable:
    """Time execution decorator."""
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        print(f"Casting {func.__name__}...")
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(
            "Spell completed in"
            f" {elapsed:.3f} seconds"
        )
        return result
    return wrapper


def power_validator(min_power: int) -> Callable:
    """Parameterized validation decorator."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(
            *args: Any, **kwargs: Any,
        ) -> Any:
            power = args[0]
            if power < min_power:
                return (
                    "Insufficient power"
                    " for this spell"
                )
            return func(*args, **kwargs)
        return wrapper
    return decorator


def retry_spell(max_attempts: int) -> Callable:
    """Retry decorator for failed spells."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(
            *args: Any, **kwargs: Any,
        ) -> Any:
            for i in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception:
                    if i < max_attempts:
                        print(
                            "Spell failed,"
                            " retrying..."
                            f" (attempt {i}"
                            f"/{max_attempts})"
                        )
            return (
                "Spell casting failed after"
                f" {max_attempts} attempts"
            )
        return wrapper
    return decorator


class MageGuild:
    """Mage guild with validation."""

    @staticmethod
    def validate_mage_name(name: str) -> bool:
        """Check if mage name is valid."""
        return (
            len(name) >= 3
            and all(
                c.isalpha() or c == ' '
                for c in name
            )
        )

    def cast_spell(
        self, spell_name: str, power: int,
    ) -> str:
        """Cast a spell with power validation."""
        @power_validator(min_power=10)
        def _cast(pwr: int) -> str:
            return (
                f"Successfully cast {spell_name}"
                f" with {pwr} power"
            )
        result: str = _cast(power)
        return result


def main() -> None:
    """Demonstrate decorator mastery."""
    print("Testing spell timer...")

    @spell_timer
    def fireball() -> str:
        time.sleep(0.1)
        return "Fireball cast!"

    result = fireball()
    print(f"Result: {result}")

    print("Testing retrying spell...")

    @retry_spell(max_attempts=3)
    def unstable() -> str:
        raise ValueError("Boom!")

    print(unstable())

    @retry_spell(max_attempts=3)
    def stable() -> str:
        return "Waaaaaaagh spelled !"

    print(stable())

    print("Testing MageGuild...")
    print(MageGuild.validate_mage_name("Gandalf"))
    print(MageGuild.validate_mage_name("Ab"))
    guild = MageGuild()
    print(guild.cast_spell("Lightning", 15))
    print(guild.cast_spell("Lightning", 5))


if __name__ == "__main__":
    main()
