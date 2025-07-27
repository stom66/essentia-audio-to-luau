# feature_extractor.py
import essentia.standard as es
from luau_writer import to_lua_table

def extract_features_to_luau(audio_path, output_path):
    # Load and analyze audio
    audio = es.MonoLoader(filename=audio_path)()
    beat_tracker = es.BeatTrackerMultiFeature()
    beats, beats_confidence = beat_tracker(audio)

    features_dict = {
        "beats": beats.tolist(),
        "confidence": beats_confidence.tolist() if hasattr(beats_confidence, "tolist") else beats_confidence,
        "duration": len(audio) / 44100,
    }

    # Write Luau output
    with open(output_path, "w") as f:
        f.write("return ")
        f.write(to_lua_table(features_dict))
        f.write("\n")
