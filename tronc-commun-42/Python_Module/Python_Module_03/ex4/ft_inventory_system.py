import sys


def main() -> None:
    print("=== Inventory System Analysis ===")
    inventory: dict[str, int] = {}
    for arg in sys.argv[1:]:
        parts = arg.split(":")
        if len(parts) != 2:
            print(f"Error - invalid parameter '{arg}'")
            continue
        name, qty_str = parts
        if name in inventory:
            print(
                f"Redundant item '{name}' - discarding"
            )
            continue
        try:
            inventory[name] = int(qty_str)
        except ValueError as e:
            print(f"Quantity error for '{name}': {e}")
    print(f"Got inventory: {inventory}")
    print(f"Item list: {list(inventory.keys())}")
    total = sum(inventory.values())
    item_count = len(inventory)
    print(
        f"Total quantity of the {item_count} "
        f"items: {total}"
    )
    for item, qty in inventory.items():
        pct = round(qty / total * 100, 1)
        print(f"Item {item} represents {pct}%")
    most = max(inventory, key=lambda k: inventory[k])
    least = min(inventory, key=lambda k: inventory[k])
    print(
        f"Item most abundant: {most} "
        f"with quantity {inventory[most]}"
    )
    print(
        f"Item least abundant: {least} "
        f"with quantity {inventory[least]}"
    )
    inventory.update({"magic_item": 1})
    print(f"Updated inventory: {inventory}")


if __name__ == "__main__":
    main()
