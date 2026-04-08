"""
Microphone capture with sliding-window chunking.

Runs a sounddevice.InputStream in a callback; accumulates audio in a
thread-safe ring buffer.  Call get_chunk() from any thread to retrieve
the latest analysis window once enough *new* samples have arrived.
"""

import threading
from typing import Optional
import numpy as np
import sounddevice as sd


class AudioCapture:
    def __init__(
        self,
        sample_rate: int = 16000,
        channels: int = 1,
        chunk_duration: float = 2.0,
        hop_duration: float = 1.0,
    ):
        """
        Args:
            sample_rate:    Must match the model's expected rate (16 kHz for emotion2vec).
            channels:       1 = mono (required by most speech models).
            chunk_duration: Length of each analysis window in seconds.
            hop_duration:   How many *new* seconds of audio trigger a new chunk.
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_samples = int(chunk_duration * sample_rate)
        self.hop_samples = int(hop_duration * sample_rate)

        # Ring buffer — 4× chunk size gives comfortable headroom
        buf_size = self.chunk_samples * 4
        self._buffer = np.zeros(buf_size, dtype=np.float32)
        self._write_pos = 0
        self._unread_samples = 0
        self._lock = threading.Lock()

        self._stream: Optional[sd.InputStream] = None

    # ---- sounddevice callback (runs in audio thread) ----

    def _callback(self, indata, frames, time_info, status):
        if status:
            print(f"[audio] {status}")
        audio = indata[:, 0]  # mono
        n = len(audio)
        with self._lock:
            end = self._write_pos + n
            if end <= len(self._buffer):
                self._buffer[self._write_pos : end] = audio
            else:
                first = len(self._buffer) - self._write_pos
                self._buffer[self._write_pos :] = audio[:first]
                self._buffer[: n - first] = audio[first:]
            self._write_pos = end % len(self._buffer)
            self._unread_samples += n

    # ---- public API ----

    def start(self):
        self._stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype="float32",
            callback=self._callback,
        )
        self._stream.start()

    def stop(self):
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()

    def get_chunk(self) -> Optional[np.ndarray]:
        """Return the latest chunk_samples of audio, or None if not enough new data."""
        with self._lock:
            if self._unread_samples < self.hop_samples:
                return None

            read_end = self._write_pos
            read_start = (read_end - self.chunk_samples) % len(self._buffer)

            if read_start < read_end:
                chunk = self._buffer[read_start:read_end].copy()
            else:
                chunk = np.concatenate(
                    [self._buffer[read_start:], self._buffer[:read_end]]
                )

            self._unread_samples = 0
            return chunk
