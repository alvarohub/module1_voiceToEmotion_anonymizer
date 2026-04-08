"""
Real-time radar / star chart for emotion dimensions.

Uses matplotlib polar plot with FuncAnimation.  Must run on the main
thread (macOS / Tk requirement).  Reads results from a queue fed by
the inference thread.

──────────────────────────────────────────────────────────────────────
CUSTOMISING DIMENSIONS
If you swap the model and change the dimension names, the radar chart
adapts automatically — it reads `dimensions` from the model at startup.
To change the *colours* per dimension, edit EMOTION_COLORS below.
──────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import queue
from typing import Optional
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


# ---- Per-dimension fill colours (extend as needed) -------------------------
EMOTION_COLORS: dict[str, str] = {
    "angry":     "#FF4444",
    "disgusted": "#88AA00",
    "fearful":   "#AA44FF",
    "happy":     "#FFD700",
    "neutral":   "#4488FF",
    "other":     "#888888",
    "sad":       "#5566CC",
    "surprised": "#FF8800",
    "unknown":   "#AAAAAA",
}
DEFAULT_COLOR = "#4488FF"


class RadarDisplay:
    """Animated radar / spider chart showing live emotion scores."""

    def __init__(
        self,
        dimensions: list[str],
        update_interval_ms: int = 100,
        smoothing: float = 0.35,
        trail_frames: int = 3,
    ):
        """
        Args:
            dimensions:         Ordered list of dimension names (from the model).
            update_interval_ms: Matplotlib timer interval.
            smoothing:          EMA alpha (0 = frozen, 1 = no smoothing).
            trail_frames:       Number of fading "ghost" polygons to draw.
        """
        self.dimensions = dimensions
        self.n = len(dimensions)
        self._alpha = smoothing
        self._trail_max = trail_frames

        # Angles for polar axes (closed polygon → +1 duplicate angle)
        self.angles = np.linspace(0, 2 * np.pi, self.n, endpoint=False).tolist()
        self.angles += self.angles[:1]

        # Smoothed scores (EMA state)
        self._smoothed = {d: 0.0 for d in dimensions}

        # Trail history (list of value-lists, newest first)
        self._trail: list[list[float]] = []

        # ---- Figure setup ----
        plt.style.use("dark_background")
        self.fig, self.ax = plt.subplots(
            figsize=(7, 7), subplot_kw={"polar": True}
        )
        self.fig.patch.set_facecolor("#1a1a2e")
        self.ax.set_facecolor("#1a1a2e")

        # Grid & tick styling
        self.ax.set_ylim(0, 1)
        self.ax.set_yticks([0.25, 0.5, 0.75, 1.0])
        self.ax.set_yticklabels(["", "0.5", "", "1.0"], color="#666", size=8)
        self.ax.set_xticks(self.angles[:-1])
        self.ax.set_xticklabels(
            [d.upper() for d in dimensions], size=10, color="#cccccc"
        )
        self.ax.spines["polar"].set_color("#333")
        self.ax.grid(color="#333", linewidth=0.5)

        # Initial (empty) polygon
        zeros = [0.0] * (self.n + 1)
        (self._line,) = self.ax.plot(
            self.angles, zeros, "o-", linewidth=2, markersize=5,
            color=DEFAULT_COLOR, zorder=10,
        )
        self._fill = self.ax.fill(
            self.angles, zeros, alpha=0.30, color=DEFAULT_COLOR, zorder=5,
        )

        # Trail artists (will be created on first update)
        self._trail_fills: list = []

        self._title = self.ax.set_title(
            "Waiting for audio …", size=16, color="white", pad=20,
        )

        self._queue: Optional[queue.Queue] = None
        self._latest: Optional[dict] = None
        self._anim: Optional[FuncAnimation] = None
        self._interval = update_interval_ms

    def set_queue(self, q: queue.Queue) -> None:
        self._queue = q

    # ---- animation callback --------------------------------------------------

    def _update(self, _frame):
        # Drain the queue, keeping only the most recent result
        if self._queue is not None:
            while True:
                try:
                    self._latest = self._queue.get_nowait()
                except queue.Empty:
                    break

        if self._latest is None:
            return (self._line,)

        raw_scores = self._latest["scores"]

        # Exponential moving average for visual smoothness
        for d in self.dimensions:
            new_val = raw_scores.get(d, 0.0)
            self._smoothed[d] = (
                self._alpha * new_val + (1 - self._alpha) * self._smoothed[d]
            )

        values = [self._smoothed[d] for d in self.dimensions]
        values_closed = values + values[:1]

        # Manage trail history
        self._trail.insert(0, values_closed)
        self._trail = self._trail[: self._trail_max]

        # Pick colour from the dominant emotion
        label = self._latest["label"]
        color = EMOTION_COLORS.get(label, DEFAULT_COLOR)

        # ---- Draw trail (older → more transparent) ----
        for artist in self._trail_fills:
            artist.remove()
        self._trail_fills.clear()

        for i, trail_vals in enumerate(reversed(self._trail)):
            opacity = 0.08 * (i + 1) / self._trail_max
            fill_artists = self.ax.fill(
                self.angles, trail_vals, alpha=opacity, color=color, zorder=2 + i,
            )
            self._trail_fills.extend(fill_artists)

        # ---- Draw current polygon ----
        self._line.set_ydata(values_closed)
        self._line.set_color(color)
        self._line.set_markerfacecolor(color)

        self._fill[0].remove()
        self._fill = self.ax.fill(
            self.angles, values_closed, alpha=0.30, color=color, zorder=5,
        )

        # ---- Title: dominant emotion + confidence ----
        conf = self._latest["confidence"]
        self._title.set_text(f"{label.upper()}  {conf:.0%}")
        self._title.set_color(color)

        return (self._line,)

    # ---- blocking entry point (call from main thread) ------------------------

    def run(self) -> None:
        self._anim = FuncAnimation(
            self.fig,
            self._update,
            interval=self._interval,
            blit=False,
            cache_frame_data=False,
        )
        plt.tight_layout()
        plt.show()
