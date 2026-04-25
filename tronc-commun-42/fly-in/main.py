import sys
from parser.map_parser import parse_map, ParseError
from engine.pathfinder import Pathfinder
from engine.simulation import Simulation
from visual.terminal import TerminalDisplay


def main() -> int:
    if len(sys.argv) < 2:
        sys.stderr.write(
            "Usage: python main.py <map_file> [--visual] [--raw]\n"
        )
        return 1

    map_file = sys.argv[1]
    has_visual = "--visual" in sys.argv
    has_raw = "--raw" in sys.argv

    if not has_visual and not has_raw:
        has_visual = True
        has_raw = True

    try:
        network = parse_map(map_file)
    except ParseError as e:
        sys.stderr.write(f"Parse error: {e}\n")
        return 1
    except FileNotFoundError:
        sys.stderr.write(f"Error: File not found: {map_file}\n")
        return 1

    display = TerminalDisplay(network, visual=has_visual)

    display.print_header()
    display.print_network()

    pathfinder = Pathfinder(network)
    aug_paths = pathfinder.find_augmenting_paths()

    if not aug_paths:
        sys.stderr.write("Error: No valid path from start to end\n")
        return 1

    display.print_paths(aug_paths)

    drone_paths = pathfinder.assign_drones()

    sim = Simulation(network, drone_paths)
    turns = sim.run()

    if has_visual:
        total = len(sim.drones)
        for i, line in enumerate(turns):
            td = sim.turn_delivered
            delivered = td[i] if i < len(td) else 0
            display.print_turn(i + 1, line, delivered, total)
        display.print_summary(len(turns), sim.drones)

    if has_raw:
        display.print_raw_output(turns)

    return 0


if __name__ == "__main__":
    sys.exit(main())
