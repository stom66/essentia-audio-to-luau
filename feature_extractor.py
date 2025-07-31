# feature_extractor.py

# Suppress librosa's occasional user warnings
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

import librosa
import numpy as np
from scipy.signal import butter, lfilter
from luau_writer import to_lua_table
from plot_features import plot_features

def butter_lowpass_filter(data, cutoff, sr, order=5):
	nyq = 0.5 * sr
	normal_cutoff = cutoff / nyq
	b, a = butter(order, normal_cutoff, btype='low', analog=False)
	return lfilter(b, a, data)

def freq_to_note(freq):
	if freq <= 0:
		return "N/A"
	note_names = ['C', 'C#', 'D', 'D#', 'E', 'F',
				  'F#', 'G', 'G#', 'A', 'A#', 'B']
	midi = int(np.round(69 + 12 * np.log2(freq / 440.0)))
	return note_names[midi % 12] + str(midi // 12 - 1)

def filter_silence(y, beats, sr=44100, threshold=0.005, window_sec=0.05):
	"""
	Remove beats that fall within silent regions based on amplitude threshold.
	"""
	filtered = []
	window = int(window_sec * sr)
	length = len(y)

	for b in beats:
		start = max(0, int(b * sr))
		end = min(length, start + window)
		if end > start and np.max(np.abs(y[start:end])) > threshold:
			filtered.append(b)
	return np.array(filtered)

def adjust_beat_times(beat_times, tempo, duration, pad_len, sr, onset_env=None, hop_length=512):
	# Remove offset from padding
	beat_times = beat_times - (pad_len / sr)
	beat_times = beat_times[beat_times >= 0]

	if len(beat_times) < 1 or tempo <= 0:
		return beat_times

	interval = 60.0 / tempo

	# --- Add back first beat if onset before beat[0] is strong ---
	if onset_env is not None and len(beat_times) > 0:
		first_beat = beat_times[0]
		first_frame = int(first_beat * sr / hop_length)

		search_start = max(0, first_frame - 3)  # look back a few frames
		peak_frame = np.argmax(onset_env[search_start:first_frame + 1])
		peak_value = onset_env[search_start + peak_frame]

		# Compare peak strength to average to confirm it's a real onset
		avg_env = np.mean(onset_env)
		if peak_value > avg_env * 1.5:
			# Insert new first beat
			back_time = (search_start + peak_frame) * hop_length / sr
			if back_time < first_beat - 0.2:  # avoid duplicates
				beat_times = np.insert(beat_times, 0, back_time)

	# Extrapolate last beat (as before)
	last = beat_times[-1]
	next_beat = last + interval
	# Allow one beat beyond duration if close to it
	if next_beat <= duration + 0.25 * interval:
		beat_times = np.append(beat_times, next_beat)

	# Clip any that overshoot duration
	beat_times = beat_times[beat_times <= duration]

	return beat_times


def extract_features_to_luau(audio_path, output_path):
	try:
		y, sr = librosa.load(audio_path, sr=44100)
	except Exception:
		return

	# Constants
	pad_len = int(sr * 0.5)  # add some padding
	hop_length = 512       # Default hop length for librosa
	window_sec = 0.05      # Silence check window in seconds
	silence_thresh = 0.0025 # Silence amplitude threshold

	# Pad audio at start and end (reflect padding to reduce edge artifacts)
	y_padded = np.pad(y, (pad_len, pad_len), mode='reflect')

	# Apply low-pass filter to ignore very high frequencies
	y_filtered = butter_lowpass_filter(y_padded, cutoff=4000, sr=sr)

	# Compute onset envelope for beat detection
	onset_env = librosa.onset.onset_strength(y=y_filtered, sr=sr, hop_length=hop_length)

	# Pad onset envelope to encourage trailing beat detection
	#pad_frames = int(pad_len / hop_length)
	#onset_env = np.pad(onset_env, (pad_frames, 0), mode='constant')

	# Beat tracking using padded onset envelope
	tempo, beat_frames = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr, hop_length=hop_length)

	# Convert beat frames to time (seconds)
	beat_times = librosa.frames_to_time(beat_frames, sr=sr, hop_length=hop_length)

	# Adjust beat times for padding offset, remove negatives, extrapolate edges safely
	duration = librosa.get_duration(y=y, sr=sr)
	beat_times = adjust_beat_times(beat_times, tempo, duration, pad_len, sr)

	# Filter out silent beats based on original (unpadded) audio
	# Note: use original audio y (unpadded) to avoid false positives from padding
	beat_times = filter_silence(y, beat_times, sr=sr, threshold=silence_thresh, window_sec=window_sec)

	# Extract pitch and magnitude (using original unpadded audio)
	pitches, magnitudes = librosa.piptrack(y=y, sr=sr, hop_length=hop_length)

	notes = []
	for t in librosa.time_to_frames(beat_times, sr=sr, hop_length=hop_length):
		if t >= magnitudes.shape[1]:
			# skip beats outside magnitude time frames
			continue
		index = magnitudes[:, t].argmax()
		freq = pitches[index, t] if magnitudes[index, t] > 0 else 0
		notes.append(freq_to_note(freq))

	# Compile results
	result = {
		"beats": list(np.round(beat_times, 3)),
		"notes": notes,
		"tempo": round(tempo, 2),
		"duration": round(duration, 2)
	}

	# Write result to Lua table file
	with open(output_path, 'w') as f:
		f.write('return ')
		f.write(to_lua_table(result))
		f.write('\n')

	# Optional: generate debug plot
	plot_features(audio_path, result, output_path.replace('.luau', '_debug.png'))
