"""Helper script to run the Behave examples with the modern formatter."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    """Run behave from the examples directory using the modern formatter."""
    examples_dir = Path(__file__).parent.resolve()

    cmd = [sys.executable, "-m", "behave"]
    if len(sys.argv) > 1:
        cmd.extend(sys.argv[1:])

    print(f"Running: {' '.join(cmd)} in {examples_dir}")
    result = subprocess.run(cmd, cwd=examples_dir, check=False)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
