import sys
import os
import site


def main() -> None:
    venv = os.environ.get("VIRTUAL_ENV")
    python_path = sys.executable

    if venv:
        env_name = os.path.basename(venv)
        print("MATRIX STATUS: Welcome to the construct")
        print(f"Current Python: {python_path}")
        print(f"Virtual Environment: {env_name}")
        print(f"Environment Path: {venv}")
        print()
        print(
            "SUCCESS: You're in an isolated"
            " environment!"
        )
        print(
            "Safe to install packages without"
            " affecting the global system."
        )
        print()
        packages = site.getsitepackages()
        if packages:
            print(
                "Package installation path:"
            )
            print(packages[0])
    else:
        print(
            "MATRIX STATUS:"
            " You're still plugged in"
        )
        print(f"Current Python: {python_path}")
        print("Virtual Environment: None detected")
        print()
        print(
            "WARNING: You're in the"
            " global environment!"
        )
        print(
            "The machines can see everything"
            " you install."
        )
        print()
        print("To enter the construct, run:")
        print("  python -m venv matrix_env")
        print(
            "  source matrix_env/bin/activate"
            "  # On Unix"
        )
        print(
            "  matrix_env\\Scripts\\activate"
            "  # On Windows"
        )
        print()
        print("Then run this program again.")


if __name__ == "__main__":
    main()
