# roblox-id-to-luau.py
import sys
import requests
import os
from feature_extractor import extract_features_to_luau  # ✅ NEW import

def roblox_asset_url(asset_id):
    return f"https://assetdelivery.roblox.com/v1/asset/?id={asset_id}"

def download_audio(asset_id, output_path):
    url = roblox_asset_url(asset_id)
    print(f"Downloading from {url}")
    response = requests.get(url)

    if response.status_code != 200:
        print(f"❌ Failed to download asset {asset_id}. Status code: {response.status_code}")
        return False

    with open(output_path, "wb") as f:
        f.write(response.content)

    print(f"✅ Saved asset to {output_path}")
    return True

def main():
    if len(sys.argv) < 2:
        print("Usage: python roblox-id-to-luau.py <roblox_asset_id1> [<roblox_asset_id2> ...]")
        sys.exit(1)

    asset_ids = sys.argv[1:]
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    for asset_id in asset_ids:
        print(f"\n🔍 Processing Asset ID: {asset_id}")
        audio_file = os.path.join(output_dir, f"{asset_id}.mp3")
        luau_file = os.path.join(output_dir, f"{asset_id}.luau")

        if download_audio(asset_id, audio_file):
            extract_features_to_luau(audio_file, luau_file)

if __name__ == "__main__":
    main()
