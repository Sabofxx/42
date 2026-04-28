from abc import ABC, abstractmethod
from typing import Any, List


class DataProcessor(ABC):
    """Abstract base class for data processing."""

    @abstractmethod
    def process(self, data: Any) -> str:
        """Process data and return result string."""
        pass

    @abstractmethod
    def validate(self, data: Any) -> bool:
        """Validate if data is appropriate."""
        pass

    def format_output(self, result: str) -> str:
        """Format the output string."""
        return f"Output: {result}"


class NumericProcessor(DataProcessor):
    """Processor for numeric data."""

    def process(self, data: Any) -> str:
        if not self.validate(data):
            raise ValueError("Invalid numeric data")
        total = sum(data)
        avg = total / len(data)
        return (
            f"Processed {len(data)} numeric values,"
            f" sum={total}, avg={avg}"
        )

    def validate(self, data: Any) -> bool:
        if not isinstance(data, list):
            return False
        return all(
            isinstance(x, (int, float)) for x in data
        )

    def format_output(self, result: str) -> str:
        return f"Output: {result}"


class TextProcessor(DataProcessor):
    """Processor for text data."""

    def process(self, data: Any) -> str:
        if not self.validate(data):
            raise ValueError("Invalid text data")
        chars = len(data)
        words = len(data.split())
        return (
            f"Processed text: {chars} characters,"
            f" {words} words"
        )

    def validate(self, data: Any) -> bool:
        return isinstance(data, str)

    def format_output(self, result: str) -> str:
        return f"Output: {result}"


class LogProcessor(DataProcessor):
    """Processor for log entries."""

    def process(self, data: Any) -> str:
        if not self.validate(data):
            raise ValueError("Invalid log data")
        parts = data.split(": ", 1)
        level = parts[0]
        message = parts[1] if len(parts) > 1 else ""
        return (
            f"[ALERT] {level} level detected:"
            f" {message}"
        )

    def validate(self, data: Any) -> bool:
        return isinstance(data, str) and ": " in data

    def format_output(self, result: str) -> str:
        return f"Output: {result}"


def main() -> None:
    print("=== CODE NEXUS - DATA PROCESSOR FOUNDATION ===")

    numeric = NumericProcessor()
    print("Initializing Numeric Processor...")
    data_n: List[int] = [1, 2, 3, 4, 5]
    print(f"Processing data: {data_n}")
    print("Validation: Numeric data verified")
    result = numeric.process(data_n)
    print(numeric.format_output(result))

    print()
    text = TextProcessor()
    print("Initializing Text Processor...")
    data_t = "Hello Nexus World"
    print(f'Processing data: "{data_t}"')
    print("Validation: Text data verified")
    result = text.process(data_t)
    print(text.format_output(result))

    print()
    log = LogProcessor()
    print("Initializing Log Processor...")
    data_l = "ERROR: Connection timeout"
    print(f'Processing data: "{data_l}"')
    print("Validation: Log entry verified")
    result = log.process(data_l)
    print(log.format_output(result))

    print()
    print("=== Polymorphic Processing Demo ===")
    print(
        "Processing multiple data types"
        " through same interface..."
    )
    processors: List[DataProcessor] = [
        NumericProcessor(),
        TextProcessor(),
        LogProcessor(),
    ]
    test_data: List[Any] = [
        [1, 2, 3],
        "Nexus Online",
        "INFO: System ready",
    ]
    for i, (proc, data) in enumerate(
        zip(processors, test_data), 1
    ):
        try:
            r = proc.process(data)
            print(f"Result {i}: {r}")
        except ValueError as e:
            print(f"Result {i}: Error - {e}")

    print()
    print(
        "Foundation systems online."
        " Nexus ready for advanced streams."
    )


if __name__ == "__main__":
    main()
