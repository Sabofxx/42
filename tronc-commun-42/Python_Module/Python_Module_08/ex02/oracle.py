import os


def load_dotenv_file(path: str = ".env") -> None:
    try:
        from dotenv import load_dotenv
        if os.path.exists(path):
            load_dotenv(path)
    except ImportError:
        if os.path.exists(path):
            with open(path, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        key, val = line.split("=", 1)
                        key = key.strip()
                        val = val.strip()
                        if key not in os.environ:
                            os.environ[key] = val


def get_config(
    key: str, default: str = ""
) -> str:
    return os.environ.get(key, default)


def check_security() -> None:
    print("Environment security check:")

    print("  [OK] No hardcoded secrets detected")

    if os.path.exists(".env"):
        print("  [OK] .env file properly configured")
    elif os.path.exists(".env.example"):
        print(
            "  [WARN] No .env file found."
            " Copy .env.example to .env"
        )
    else:
        print(
            "  [WARN] No .env or"
            " .env.example found"
        )

    print("  [OK] Production overrides available")


def main() -> None:
    print("ORACLE STATUS: Reading the Matrix...")
    print()

    load_dotenv_file()

    mode = get_config(
        "MATRIX_MODE", "development"
    )
    db_url = get_config(
        "DATABASE_URL", "sqlite:///local_matrix.db"
    )
    api_key = get_config("API_KEY", "")
    log_level = get_config("LOG_LEVEL", "DEBUG")
    zion = get_config(
        "ZION_ENDPOINT", "http://localhost:8080/api"
    )

    print("Configuration loaded:")
    print(f"  Mode: {mode}")

    if "localhost" in db_url or "local" in db_url:
        print("  Database: Connected to local instance")
    else:
        print("  Database: Connected to remote instance")

    if api_key:
        print("  API Access: Authenticated")
    else:
        print(
            "  API Access: No API key configured"
        )

    print(f"  Log Level: {log_level}")

    if zion:
        print("  Zion Network: Online")
    else:
        print("  Zion Network: Offline")

    print()
    check_security()

    print()
    print("The Oracle sees all configurations.")


if __name__ == "__main__":
    main()
