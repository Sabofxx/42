import sys
from typing import Optional
from models.network import Network
from models.drone import Drone, DroneState
from models.zone import ZoneType


COLORS: dict[str, str] = {
    "green": "\033[92m",
    "red": "\033[91m",
    "blue": "\033[94m",
    "yellow": "\033[93m",
    "orange": "\033[38;5;208m",
    "cyan": "\033[96m",
    "magenta": "\033[95m",
    "purple": "\033[35m",
    "white": "\033[97m",
    "gray": "\033[90m",
    "brown": "\033[38;5;130m",
    "lime": "\033[38;5;118m",
    "gold": "\033[38;5;220m",
    "crimson": "\033[38;5;196m",
    "violet": "\033[38;5;135m",
    "maroon": "\033[38;5;88m",
    "darkred": "\033[38;5;52m",
    "rainbow": "\033[38;5;201m",
    "black": "\033[30m",
}

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"


class TerminalDisplay:
    def __init__(self, network: Network, visual: bool = True) -> None:
        self.network = network
        self.visual = visual

    def _colorize(
        self, text: str, color: Optional[str]
    ) -> str:
        if not self.visual or color is None:
            return text
        code = COLORS.get(color, "")
        if not code:
            return text
        return f"{code}{text}{RESET}"

    def _zone_type_symbol(self, zone_type: ZoneType) -> str:
        symbols = {
            ZoneType.NORMAL: "o",
            ZoneType.BLOCKED: "X",
            ZoneType.RESTRICTED: "~",
            ZoneType.PRIORITY: "*",
        }
        return symbols.get(zone_type, "o")

    def print_header(self) -> None:
        if not self.visual:
            return
        print(f"\n{BOLD}{'=' * 60}{RESET}")
        print(f"{BOLD}  FLY-IN Drone Simulation{RESET}")
        print(f"{'=' * 60}")
        print(
            f"  Drones: {self._colorize(str(self.network.nb_drones), 'cyan')}"
        )
        nz = str(len(self.network.zones))
        nc = str(len(self.network.connections))
        sz = str(self.network.start_zone)
        print(
            f"  Zones:  {self._colorize(nz, 'yellow')}"
        )
        print(
            f"  Links:  {self._colorize(nc, 'blue')}"
        )
        print(
            f"  Start:  {self._colorize(sz, 'green')}"
        )
        print(
            f"  End:    {self._colorize(str(self.network.end_zone), 'red')}"
        )
        print(f"{'=' * 60}\n")

    def print_network(self) -> None:
        if not self.visual:
            return
        print(f"{BOLD}Network Topology:{RESET}")
        for name, zone in self.network.zones.items():
            symbol = self._zone_type_symbol(zone.zone_type)
            label = f"  [{symbol}] {name}"
            if zone.is_start:
                label += " (START)"
            elif zone.is_end:
                label += " (END)"
            extras: list[str] = []
            if zone.zone_type != ZoneType.NORMAL:
                extras.append(f"type={zone.zone_type.value}")
            if zone.max_drones != 1:
                extras.append(f"cap={zone.max_drones}")
            if extras:
                label += f" [{', '.join(extras)}]"
            print(self._colorize(label, zone.color))
        print()

    def print_paths(self, paths: list[list[str]]) -> None:
        if not self.visual:
            return
        print(f"{BOLD}Computed Paths:{RESET}")
        for i, path in enumerate(paths):
            path_str = " -> ".join(path)
            print(f"  Path {i + 1}: {self._colorize(path_str, 'cyan')}")
        print()

    def print_turn(
        self, turn_num: int, line: str,
        delivered: int, total: int,
    ) -> None:
        if not self.visual:
            return
        bar_len = 30
        filled = int(bar_len * delivered / total) if total > 0 else 0
        bar = (
            self._colorize("█" * filled, "green")
            + self._colorize("░" * (bar_len - filled), "gray")
        )
        progress = f"[{bar}] {delivered}/{total}"

        moves = line.split()
        colored_moves: list[str] = []
        for move in moves:
            parts = move.split("-", 1)
            drone_label = self._colorize(parts[0], "cyan")
            dest = self._colorize(parts[1], "yellow") if len(parts) > 1 else ""
            colored_moves.append(f"{drone_label}-{dest}")

        print(
            f"  {DIM}Turn {turn_num:3d}{RESET}  "
            f"{progress}  "
            f"{' '.join(colored_moves)}"
        )

    def print_summary(
        self, total_turns: int, drones: list[Drone]
    ) -> None:
        delivered = sum(
            1 for d in drones if d.state == DroneState.DELIVERED
        )
        total = len(drones)

        if self.visual:
            print(f"\n{'=' * 60}")
            print(f"{BOLD}  Simulation Complete{RESET}")
            print(f"{'=' * 60}")
            print(
                f"  Total turns: "
                f"{self._colorize(str(total_turns), 'cyan')}"
            )
            print(
                f"  Delivered:   "
                f"{self._colorize(f'{delivered}/{total}', 'green')}"
            )
            if delivered == total:
                print(
                    f"  Status:      "
                    f"{self._colorize('ALL DRONES DELIVERED', 'green')}"
                )
            else:
                print(
                    f"  Status:      "
                    f"{self._colorize('INCOMPLETE', 'red')}"
                )
            print(f"{'=' * 60}\n")

    def print_raw_output(self, turns: list[str]) -> None:
        for line in turns:
            sys.stdout.write(line + "\n")
