def main() -> None:
    print("=== CYBER ARCHIVES - DATA RECOVERY SYSTEM ===")
    filename = "ancient_fragment.txt"
    print(f"Accessing Storage Vault: {filename}")
    try:
        file = open(filename, "r")
        data = file.read()
        file.close()
    except FileNotFoundError:
        print(
            "ERROR: Storage vault not found."
            " Run data generator first."
        )
        return
    print("Connection established...")
    print("RECOVERED DATA:")
    for line in data.splitlines():
        if line.strip():
            print(line)
    print("Data recovery complete. Storage unit disconnected.")


if __name__ == "__main__":
    main()
