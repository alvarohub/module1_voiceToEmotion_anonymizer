#!/usr/bin/env python3
"""Quick F0 diagnostic — records 3s from mic, runs openSMILE LLD, reports stats."""
import sounddevice as sd
import numpy as np
import opensmile

devs = sd.query_devices()
default_in = sd.default.device[0]
info = sd.query_devices(default_in)
print(f"Device: {info['name']}, ch={info['max_input_channels']}, native_sr={info['default_samplerate']}")

sr = 16000
dur = 3.0
print(f"Recording {dur}s at {sr} Hz — SPEAK or HUM NOW ...")
audio = sd.rec(int(sr * dur), samplerate=sr, channels=1, dtype="float32")
sd.wait()
audio = audio.squeeze()

rms = np.sqrt(np.mean(audio**2))
peak = np.max(np.abs(audio))
print(f"Captured {len(audio)} samples, RMS={rms:.5f}, peak={peak:.5f}")
if peak < 0.005:
    print("WARNING: Very low level — mic may not be active")

# Run LLD
smile = opensmile.Smile(
    feature_set=opensmile.FeatureSet.eGeMAPSv02,
    feature_level=opensmile.FeatureLevel.LowLevelDescriptors,
)
df = smile.process_signal(audio, sampling_rate=sr)
f0 = df["F0semitoneFrom27.5Hz_sma3nz"].values
loud = df["Loudness_sma3"].values

nz = f0[f0 > 0]
print(f"\nF0: {len(df)} frames total, {len(nz)} voiced ({100*len(nz)/max(len(df),1):.0f}%)")
if len(nz) > 0:
    hz = 27.5 * 2**(nz / 12)
    print(f"  semitone range: {nz.min():.1f} – {nz.max():.1f} st")
    print(f"  Hz range:       {hz.min():.0f} – {hz.max():.0f} Hz")
    print(f"  median:         {np.median(nz):.1f} st = {27.5 * 2**(np.median(nz)/12):.0f} Hz")
else:
    print("  NO F0 detected at all!")
print(f"\nLoudness: mean={loud.mean():.4f}, max={loud.max():.4f}")
print(f"\nFirst 30 F0 values: {f0[:30]}")
print(f"First 30 Loud values: {loud[:30]}")
