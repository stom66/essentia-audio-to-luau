

## 🥁 Rhythm Features

|Feature|Description|
|---|---|
|`rhythm.bpm`|The estimated beats per minute (main tempo)|
|`rhythm.beats_position`|List of **timestamps (in seconds)** for each detected beat|
|`rhythm.onset_times`|Timestamps of **musical attacks** — like drum hits|
|`rhythm.bpm_histogram`|Distribution of tempo guesses — first peak = most likely bpm|
|`rhythm.beats_loudness_band_ratio`|How loud each beat is across frequency bands — can help detect **emphasized beats**|

---

## 🧠 Tonal Features

These describe **harmony**, **chords**, and **key**.

### 🔹 `tonal.hpcp` (Harmonic Pitch Class Profile)

- Histogram showing **which musical notes are most present** (C, D, E, etc.)
- Helps identify key or harmony.
### 🔹 `tonal.thpcp`

- A **transposition-invariant** version of HPCP — useful for matching music regardless of key.
### 🔹 `tonal.chords_histogram`

- Shows the **frequency of detected chords** across the track.

📌 **Use for:** Detecting key/chords (e.g., C major), potentially useful for **syncing visuals to harmony**.

---

## 🎚️ **Low-Level Spectral Features**

These describe the **raw frequency content** of the sound — good for classifying texture, timbre, or detecting instruments.
### 🔹 `barkbands`, `melbands`, `melbands128`, `erbbands`

These represent **energy levels in different frequency bands**. Think of them as how much bass, mids, and treble exist in a moment.

- `barkbands`: 24 bands based on human hearing.
- `melbands`: 40 bands based on pitch perception.
- `melbands128`: same as `melbands` but higher resolution (128 bands).
- `erbbands`: another human-ear model (similar to bark).

Each has:

- `mean`, `median`, `min`, `max`: average/typical values across the song
- `stdev`, `var`: how much variation there is
- `dmean`, `dvar`, `dmean2`, `dvar2`: change/deltas between frames

📌 **Use for:** Tone classification, instrument detection, machine learning — **not needed** for rhythm directly.

---

### 🔹 `mfcc` (Mel-Frequency Cepstral Coefficients)

- Captures **timbre** (e.g. "bright" vs "dull" sounds)
- Used in speech/music classification and audio fingerprinting
- `mean`, `cov`, `icov`: statistical summaries

📌 **Use for:** Matching similar sounding clips — **not needed for beatmaps**, but cool for **genre detection** or "feel."

---

### 🔹 `gfcc` (Gammatone Cepstral Coefficients)

- Similar to MFCC but modeled even closer to human hearing.

📌 **Same use as MFCC**, just more detailed.

---

### 🔹 `spectral_contrast_coeffs` & `spectral_contrast_valleys`

- Measures the **difference between strong and weak frequencies**.
- Helps distinguish between percussive vs harmonic content.

📌 **Use for:** Audio fingerprinting, not rhythm. Might help if you're **generating difficulty maps** (e.g., noisier = harder).