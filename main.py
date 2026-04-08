#!/usr/bin/env python3
"""
Real-time Speech → Emotion track

    python main.py

Captures audio from the default microphone, runs emotion2vec inference
on overlapping windows, displays a live radar chart, and writes a
timestamped CSV track to the output/ folder.

Prerequisites (macOS):
    brew install portaudio
    pip install -r requirements.txt
"""

from __future__ import annotations

import os
import sys
import time
import queue
import threading
from datetime import datetime

# ============================================================
# CONFIGURATION — edit these to taste
# ============================================================
CONFIG = {
    # Audio
    "sample_rate": 16000,
    "chunk_duration": 2.0,   # seconds per analysis window
    "hop_duration": 1.0,     # seconds of *new* audio before next analysis

    # Model
    # ── MODEL SWAP POINT ─────────────────────────────────────
    # Change the import below AND this model name to switch
    # backbones.  See emotion_model.py for the full guide.
    "model_name": "iic/emotion2vec_plus_large",   # or "iic/emotion2vec_plus_base"
    "device": "cpu",                                # "cpu" | "cuda" | "mps"

    # Output
    "output_dir": "output",

    # Display
    "radar_update_ms": 100,
    "radar_smoothing": 0.35,   # 0 = frozen, 1 = raw (no smoothing)
    "radar_trail": 3,          # ghosted previous frames (0 to disable)
}


# ── MODEL SWAP POINT ─────────────────────────────────────────
# To use a different model, change this import.
# e.g.:  from emotion_model import HuBERTEmotionModel as EmotionModel
from emotion_model import Emotion2VecModel as EmotionModel

from audio_capture import AudioCapture
from track_writer import TrackWriter
from radar_display import RadarDisplay


# ============================================================
# Inference thread
# ============================================================

def inference_loop(
    audio_capture: AudioCapture,
    model,
    result_queue: queue.Queue,
    track_writer: TrackWriter,
    stop_event: threading.Event,
) -> None:
    """Background thread: pull audio → run model → push results."""
    while not stop_event.is_set():
        chunk = audio_capture.get_chunk()
        if chunk is None:
            time.sleep(0.05)
            continue

        timestamp_ms = time.time() * 1000.0

        try:
            result = model.predict(chunk, sr=CONFIG["sample_rate"])
        except Exception as exc:
            print(f"[inference] error: {exc}", file=sys.stderr)
            continue

        result["timestamp_ms"] = timestamp_ms

        # Fan out to display + CSV writer
        result_queue.put(result)
        track_writer.write(result, timestamp_ms)

        # Console one-liner
        dims = " ".join(
            f"{d[:3]}={result['scores'].get(d, 0):.2f}"
            for d in model.dimensions
        )
        print(f"[{result['label']:>10s}] {result['confidence']:.0%}  {dims}")


# ============================================================
# Main
# ============================================================

def main() -> None:
    os.makedirs(CONFIG["output_dir"], exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = os.path.join(CONFIG["output_dir"], f"emotion_track_{ts}.csv")

    # ---- Load model ---------------------------------------------------------
    print("Loading model …")
    model = EmotionModel(
        model_name=CONFIG["model_name"],
        device=CONFIG["device"],
    )
    print(f"Model ready — dimensions: {model.dimensions}")

    # ---- Set up components --------------------------------------------------
    audio = AudioCapture(
        sample_rate=CONFIG["sample_rate"],
        chunk_duration=CONFIG["chunk_duration"],
        hop_duration=CONFIG["hop_duration"],
    )

    writer = TrackWriter(csv_path, model.dimensions)
    result_q: queue.Queue = queue.Queue()
    stop = threading.Event()

    display = RadarDisplay(
        dimensions=model.dimensions,
        update_interval_ms=CONFIG["radar_update_ms"],
        smoothing=CONFIG["radar_smoothing"],
        trail_frames=CONFIG["radar_trail"],
    )
    display.set_queue(result_q)

    # ---- Start capture & inference ------------------------------------------
    audio.start()
    print(f"🎙  Listening … (saving to {csv_path})")

    inf_thread = threading.Thread(
        target=inference_loop,
        args=(audio, model, result_q, writer, stop),
        daemon=True,
    )
    inf_thread.start()

    # ---- Run display (blocks until window is closed) ------------------------
    try:
        display.run()
    except KeyboardInterrupt:
        pass
    finally:
        print("\nShutting down …")
        stop.set()
        audio.stop()
        writer.close()
        print(f"Track saved → {csv_path}")


if __name__ == "__main__":
    main()
