import re
from typing import Optional
from models.zone import Zone, ZoneType
from models.connection import Connection
from models.network import Network


class ParseError(Exception):
    def __init__(self, line_num: int, message: str) -> None:
        self.line_num = line_num
        super().__init__(f"Line {line_num}: {message}")


def _parse_metadata(raw: str, line_num: int) -> dict[str, str]:
    raw = raw.strip()
    if not raw.startswith("[") or not raw.endswith("]"):
        raise ParseError(line_num, f"Invalid metadata syntax: {raw}")
    inner = raw[1:-1].strip()
    if not inner:
        return {}
    meta: dict[str, str] = {}
    for token in inner.split():
        if "=" not in token:
            raise ParseError(
                line_num, f"Invalid metadata token: {token}"
            )
        key, value = token.split("=", 1)
        meta[key] = value
    return meta


def _parse_zone_type(type_str: str, line_num: int) -> ZoneType:
    try:
        return ZoneType(type_str)
    except ValueError:
        raise ParseError(
            line_num,
            f"Invalid zone type '{type_str}'. "
            f"Must be: normal, blocked, restricted, priority",
        )


def _parse_zone_line(
    parts: list[str], line_num: int, is_start: bool = False,
    is_end: bool = False,
) -> Zone:
    if len(parts) < 3:
        raise ParseError(
            line_num, "Zone requires: <name> <x> <y> [metadata]"
        )
    name = parts[0]
    if "-" in name:
        raise ParseError(
            line_num, f"Zone name cannot contain dashes: '{name}'"
        )
    try:
        x = int(parts[1])
        y = int(parts[2])
    except ValueError:
        raise ParseError(
            line_num, "Zone coordinates must be integers"
        )
    zone_type = ZoneType.NORMAL
    color: Optional[str] = None
    max_drones = 1
    meta_str = " ".join(parts[3:])
    if meta_str:
        bracket_match = re.search(r"\[.*\]", meta_str)
        if bracket_match:
            meta = _parse_metadata(bracket_match.group(), line_num)
            if "zone" in meta:
                zone_type = _parse_zone_type(meta["zone"], line_num)
            if "color" in meta:
                color = meta["color"]
            if "max_drones" in meta:
                try:
                    max_drones = int(meta["max_drones"])
                    if max_drones < 1:
                        raise ValueError
                except ValueError:
                    raise ParseError(
                        line_num,
                        "max_drones must be a positive integer",
                    )
    return Zone(
        name=name, x=x, y=y, zone_type=zone_type,
        color=color, max_drones=max_drones,
        is_start=is_start, is_end=is_end,
    )


def _parse_connection_line(
    parts: list[str], line_num: int
) -> Connection:
    if len(parts) < 1:
        raise ParseError(
            line_num, "Connection requires: <zone1>-<zone2> [metadata]"
        )
    link = parts[0]
    if link.count("-") < 1:
        raise ParseError(
            line_num, f"Invalid connection format: '{link}'"
        )
    dash_idx = link.index("-")
    zone1 = link[:dash_idx]
    zone2 = link[dash_idx + 1:]
    if not zone1 or not zone2:
        raise ParseError(
            line_num, f"Invalid connection format: '{link}'"
        )
    max_link_capacity = 1
    meta_str = " ".join(parts[1:])
    if meta_str:
        bracket_match = re.search(r"\[.*\]", meta_str)
        if bracket_match:
            meta = _parse_metadata(bracket_match.group(), line_num)
            if "max_link_capacity" in meta:
                try:
                    max_link_capacity = int(meta["max_link_capacity"])
                    if max_link_capacity < 1:
                        raise ValueError
                except ValueError:
                    raise ParseError(
                        line_num,
                        "max_link_capacity must be a positive integer",
                    )
    return Connection(zone1, zone2, max_link_capacity)


def parse_map(filepath: str) -> Network:
    nb_drones: Optional[int] = None
    zones: list[Zone] = []
    conns: list[Connection] = []
    zone_names: set[str] = set()
    conn_keys: set[str] = set()
    has_start = False
    has_end = False

    with open(filepath, "r") as f:
        for line_num, raw_line in enumerate(f, 1):
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue

            if line.startswith("nb_drones:"):
                val = line.split(":", 1)[1].strip()
                try:
                    nb_drones = int(val)
                    if nb_drones < 1:
                        raise ValueError
                except ValueError:
                    raise ParseError(
                        line_num,
                        "nb_drones must be a positive integer",
                    )
            elif line.startswith("start_hub:"):
                rest = line.split(":", 1)[1].strip().split()
                zone = _parse_zone_line(
                    rest, line_num, is_start=True
                )
                if zone.name in zone_names:
                    raise ParseError(
                        line_num,
                        f"Duplicate zone name: '{zone.name}'",
                    )
                zone_names.add(zone.name)
                zones.append(zone)
                has_start = True
            elif line.startswith("end_hub:"):
                rest = line.split(":", 1)[1].strip().split()
                zone = _parse_zone_line(
                    rest, line_num, is_end=True
                )
                if zone.name in zone_names:
                    raise ParseError(
                        line_num,
                        f"Duplicate zone name: '{zone.name}'",
                    )
                zone_names.add(zone.name)
                zones.append(zone)
                has_end = True
            elif line.startswith("hub:"):
                rest = line.split(":", 1)[1].strip().split()
                zone = _parse_zone_line(rest, line_num)
                if zone.name in zone_names:
                    raise ParseError(
                        line_num,
                        f"Duplicate zone name: '{zone.name}'",
                    )
                zone_names.add(zone.name)
                zones.append(zone)
            elif line.startswith("connection:"):
                rest = line.split(":", 1)[1].strip().split()
                conn = _parse_connection_line(rest, line_num)
                if conn.zone1_name not in zone_names:
                    raise ParseError(
                        line_num,
                        f"Unknown zone: '{conn.zone1_name}'",
                    )
                if conn.zone2_name not in zone_names:
                    raise ParseError(
                        line_num,
                        f"Unknown zone: '{conn.zone2_name}'",
                    )
                if conn.key in conn_keys:
                    raise ParseError(
                        line_num,
                        f"Duplicate connection: {conn.key}",
                    )
                conn_keys.add(conn.key)
                conns.append(conn)
            else:
                raise ParseError(
                    line_num, f"Unknown directive: '{line}'"
                )

    if nb_drones is None:
        raise ParseError(0, "Missing nb_drones directive")
    if not has_start:
        raise ParseError(0, "Missing start_hub directive")
    if not has_end:
        raise ParseError(0, "Missing end_hub directive")

    network = Network(nb_drones)
    for zone in zones:
        network.add_zone(zone)
    for conn in conns:
        network.add_connection(conn)
    return network
