# feature_extractor.py

# Suppress librosa's occasional user warnings
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

import librosa
import numpy as np
from scipy.signal import butter, lfilter
from luau_writer import to_lua_table
from plot_features import plot_features

# --- Constants ---

SAMPLE_RATE = 44100              # Audio sample rate in Hz; 44.1kHz is standard for music/audio
HOP_LENGTH = 512                 # Number of samples between successive analysis frames; affects time resolution
PADDING_SEC = 0.5                # Duration of audio padding (in seconds) added at both start and end to avoid edge artifacts

LOWPASS_CUTOFF = 4000             # Cutoff frequency (Hz) for low-pass filter; removes high-frequency noise before onset detection
LOWPASS_ORDER = 5                # Order of the Butterworth filter; higher values mean a steeper filter roll-off

SILENCE_THRESHOLD = 0.01       # Amplitude threshold for detecting silence; beats in quieter regions below this are discarded
SILENCE_WINDOW_SEC = 0.05        # Duration (in seconds) of the window used to measure silence around each beat

ONSET_PEAK_RATIO = 1.5           # Multiplier used to detect a strong onset before the first beat (relative to average onset strength)
EXTRAPOLATION_MARGIN = 0.25      # Fraction of a beat interval allowed to extrapolate the final beat beyond the track duration

FIRST_BEAT_LOOKBACK_FRAMES = 3   # Number of frames to look back before the first detected beat to search for a potential earlier onset
FIRST_BEAT_DUPLICATE_GAP = 0.2   # Minimum time difference (in seconds) required to insert a new first beat to avoid duplicates


# --- Helper Functions ---

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

def filter_silence(y, beats, sr=SAMPLE_RATE, threshold=SILENCE_THRESHOLD, window_sec=SILENCE_WINDOW_SEC):
	"""
	Remove beats that fall within silent regions based on amplitude threshold.
	Always keeps the final beat.
	"""
	filtered = []
	window = int(window_sec * sr)
	length = len(y)

	for i, b in enumerate(beats):
		start = max(0, int(b * sr))
		end = min(length, start + window)
		is_final = i == len(beats) - 1

		if is_final or (end > start and np.max(np.abs(y[start:end])) > threshold):
			filtered.append(b)

	return np.array(filtered)

def adjust_beat_times(beat_times, tempo, duration, pad_len, sr, onset_env=None, hop_length=HOP_LENGTH):
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

		search_start = max(0, first_frame - FIRST_BEAT_LOOKBACK_FRAMES)
		peak_frame = np.argmax(onset_env[search_start:first_frame + 1])
		peak_value = onset_env[search_start + peak_frame]

		# Compare peak strength to average to confirm it's a real onset
		avg_env = np.mean(onset_env)
		if peak_value > avg_env * ONSET_PEAK_RATIO:
			back_time = (search_start + peak_frame) * hop_length / sr
			if back_time < first_beat - FIRST_BEAT_DUPLICATE_GAP:
				beat_times = np.insert(beat_times, 0, back_time)

	# --- Extrapolate final beat ---
	last = beat_times[-1]
	next_beat = last + interval
	if next_beat <= duration + EXTRAPOLATION_MARGIN * interval:
		beat_times = np.append(beat_times, next_beat)

	# Clip any that overshoot duration
	beat_times = beat_times[beat_times <= duration]

	return beat_times

# --- Main Feature Extraction ---

def extract_features_to_luau(audio_path, output_path):
	try:
		y, sr = librosa.load(audio_path, sr=SAMPLE_RATE)
	except Exception:
		return

	pad_len = int(sr * PADDING_SEC)

	# Pad audio at start and end (reflect padding to reduce edge artifacts)
	y_padded = np.pad(y, (pad_len, pad_len), mode='reflect')

	# Apply low-pass filter to ignore very high frequencies
	y_filtered = butter_lowpass_filter(
		y_padded, cutoff=LOWPASS_CUTOFF, sr=sr, order=LOWPASS_ORDER
	)

	# Compute onset envelope for beat detection
	onset_env = librosa.onset.onset_strength(
		y=y_filtered, sr=sr, hop_length=HOP_LENGTH
	)

	# Beat tracking
	tempo, beat_frames = librosa.beat.beat_track(
		onset_envelope=onset_env, sr=sr, hop_length=HOP_LENGTH
	)

	# Convert beat frames to time
	beat_times = librosa.frames_to_time(beat_frames, sr=sr, hop_length=HOP_LENGTH)

	# Adjust for padding, infer first/last beats
	duration = librosa.get_duration(y=y, sr=sr)
	beat_times = adjust_beat_times(
		beat_times, tempo, duration, pad_len, sr, onset_env=onset_env, hop_length=HOP_LENGTH
	)

	# Filter out silent beats using original audio (not padded)
	beat_times = filter_silence(
		y, beat_times, sr=sr, threshold=SILENCE_THRESHOLD, window_sec=SILENCE_WINDOW_SEC
	)

	# Extract pitch data
	pitches, magnitudes = librosa.piptrack(y=y, sr=sr, hop_length=HOP_LENGTH)

	notes = []
	for t in librosa.time_to_frames(beat_times, sr=sr, hop_length=HOP_LENGTH):
		if t >= magnitudes.shape[1]:
			continue
		index = magnitudes[:, t].argmax()
		freq = pitches[index, t] if magnitudes[index, t] > 0 else 0
		notes.append(freq_to_note(freq))

	# Compile results
	result = {
		"beats": list(np.round(beat_times, 3)),
		"notes": notes,
		"tempo": round(tempo, 2),
		"duration": round(duration, 2),
		"skipBeats": list(),
		"ignoreFirstXBeats": 0,
		"ignoreLastXBeats": 0
	}

	# Write to Lua file
	with open(output_path, 'w') as f:
		f.write('return ')
		f.write(to_lua_table(result))
		f.write('\n')

	# Optional debug plot
	plot_features(y_filtered, sr, onset_env, result, output_path.replace('.luau', '_debug.png'))
