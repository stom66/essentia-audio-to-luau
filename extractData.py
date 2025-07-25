import essentia
import essentia.standard as es
import sys
from pathlib import Path

if len(sys.argv) != 2:
    print("Usage: python extractData.py <audio_file>")
    sys.exit(1)

input_path = Path(sys.argv[1])
if not input_path.exists():
    print(f"Error: File not found: {input_path}")
    sys.exit(1)

# Extract features using Essentia
features, _ = es.MusicExtractor()(str(input_path))

# Convert Pool to a regular dict
features_dict = {}
for key in features.descriptorNames():
    val = features[key]
    features_dict[key] = val.tolist() if hasattr(val, 'tolist') else val

# Helpers to convert dict to Lua table
def to_lua_value(v):
    if isinstance(v, dict):
        return to_lua_table(v)
    elif isinstance(v, list):
        return "{" + ", ".join(to_lua_value(i) for i in v) + "}"
    elif isinstance(v, str):
        return f'"{v}"'
    elif isinstance(v, bool):
        return "true" if v else "false"
    elif isinstance(v, (int, float)):
        return str(v)
    else:
        return f'"{str(v)}"'

def to_lua_table(d):
    lines = []
    for k, v in d.items():
        key = k if k.isidentifier() else f'["{k}"]'
        lines.append(f"{key} = {to_lua_value(v)},")
    return "{\n  " + "\n  ".join(lines) + "\n}"

# Output path with .luau extension in the same folder
output_path = input_path.with_suffix('.luau')

with open(output_path, "w") as f:
    f.write("return ")
    f.write(to_lua_table(features_dict))
    f.write("\n")

print(f"Features saved to {output_path}")
