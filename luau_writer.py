# luau_writer.py

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
        key = k if isinstance(k, str) and k.isidentifier() else f'["{k}"]'
        lines.append(f"{key} = {to_lua_value(v)},")
    return "{\n  " + "\n  ".join(lines) + "\n}"
