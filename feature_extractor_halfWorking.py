import warnings
warnings.filterwarnings("ignore", category=UserWarning)

import numpy as np
import soundfile as sf
import librosa
import madmom
from scipy.signal import find_peaks
from luau_writer import to_lua_table

def extract_features_to_luau(audio_path, output_path):
	# Configuration
	RNN_FPS = 100
	ENERGY_THRESH_PERCENTILE = 30
	PEAK_CONFIDENCE = 0.025  # Lowered to catch more beats

	# Load audio
	y, sr = librosa.load(audio_path, sr=44100, mono=True)
	duration = librosa.get_duration(y=y, sr=sr)

	# Compute energy (for silence gating)
	frame_length, hop_length = 1024, 512
	energy = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]
	energy_times = librosa.frames_to_time(np.arange(len(energy)), sr=sr, hop_length=hop_length)
	energy_thresh = np.percentile(10 * np.log10(energy + 1e-10), ENERGY_THRESH_PERCENTILE)

	# RNN beat activations
	rnn_act = madmom.features.beats.RNNBeatProcessor()(audio_path)
	rnn_times = np.arange(len(rnn_act)) / RNN_FPS

	# Initial peak picking with more relaxed spacing
	min_peak_distance = int(RNN_FPS * 0.015)  # ~60 ms spacing
	peaks, _ = find_peaks(rnn_act, height=PEAK_CONFIDENCE, distance=min_peak_distance)
	beats = rnn_times[peaks]
	confidences = rnn_act[peaks]

	if len(beats) == 0:
		print("⚠️ No beats found!")
		return

	# Estimate median beat interval
	intervals = np.diff(beats)
	median_interval = np.median(intervals) if len(intervals) else 0.5  # fallback

	# Fill missing beats based on expected interval
	full_beats = [beats[0]]
	for i in range(1, len(beats)):
		t0, t1 = beats[i - 1], beats[i]
		gap = t1 - t0
		num_subdivs = int(round(gap / median_interval)) - 1
		for j in range(1, num_subdivs + 1):
			interp = t0 + j * median_interval
			if interp < t1:
				full_beats.append(interp)
		full_beats.append(t1)

	full_beats.sort()

	# Filter by silence and confidence
	valid_beats, valid_confs = [], []
	for b in full_beats:
		idx_e = np.searchsorted(energy_times, b)
		idx_rnn = int(b * RNN_FPS)
		if idx_e < len(energy) and idx_rnn < len(rnn_act):
			db_energy = 10 * np.log10(energy[idx_e] + 1e-10)
			if db_energy > energy_thresh and rnn_act[idx_rnn] >= PEAK_CONFIDENCE:
				valid_beats.append(float(b))
				valid_confs.append(float(rnn_act[idx_rnn]))

	# Estimate pitch at each beat
	f0 = librosa.yin(y, fmin=librosa.note_to_hz('C2'),
					 fmax=librosa.note_to_hz('C7'), sr=sr)
	f0_times = librosa.times_like(f0, sr=sr)

	def hz_to_note_safe(hz):
		return librosa.hz_to_note(hz, octave=True) if hz > 0 and not np.isnan(hz) else 'N/A'

	notes = []
	for b in valid_beats:
		idx = np.searchsorted(f0_times, b)
		pitch = f0[idx] if 0 <= idx < len(f0) else 0
		notes.append(hz_to_note_safe(pitch))

	# Output dictionary
	features_dict = {
		"beats": valid_beats,
		"confidence": float(np.mean(valid_confs)) if valid_confs else 0.0,
		"duration": float(duration),
		"notes": notes
	}

	with open(output_path, 'w') as f:
		f.write('return ')
		f.write(to_lua_table(features_dict))
		f.write('\n')

	import matplotlib.pyplot as plt

	# Plot RNN beat activations with detected beats
	plt.figure(figsize=(12, 4))
	plt.plot(rnn_times, rnn_act, label='RNN Activation', alpha=0.7)
	plt.vlines(valid_beats, 0, 1, color='green', linestyle='--', label='Valid Beats')
	plt.vlines(beats, 0, 1, color='red', linestyle=':', alpha=0.4, label='Initial Peaks')
	plt.title("Beat Detection Debug Plot")
	plt.xlabel("Time (s)")
	plt.ylabel("Activation")
	plt.ylim(0, 1)
	plt.legend(loc='upper right')
	plt.tight_layout()

	# Save to file
	debug_plot_path = output_path.replace('.luau', '_debug.png')
	plt.savefig(debug_plot_path)
	plt.close()

	print(f"📈 Debug plot saved to: {debug_plot_path}")
