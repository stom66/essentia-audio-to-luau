# Essentia Music Feature Extractor Demo

This is a simple demo project that uses the [Essentia](https://essentia.upf.edu/) audio analysis library to extract detailed musical features from an audio file and save them as JSON data.

## What It Does

- Takes an input audio file (e.g., `.mp3`, `.m4a`)
- Extracts features such as tempo (BPM), beat positions, and low-level audio descriptors
- Saves the extracted data into a `song_features.json` file

This demo can serve as a starting point for music analysis tasks such as building rhythm games, music visualization, or audio classification.

## Requirements

- Python 3.10 or newer
- `essentia` Python library

## Setup Instructions

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/essentia-music-extractor-demo.git
    cd essentia-music-extractor-demo
    ```

2. Create and activate a virtual environment (recommended):
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3. Install dependencies:
    ```bash
    pip install essentia
    ```
    > **Note:** On some systems, you may need to add `--break-system-packages` when installing Essentia:
    > ```bash
    > pip install essentia --break-system-packages
    > ```

4. Add your audio file to the `input/` directory. Update the `audio_path` in `extractData.py` if needed.

5. Run the feature extraction script:
    ```bash
    python extractData.py
    ```

6. After running, a `song_features.json` file will be created with the extracted features.

## Understanding the Output

- The JSON file contains detailed musical data, including BPM (`rhythm.bpm`), beat positions (`rhythm.beats_position`), and more.
- You can use this data to build rhythm-based applications, analyze music structure, or explore audio features.
- See [ABOUT_THE_DATA](ABOUT_THE_DATA.md) for a Chat-GPT generated explanation of the json data.

## Troubleshooting

- If you get errors about missing `essentia` module, ensure you installed it in the active virtual environment.
- For Debian-based systems, you may need to install system dependencies or use `--break-system-packages`.
- Make sure your Python version is compatible with Essentia (3.10+ recommended).

## License

Whatever. I did nothing here but tie some things together. Check the Essentia license if you have concerns.