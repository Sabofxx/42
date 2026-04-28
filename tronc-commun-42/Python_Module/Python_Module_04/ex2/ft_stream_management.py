import sys


def main() -> None:
    print("=== CYBER ARCHIVES - COMMUNICATION SYSTEM ===")
    archivist_id = input(
        "Input Stream active. Enter archivist ID: "
    )
    status = input(
        "Input Stream active. Enter status report: "
    )
    sys.stdout.write(
        f"[STANDARD] Archive status from "
        f"{archivist_id}: {status}\n"
    )
    sys.stderr.write(
        "[ALERT] System diagnostic:"
        " Communication channels verified\n"
    )
    sys.stdout.write(
        "[STANDARD] Data transmission complete\n"
    )
    print("Three-channel communication test successful.")


if __name__ == "__main__":
    main()
