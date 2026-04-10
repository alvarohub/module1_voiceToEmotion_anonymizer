#!/usr/bin/env python3
"""
Definitive F0 chunk-size diagnostic.

Records 3s of speech, then compares openSMILE F0 detection:
  1. Full 3s at once
  2. Chopped into 0.5s chunks processed independently
  3. 0.5s chunks WITH 3s context (read 3s, only report last 0.5s)
  4. Through AudioCapture ring buffer

Run:  python test/diag_f0_chunk.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sounddevice as sd
import numpy as np
import opensmile
import wave

SR = 16000
DUR = 3.0

# Show device info
info = sd.query_devices(sd.default.device[0])
print(f"Device: {info['name']}")
print(f"Recording {DUR}s at {SR}Hz — SPEAK CONTINUOUSLY NOW ...")
audio = sd.rec(int(SR * DUR), samplerate=SR, channels=1, dtype="float32")
sd.wait()
audio = audio.squeeze()
peak = np.max(np.abs(audio))
rms = np.sqrt(np.mean(audio ** 2))
print(f"Captured {len(audio)} samples, peak={peak:.5f}, rms={rms:.5f}")
if peak < 0.01:
    print("⚠️  Very low level — mic not active?")

# Save full recording for reference
os.makedirs("output", exist_ok=True)
data16 = (audio * 32767).clip(-32768, 32767).astype(np.int16)
with wave.open("output/diag_full_3s.wav", "w") as wf:
    wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR)
    wf.writeframes(data16.tobytes())
print("Saved output/diag_full_3s.wav\n")

smile = opensmile.Smile(
    feature_set=opensmile.FeatureSet.eGeMAPSv02,
    feature_level=opensmile.FeatureLevel.LowLevelDescriptors,
)

def report(label, f0_vals):
    nz = f0_vals[f0_vals > 0]
    pct = 100 * len(nz) / max(len(f0_vals), 1)
    if len(nz):
        med_st = np.median(nz)
        med_hz = 27.5 * 2 ** (med_st / 12)
        print(f"  {label}: {len(nz)}/{len(f0_vals)} voiced ({pct:.0f}%), "
              f"median={med_st:.1f}st = {med_hz:.0f}Hz")
    else:
        print(f"  {label}: 0/{len(f0_vals)} voiced (0%)")

# ── Test 1: Full 3s ──────────────────────────────────────────
print("═══ TEST 1: Full 3s at once ═══")
df = smile.process_signal(audio, sampling_rate=SR)
f0 = df["F0semitoneFrom27.5Hz_sma3nz"].values
report("FULL", f0)

# ── Test 2: 0.5s chunks independently ────────────────────────
print("\n═══ TEST 2: Independent 0.5s chunks ═══")
chunk_samples = int(0.5 * SR)
total_v, total_f = 0, 0
for i in range(0, len(audio) - chunk_samples + 1, chunk_samples):
    chunk = audio[i : i + chunk_samples]
    df_c = smile.process_signal(chunk, sampling_rate=SR)
    f0_c = df_c["F0semitoneFrom27.5Hz_sma3nz"].values
    nz = f0_c[f0_c > 0]
    total_v += len(nz)
    total_f += len(f0_c)
    pk = np.max(np.abs(chunk))
    report(f"  chunk{i // chunk_samples} (peak={pk:.4f})", f0_c)
print(f"  TOTAL: {total_v}/{total_f} voiced ({100*total_v/max(total_f,1):.0f}%)")

# ── Test 3: 0.5s with 3s context (sliding window) ────────────
print("\n═══ TEST 3: 0.5s display window BUT 3s context ═══")
# Process full 3s, then slice to the last 0.5s of frames
ctx_frames = len(f0)  # total frames for 3s
win_frames = int(0.5 / 0.01)  # ~50 frames for 0.5s at 10ms hop
for end_sec_10 in range(5, int(DUR * 10) + 1, 5):
    end_sec = end_sec_10 / 10.0
    start_sec = max(0.0, end_sec - 3.0)
    ctx = audio[int(start_sec * SR) : int(end_sec * SR)]
    df_ctx = smile.process_signal(ctx, sampling_rate=SR)
    f0_ctx = df_ctx["F0semitoneFrom27.5Hz_sma3nz"].values
    # Only look at the LAST 0.5s of frames
    tail = f0_ctx[-win_frames:] if len(f0_ctx) > win_frames else f0_ctx
    report(f"  t={end_sec:.1f}s (ctx={len(ctx)/SR:.1f}s, show last {len(tail)} frames)", tail)

# ── Test 4: Through AudioCapture ring buffer ──────────────────
print("\n═══ TEST 4: Through AudioCapture ring buffer ═══")
from audio_capture import AudioCapture
import time

ac = AudioCapture(sample_rate=SR, chunk_duration=2.0, hop_duration=2.0)
ac.start()
print(f"Ring buffer recording {DUR}s — SPEAK AGAIN ...")
time.sleep(DUR)

# Read 0.5s from ring buffer
rb_05 = ac.get_latest_audio(0.5)
# Read full 3s from ring buffer
rb_30 = ac.get_latest_audio(3.0)
ac.stop()

if rb_05 is not None:
    pk05 = np.max(np.abs(rb_05))
    df_rb05 = smile.process_signal(rb_05, sampling_rate=SR)
    f0_rb05 = df_rb05["F0semitoneFrom27.5Hz_sma3nz"].values
    report(f"  ringbuf 0.5s (peak={pk05:.4f})", f0_rb05)
else:
    print("  ringbuf 0.5s: None returned")

if rb_30 is not None:
    pk30 = np.max(np.abs(rb_30))
    df_rb30 = smile.process_signal(rb_30, sampling_rate=SR)
    f0_rb30 = df_rb30["F0semitoneFrom27.5Hz_sma3nz"].values
    report(f"  ringbuf 3.0s (peak={pk30:.4f})", f0_rb30)
    # Also chunk the ring buffer 3s into 0.5s pieces
    for i in range(0, len(rb_30) - chunk_samples + 1, chunk_samples):
        chunk = rb_30[i : i + chunk_samples]
        df_rbc = smile.process_signal(chunk, sampling_rate=SR)
        f0_rbc = df_rbc["F0semitoneFrom27.5Hz_sma3nz"].values
        nz = f0_rbc[f0_rbc > 0]
        pk = np.max(np.abs(chunk))
        report(f"    rb chunk{i//chunk_samples} (peak={pk:.4f})", f0_rbc)
else:
    print("  ringbuf 3.0s: None returned")

print("\nDone. Check output/diag_full_3s.wav to verify audio quality.")
