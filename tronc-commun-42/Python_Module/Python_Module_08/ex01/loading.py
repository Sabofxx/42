import sys
import importlib


DEPS = {
    "pandas": "Data manipulation",
    "requests": "Network access",
    "matplotlib": "Visualization",
    "numpy": "Numerical computation",
}


def check_dependency(
    name: str,
) -> tuple[bool, str]:
    try:
        mod = importlib.import_module(name)
        version = getattr(mod, "__version__", "?")
        return True, version
    except ImportError:
        return False, ""


def show_versions() -> dict[str, str]:
    installed: dict[str, str] = {}
    print("Checking dependencies:")
    all_ok = True
    for pkg, desc in DEPS.items():
        ok, ver = check_dependency(pkg)
        if ok:
            print(f"  [OK] {pkg} ({ver}) - {desc} ready")
            installed[pkg] = ver
        else:
            print(f"  [MISSING] {pkg} - {desc}")
            all_ok = False
    if not all_ok:
        print()
        print("Some dependencies are missing.")
        print("Install with pip:")
        print(
            "  pip install -r requirements.txt"
        )
        print("Or with Poetry:")
        print("  poetry install")
    return installed


def run_analysis() -> None:
    import pandas as pd  # noqa: E402
    import numpy as np  # noqa: E402
    import matplotlib  # noqa: E402
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt  # noqa: E402

    print()
    print("Analyzing Matrix data...")

    n = 1000
    print(f"Processing {n} data points...")
    np.random.seed(42)
    data = pd.DataFrame({
        "signal": np.random.randn(n),
        "noise": np.random.uniform(0, 1, n),
        "anomaly": np.random.choice(
            [0, 1], n, p=[0.95, 0.05]
        ),
    })

    data["strength"] = (
        data["signal"].abs() - data["noise"]
    )

    print("Generating visualization...")
    fig, ax = plt.subplots(1, 1, figsize=(8, 5))
    ax.hist(
        data["strength"], bins=30,
        color="green", alpha=0.7,
        label="Signal Strength"
    )
    ax.set_title("Matrix Signal Analysis")
    ax.set_xlabel("Strength")
    ax.set_ylabel("Frequency")
    ax.legend()
    plt.tight_layout()
    plt.savefig("matrix_analysis.png")
    plt.close()

    print()
    print("Analysis complete!")
    print("Results saved to: matrix_analysis.png")


def main() -> None:
    print("LOADING STATUS: Loading programs...")
    print()
    installed = show_versions()

    required = {"pandas", "numpy", "matplotlib"}
    if not required.issubset(installed.keys()):
        print()
        print(
            "Cannot proceed without"
            " core dependencies."
        )
        sys.exit(1)

    run_analysis()


if __name__ == "__main__":
    main()
