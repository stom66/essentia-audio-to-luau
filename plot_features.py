import os
import librosa
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from luau_writer import to_lua_table

def plot_features(y, sr, onset_env, features, output_img_path):
	# y, sr = librosa.load(audio_path, sr=None, mono=True)
	times = np.linspace(0, len(y) / sr, num=len(y))

	# onset_env = librosa.onset.onset_strength(y=y, sr=sr)

	plt.figure(figsize=(16, 6))
	plt.plot(times, y, label='Waveform', alpha=0.5)
	plt.plot(librosa.times_like(onset_env, sr=sr), onset_env / np.max(onset_env), label='Onset Envelope', color='green', alpha=0.5)

	for beat in features['beats']:
		plt.axvline(x=beat, ymin=0, ymax=0.075, color='red', linestyle='solid', label='Low Beat' if beat == features['beats'][0] else "")

	plt.legend(loc='upper right')
	plt.xlabel('Time (s)')
	plt.ylabel('Amplitude / Normalized Onset')
	plt.title('Audio Features')

	# Display tempo on the plot
	tempo = features.get('tempo', None)
	if tempo:
		plt.text(0.99, 0.95, f"Tempo: {tempo:.2f} BPM", transform=plt.gca().transAxes,
					fontsize=12, color='blue', ha='center', va='top',
					bbox=dict(facecolor='white', edgecolor='blue', boxstyle='round,pad=0.3'))


	plt.tight_layout()
	plt.savefig(output_img_path)
	plt.close()
