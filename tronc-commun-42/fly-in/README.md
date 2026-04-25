*Fly-in is a drone routing simulation that finds optimal paths through a graph network and simulates multi-drone movement turn by turn.*

## Description

Fly-in solves the problem of routing N drones from a start zone to an end zone through a network of interconnected zones, each with capacity constraints. The goal is to minimize the total number of simulation turns required for all drones to reach the destination.

The project parses a map file describing the network topology (zones, connections, capacities, special zone types), computes optimal routing paths using a modified Dijkstra algorithm, then runs a turn-based simulation where drones move through the network respecting all capacity constraints.

### Zone Types

- **Normal**: standard zone, 1 turn to traverse
- **Restricted**: slow zone, 2 turns to traverse (1 turn in transit on the connection, then arrival)
- **Priority**: preferred zone, 1 turn to traverse but weighted lower in pathfinding
- **Blocked**: impassable, drones cannot enter

### Constraints

- Each zone has a maximum drone capacity (default 1), except start and end zones (unlimited)
- Each connection has a maximum simultaneous usage capacity (default 1)
- Drones move simultaneously each turn, respecting all capacity limits

## Instructions

### Prerequisites

- Python 3.10 or higher
- pip

### Installation

```bash
make install
```

### Running

```bash
make run                                    # default map
make run MAP=maps/medium/01_dead_end_trap.txt  # specific map
```

Or directly:

```bash
python main.py <map_file> [--visual] [--raw]
```

- `--visual`: show colored terminal visualization with progress bars
- `--raw`: show raw output (one line per turn, drone movements)
- No flag: show both visual and raw output

### Other Commands

```bash
make debug MAP=maps/easy/01_linear_path.txt  # visual mode only
make lint                                     # flake8 check
make lint-strict                              # flake8 + mypy strict
make clean                                    # remove __pycache__
```

## Resources

- Python 3.10+ with type hints
- flake8 for linting
- mypy for static type checking
- No external runtime dependencies

## Algorithm

### Pathfinding: Modified Dijkstra with Node-Disjoint Path Discovery

The pathfinder uses an iterative approach to find multiple distinct paths:

1. **Dijkstra with weights**: priority zones get weight 0 (preferred), normal zones weight 1, restricted zones weight 2. This naturally routes drones through faster paths first.

2. **Node-disjoint iteration**: after finding the shortest path, intermediate nodes are marked as "used" (their capacity is consumed for future path searches). The next Dijkstra run avoids fully-used nodes, finding an alternative route. This repeats until no more paths exist.

3. **Drone assignment**: drones are distributed across available paths using a greedy algorithm. Each drone is assigned to the path with the lowest expected finish time, calculated as `path_cost + number_of_drones_already_on_path`. This balances load across paths to minimize total turns.

### Simulation: Turn-Based Capacity-Aware Movement

Each simulation turn executes in three phases:

1. **Plan arrivals**: drones that were in transit (from restricted zone movement) complete their arrival.

2. **Plan departures**: for each waiting/moving drone, check if its next zone has available capacity and the connection is not saturated. Drones are sorted by remaining path length (shortest first) to prioritize drones closest to delivery.

3. **Execute moves**: all planned movements happen simultaneously. Drones entering restricted zones enter an IN_TRANSIT state for one turn before arriving.

The simulation respects zone capacity by tracking current occupancy plus planned arrivals/departures within the same turn, preventing capacity violations even with simultaneous movement.

## Visual Representation

The terminal visualization provides:

- **Header**: network statistics (drone count, zone count, link count, start/end zones)
- **Topology view**: all zones listed with their type symbol, special properties, and capacity
- **Path display**: computed routing paths shown before simulation starts
- **Turn-by-turn output**: each turn shows a progress bar with delivered/total count, followed by colored drone movements
- **Summary**: final statistics with total turns and delivery status

Zone type symbols in the topology view:
- `[o]` Normal zone
- `[X]` Blocked zone
- `[~]` Restricted zone (2-turn traversal)
- `[*]` Priority zone (preferred routing)

Output format per turn: `D<id>-<destination>` for each drone movement, space-separated. For restricted zones, the connection name is shown during the transit turn.
