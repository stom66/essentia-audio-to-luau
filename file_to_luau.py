# file-to-luau.py
import sys
from pathlib import Path
from feature_extractor import extract_features_to_luau  # ✅ NEW import

def main():
    if len(sys.argv) != 2:
        print("Usage: python file-to-luau.py <audio_file>")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    if not input_path.is_file():
        print(f"❌ Error: File not found: {input_path}")
        sys.exit(1)

    output_path = input_path.with_suffix(".luau")
    extract_features_to_luau(str(input_path), str(output_path))
    print(f"✅ Features saved to: {output_path}")

if __name__ == "__main__":
    main()
