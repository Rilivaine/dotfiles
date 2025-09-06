#!/usr/bin/env python3
import subprocess
import json

def get_binds():
    """Fetches all binds via hyprctl in JSON format."""
    result = subprocess.run(
        ['hyprctl', 'binds', '-j'],
        capture_output=True,
        text=True,
        check=True
    )
    return json.loads(result.stdout)

def format_bind(bind: dict[str, str]):
    """Formats a single bind entry for printing."""
    mods = bind.get('modkeys') or [str(bind.get('modmask', ''))]
    key = bind.get('key', '')
    dispatcher = bind.get('dispatcher', '')
    description = bind.get('description', '')
    arg = bind.get('arg', '')
    mods_str = '+'.join(mods)
    return f"{mods_str} + {key} → {dispatcher} {arg} — {description}".strip()

def main():
    binds = get_binds()
    for b in binds:
        print(format_bind(b))

if __name__ == '__main__':
    main()
