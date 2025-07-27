# Essentia Music Data to Luau

This is a simple demo project that uses the [Essentia](https://essentia.upf.edu/) audio analysis library to extract musical features from audio and convert them into Luau tables, suitable for use in Roblox projects like rhythm games, music visualizations, or sound-driven gameplay.

## ✨ What It Does

- Accepts either:
  - A **local audio file** (e.g., `.mp3`, `.m4a`, `.wav`)
  - A **Roblox audio asset ID**
- Extracts features such as:
  - Beat positions
  - Beat confidence
  - Track duration
- Saves results into a `<filename>.luau` file using a proper Luau table format

## ✅ Requirements

- Python 3.10 or newer
- [`essentia`](https://essentia.upf.edu/) Python bindings
- `requests` (for downloading Roblox assets)

## ⚙️ Setup Instructions

1. Clone the repository:

    ```bash
    git clone https://github.com/stom66/essentia-audio-to-luau
    cd essentia-audio-to-luau
    ```

2. Create and activate a virtual environment (recommended):

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # or venv\Scripts\activate on Windows
    ```

3. Install dependencies:

    ```bash
    pip install essentia requests
    ```

    > On some systems (like Debian), you may need:
    >
    > ```bash
    > pip install essentia requests --break-system-packages
    > ```

---

## 🚀 Usage

### 🗂️ Convert a Local File

```bash
python file_to_luau.py path/to/audio.mp3
```

This creates:

```
path/to/audio.luau
```

### 🔗 Convert a Roblox Audio Asset ID

```sh
python roblox_id_to_luau.py 123456789 
```

This downloads the audio from Roblox and saves:

```sh
output/123456789.luau
```

Multiple asset IDs are supported:

```sh
python roblox_id_to_luau.py 123456789 987654321
```

## 📄 Output Format

The .luau file contains a Lua-style table with extracted audio features:

```lua
return {
  beats = { 0.25, 0.75, 1.22, ... },
  confidence = { 0.9, 0.85, 0.88, ... },
  duration = 34.2
}
```

### 📚 Understanding the Data

This project uses BeatTrackerMultiFeature from Essentia, which gives you:

- beats: estimated times of beats in seconds
- confidence: confidence values for each beat
- duration: total duration of the audio in seconds

For more about feature extraction, see the Essentia documentation.

Also check out [ABOUT_THE_DATA](ABOUT_THE_DATA.md) for a Chat-GPT generated breakdown of what’s extracted and how to use it.

### 🛠️ Troubleshooting

- Missing module error?

	Run pip install essentia requests inside your virtual environment.

- Essentia install issues?

	Try --break-system-packages or consult their install guide.

- Audio file not working?

	Try converting it to .mp3 or .wav and test again.

### 📜 License

- Demo project by stom66
- Feature extraction powered by [Essentia](https://essentia.upf.edu/)
- Music sample: Pixabay License
	- Track: Dame Esta Noche - House Background Music


This is a proof-of-concept. All rights to underlying libraries and music remain with their respective authors.