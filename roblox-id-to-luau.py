import sys
import requests
import os
import essentia
import essentia.standard as es

def roblox_asset_url(asset_id):
    return f"https://assetdelivery.roblox.com/v1/asset/?id={asset_id}"

def download_audio(asset_id, output_path):
    url = roblox_asset_url(asset_id)
    print(f"Downloading from {url}")
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed to download asset {asset_id}. Status code: {response.status_code}")
        sys.exit(1)

    with open(output_path, "wb") as f:
        f.write(response.content)

    print(f"Saved asset to {output_path}")

def extract_features_to_luau(audio_path, output_path):
    features, _ = es.MusicExtractor()(audio_path)

    features_dict = {}
    for key in features.descriptorNames():
        val = features[key]
        features_dict[key] = val.tolist() if hasattr(val, "tolist") else val

    with open(output_path, "w") as f:
        f.write("return {\n")
        for key, value in features_dict.items():
            f.write(f'  ["{key}"] = ')
            if isinstance(value, list):
                list_string = "{" + ", ".join(map(str, value)) + "}"
                f.write(list_string)
            elif isinstance(value, str):
                f.write(f'"{value}"')
            else:
                f.write(str(value))
            f.write(",\n")
        f.write("}\n")

    print(f"Wrote Luau data to {output_path}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python roblox-id-to-luau.py <roblox_asset_id>")
        sys.exit(1)

    asset_id = sys.argv[1]
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    # Paths
    audio_file = os.path.join(output_dir, f"{asset_id}.mp3")
    luau_file = os.path.join(output_dir, f"{asset_id}.luau")

    # Download and process
    download_audio(asset_id, audio_file)
    extract_features_to_luau(audio_file, luau_file)

if __name__ == "__main__":
    main()
