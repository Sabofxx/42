class Connection:
    def __init__(
        self,
        zone1_name: str,
        zone2_name: str,
        max_link_capacity: int = 1,
    ) -> None:
        self.zone1_name = zone1_name
        self.zone2_name = zone2_name
        self.max_link_capacity = max_link_capacity

    @property
    def key(self) -> str:
        names = sorted([self.zone1_name, self.zone2_name])
        return f"{names[0]}-{names[1]}"

    def other(self, zone_name: str) -> str:
        if zone_name == self.zone1_name:
            return self.zone2_name
        return self.zone1_name

    def __repr__(self) -> str:
        return f"Connection({self.zone1_name}-{self.zone2_name})"
