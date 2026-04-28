from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union


class DataStream(ABC):
    """Abstract base class for data streams."""

    def __init__(self, stream_id: str) -> None:
        self.stream_id = stream_id
        self.processed_count: int = 0

    @abstractmethod
    def process_batch(
        self, data_batch: List[Any]
    ) -> str:
        """Process a batch of data."""
        pass

    def filter_data(
        self,
        data_batch: List[Any],
        criteria: Optional[str] = None,
    ) -> List[Any]:
        """Filter data based on criteria."""
        if criteria is None:
            return data_batch
        return [
            d for d in data_batch
            if criteria.lower() in str(d).lower()
        ]

    def get_stats(
        self,
    ) -> Dict[str, Union[str, int, float]]:
        """Return stream statistics."""
        return {
            "stream_id": self.stream_id,
            "processed": self.processed_count,
        }


class SensorStream(DataStream):
    """Stream for environmental sensor data."""

    def process_batch(
        self, data_batch: List[Any]
    ) -> str:
        self.processed_count += len(data_batch)
        temps = []
        for item in data_batch:
            try:
                parts = str(item).split(":")
                if parts[0] == "temp":
                    temps.append(float(parts[1]))
            except (IndexError, ValueError):
                continue
        count = len(data_batch)
        if temps:
            avg = sum(temps) / len(temps)
            return (
                f"{count} readings processed,"
                f" avg temp: {avg}\u00b0C"
            )
        return f"{count} readings processed"

    def filter_data(
        self,
        data_batch: List[Any],
        criteria: Optional[str] = None,
    ) -> List[Any]:
        if criteria == "critical":
            return [
                d for d in data_batch
                if "critical" in str(d).lower()
                or float(str(d).split(":")[1]) > 30
            ]
        return super().filter_data(data_batch, criteria)

    def get_stats(
        self,
    ) -> Dict[str, Union[str, int, float]]:
        stats = super().get_stats()
        stats["type"] = "Environmental Data"
        return stats


class TransactionStream(DataStream):
    """Stream for financial transaction data."""

    def process_batch(
        self, data_batch: List[Any]
    ) -> str:
        self.processed_count += len(data_batch)
        net = 0
        for item in data_batch:
            parts = str(item).split(":")
            if len(parts) == 2:
                action = parts[0]
                val = int(parts[1])
                if action == "buy":
                    net += val
                elif action == "sell":
                    net -= val
        sign = "+" if net >= 0 else ""
        return (
            f"{len(data_batch)} operations,"
            f" net flow: {sign}{net} units"
        )

    def filter_data(
        self,
        data_batch: List[Any],
        criteria: Optional[str] = None,
    ) -> List[Any]:
        if criteria == "large":
            return [
                d for d in data_batch
                if abs(int(str(d).split(":")[1])) >= 100
            ]
        return super().filter_data(data_batch, criteria)

    def get_stats(
        self,
    ) -> Dict[str, Union[str, int, float]]:
        stats = super().get_stats()
        stats["type"] = "Financial Data"
        return stats


class EventStream(DataStream):
    """Stream for system event data."""

    def process_batch(
        self, data_batch: List[Any]
    ) -> str:
        self.processed_count += len(data_batch)
        errors = sum(
            1 for e in data_batch
            if "error" in str(e).lower()
        )
        result = f"{len(data_batch)} events"
        if errors:
            result += f", {errors} error detected"
        return result

    def get_stats(
        self,
    ) -> Dict[str, Union[str, int, float]]:
        stats = super().get_stats()
        stats["type"] = "System Events"
        return stats


class StreamProcessor:
    """Handles multiple stream types polymorphically."""

    def __init__(self) -> None:
        self.streams: List[DataStream] = []

    def add_stream(self, stream: DataStream) -> None:
        self.streams.append(stream)

    def process_all(
        self, batches: List[List[Any]]
    ) -> List[str]:
        results: List[str] = []
        for stream, batch in zip(
            self.streams, batches
        ):
            try:
                r = stream.process_batch(batch)
                results.append(r)
            except Exception as e:
                results.append(f"Error: {e}")
        return results


def main() -> None:
    print("=== CODE NEXUS - POLYMORPHIC STREAM SYSTEM ===")

    print("Initializing Sensor Stream...")
    sensor = SensorStream("SENSOR_001")
    stats = sensor.get_stats()
    print(
        f"Stream ID: {stats['stream_id']},"
        f" Type: {stats['type']}"
    )
    s_batch: List[Any] = [
        "temp:22.5", "humidity:65", "pressure:1013"
    ]
    print(f"Processing sensor batch: {s_batch}")
    r = sensor.process_batch(s_batch)
    print(f"Sensor analysis: {r}")

    print()
    print("Initializing Transaction Stream...")
    trans = TransactionStream("TRANS_001")
    stats = trans.get_stats()
    print(
        f"Stream ID: {stats['stream_id']},"
        f" Type: {stats['type']}"
    )
    t_batch: List[Any] = [
        "buy:100", "sell:150", "buy:75"
    ]
    print(f"Processing transaction batch: {t_batch}")
    r = trans.process_batch(t_batch)
    print(f"Transaction analysis: {r}")

    print()
    print("Initializing Event Stream...")
    event = EventStream("EVENT_001")
    stats = event.get_stats()
    print(
        f"Stream ID: {stats['stream_id']},"
        f" Type: {stats['type']}"
    )
    e_batch: List[Any] = ["login", "error", "logout"]
    print(f"Processing event batch: {e_batch}")
    r = event.process_batch(e_batch)
    print(f"Event analysis: {r}")

    print()
    print("=== Polymorphic Stream Processing ===")
    print(
        "Processing mixed stream types"
        " through unified interface..."
    )
    processor = StreamProcessor()
    s2 = SensorStream("SENSOR_002")
    t2 = TransactionStream("TRANS_002")
    e2 = EventStream("EVENT_002")
    processor.add_stream(s2)
    processor.add_stream(t2)
    processor.add_stream(e2)

    batches: List[List[Any]] = [
        ["temp:25.0", "temp:30.1"],
        ["buy:200", "sell:50", "buy:30", "sell:120"],
        ["login", "error", "logout"],
    ]
    results = processor.process_all(batches)
    print("Batch 1 Results:")
    print(f"- Sensor data: {results[0]}")
    print(f"- Transaction data: {results[1]}")
    print(f"- Event data: {results[2]}")

    print()
    print(
        "Stream filtering active:"
        " High-priority data only"
    )
    crit_sensors = sensor.filter_data(
        ["temp:35", "temp:20", "critical:alert"],
        "critical"
    )
    large_trans = trans.filter_data(
        ["buy:200", "sell:50", "buy:150"],
        "large"
    )
    print(
        f"Filtered results: {len(crit_sensors)}"
        " critical sensor alerts,"
        f" {len(large_trans)} large transaction"
    )

    print()
    print(
        "All streams processed successfully."
        " Nexus throughput optimal."
    )


if __name__ == "__main__":
    main()
