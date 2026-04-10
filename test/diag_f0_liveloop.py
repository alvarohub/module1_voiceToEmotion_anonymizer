#!/usr/bin/env python3
"""
Minimal live-loop reproduction test.

Replicates exact behavior of prosody_lld_loop without matplotlib.
If F0 works here → matplotlib is the culprit.
If F0 fails here → something in the loop/extraction is wrong.

Run:  python test/diag_f0_liveloop.py
"""
import sys, os, time, threading
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from audio_capture import AudioCapture
from prosody import extract_prosody_lld

SR = 16000
INTERVAL = 0.5
DURATION = 6.0  # total seconds to run

print(f"Starting AudioCapture at {SR}Hz ...")
ac = AudioCapture(sample_rate=SR, chunk_duration=2.0, hop_duration=2.0)
ac.start()
time.sleep(0.3)  # let buffer fill a bit

print(f"\n{'='*60}")
print(f"Live loop: reading {INTERVAL}s every {INTERVAL}s for {DURATION}s")
print(f"SPEAK CONTINUOUSLY NOW!")
print(f"{'='*60}\n")

os.makedirs("output", exist_ok=True)
saved = False
n_calls = int(DURATION / INTERVAL)

for i in range(n_calls):
    time.sleep(INTERVAL)
    audio = ac.get_latest_audio(INTERVAL)
    if audio is None:
        print(f"  [{i:2d}] None returned")
        continue

    peak = float(np.max(np.abs(audio)))
    rms = float(np.sqrt(np.mean(audio ** 2)))

    # Save first chunk with speech for offline comparison
    if not saved and peak > 0.02:
        import wave
        path = "output/diag_liveloop_chunk.wav"
        data16 = (audio * 32767).clip(-32768, 32767).astype(np.int16)
        with wave.open(path, "w") as wf:
            wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR)
            wf.writeframes(data16.tobytes())
        print(f"  [SAVED {path}]")
        saved = True

    # Use EXACT same extraction as live app
    lld = extract_prosody_lld(audio, sr=SR)
    if lld is None:
        print(f"  [{i:2d}] extract_prosody_lld returned None")
        continue

    f0 = lld["frames"].get("F0semitoneFrom27.5Hz_sma3nz", np.array([]))
    nz = f0[f0 > 0]
    total = len(f0)
    if len(nz) > 0:
        med_st = np.median(nz)
        med_hz = 27.5 * 2 ** (med_st / 12)
        print(f"  [{i:2d}] peak={peak:.4f} rms={rms:.5f} → "
              f"F0: {len(nz)}/{total} voiced ({100*len(nz)/total:.0f}%), "
              f"median={med_st:.1f}st = {med_hz:.0f}Hz")
    else:
        print(f"  [{i:2d}] peak={peak:.4f} rms={rms:.5f} → F0: 0/{total} voiced")

ac.stop()
print(f"\n{'='*60}")
print("Done. If F0 worked here but not in main.py, matplotlib is involved.")
print("Compare output/diag_liveloop_chunk.wav with output/diag_full_3s.wav")
