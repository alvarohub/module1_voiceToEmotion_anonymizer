"""
Append-only CSV writer for the emotion track.

Each row contains a wall-clock timestamp, elapsed time since the first
write, the top emotion label, its confidence, and the per-dimension
score vector.
"""

from __future__ import annotations

import csv
import os
from typing import Optional


class TrackWriter:
    def __init__(self, output_path: str, dimensions: list[str]):
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        self._file = open(output_path, "w", newline="")
        self._writer = csv.writer(self._file)
        self._dimensions = dimensions
        self._start_ms: Optional[float] = None

        # Header
        self._writer.writerow(
            ["timestamp_ms", "elapsed_ms", "label", "confidence"] + dimensions
        )
        self._file.flush()

    def write(self, result: dict, timestamp_ms: float) -> None:
        if self._start_ms is None:
            self._start_ms = timestamp_ms

        elapsed = timestamp_ms - self._start_ms
        row = [
            int(timestamp_ms),
            int(elapsed),
            result["label"],
            f"{result['confidence']:.4f}",
        ] + [f"{result['scores'].get(d, 0.0):.4f}" for d in self._dimensions]

        self._writer.writerow(row)
        self._file.flush()

    def close(self) -> None:
        self._file.close()
