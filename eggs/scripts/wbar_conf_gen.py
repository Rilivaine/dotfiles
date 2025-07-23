#!/usr/bin/env python3
"""
Rewrite of the Waybar control-shell into Python, with improved structure and error handling.
Supports multiple configuration profiles to merge into a single bar setup.
"""
import argparse
import logging
import subprocess
import sys
import string
from pathlib import Path
import re

# region utils

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

def dict_substitute(text: str, env: dict[str, str]) -> str:
    template = string.Template(text)
    return template.safe_substitute(env)

def append_file(output: Path, content: str) -> None:
    with output.open('a') as f:
        f.write(content)

def restart_waybar(conf: Path, style: Path) -> None:
    subprocess.run(['killall', 'waybar'], check=False)
    subprocess.Popen(['waybar', '--config', str(conf), '--style', str(style)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    logging.info("Waybar restarted.")

def read_control(ctl_path: Path) -> list[str]:
    if not ctl_path.exists():
        logging.error(f"Control file not found: {ctl_path}")
        sys.exit(1)
    return [line.strip() for line in ctl_path.read_text().splitlines() if line.strip()]

def parse_control(ctl_path: Path) -> dict[str, str]:
    ctl_lines = read_control(ctl_path)
    active = next(line for line in ctl_lines if line.startswith('1|'))
    _, output, height, position, left_col, center_col, right_col = active.split('|')

    return {'output': output, 'height': height, 'position': position, 'left_col': left_col, 'center_col': center_col, 'right_col': right_col}

def write_control(ctl_path: Path, lines: list[str]) -> None:
    tmp = ctl_path.with_suffix('.ctl.tmp')
    tmp.write_text("\n".join(lines) + "\n")
    tmp.replace(ctl_path)
    logging.debug(f"Wrote updated control to {ctl_path}")

def rotate_index(ctl_path: Path, mode: str) -> tuple[list[str], bool]:
    lines = read_control(ctl_path)
    n = len(lines)
    if n <= 1 or mode not in {'n', 'p'}:
        return lines, False
    active_idx = next((i for i, l in enumerate(lines) if l.startswith('1|')), None)
    if active_idx is None:
        logging.warning("No active entry in control; nothing to rotate.")
        return lines, False
    new_idx = (active_idx + 1) % n if mode == 'n' else (active_idx - 1) % n
    updated: list[str] = []
    for i, l in enumerate(lines):
        cols = l.split('|', 2)
        flag = '1' if i == new_idx else '0'
        updated.append(flag + '|' + '|'.join(cols[1:]))
    write_control(ctl_path, updated)
    return updated, True

# endregion utils

# region bar config

def generate_header(config_template_file: Path, dict: dict[str, str], should_add_comma: bool) -> str:
    text = dict_substitute(config_template_file.read_text(), dict)
    text = dict_substitute(text, dict)

    if should_add_comma:
        text += ','
    return text

def generate_padding_modules(col: str) -> tuple[list[str], str]:
    raw = col
    mapping = {'(': 'custom/l_end', ')': 'custom/r_end', '[': 'custom/sl_end', ']': 'custom/sr_end', '{': 'custom/rl_end', '}': 'custom/rr_end'}
    for k, v in mapping.items():
        raw = raw.replace(k, v)
    mods = raw.split()

    entry = f"\"custom/padd\", " + ", ".join(f'\"{m}\"' for m in mods) + ", \"custom/padd\""
    return mods, entry

def generate_modules(mods: list[str], modules_dir: Path) -> str:
    seen: set[str] = set()
    text = ''
    for m in mods:
        name = m.split('/')[-1].split('#')[0]
        if name in seen:
            continue
        seen.add(name)
        path = modules_dir / f"{name}.jsonc"
        if path.exists():
            text += path.read_text()
    
    return text

def bar_dict_update(dict: dict[str, str], modules_dir: Path, parsed_bar_dict: dict[str, str], name: str) -> dict[str, str]:
    
    if not parsed_bar_dict['output']:
        parsed_bar_dict['output'] = f"\"*\""

    if not parsed_bar_dict['height']:
        res = subprocess.getoutput("cat /sys/class/drm/*/modes | head -1 | cut -dx -f2")
        parsed_bar_dict['height'] = str(int(int(res)*2/100))

    mods_left, mods_left_entry = generate_padding_modules(parsed_bar_dict['left_col'])
    mods_center, mods_center_entry = generate_padding_modules(parsed_bar_dict['center_col'])
    mods_right, mods_right_entry = generate_padding_modules(parsed_bar_dict['right_col'])

    if parsed_bar_dict['position'] == 'left':
        hv_pos = 'width'
        r_deg = '90'
    elif parsed_bar_dict['position'] == 'right':
        hv_pos = 'width'
        r_deg = '270'
    else:
        hv_pos = 'height'
        r_deg = '0'

    i_size = int(parsed_bar_dict['height']) * 6 // 10
    if i_size < 12:
      i_size = 12

    i_task = int(parsed_bar_dict['height']) * 6 // 10
    if i_task < 16:
      i_task = 16

    i_priv = int(parsed_bar_dict['height']) * 6 // 13
    if i_priv < 12:
      i_priv = 12

    dict['w_name'] = name

    dict['w_output'] = parsed_bar_dict['output']
    dict['w_height'] = parsed_bar_dict['height']
    dict['w_position'] = parsed_bar_dict['position']
    dict['w_modules_left'] = mods_left_entry
    dict['w_modules_center'] = mods_center_entry
    dict['w_modules_right'] = mods_right_entry
    dict['w_modules_config'] = generate_modules(mods_left + mods_center + mods_right, modules_dir)
    dict['set_sysname'] = subprocess.getoutput('hostnamectl hostname').strip()

    dict['hv_pos'] = hv_pos
    dict['r_deg'] = r_deg

    dict['i_size'] = str(i_size)

    dict['i_task'] = str(i_task)

    dict['i_priv'] = str(i_priv)

    return dict

def build_bar(ctl_path: Path, modules_dir: Path, template_file: Path, should_add_comma: bool) -> str:
  # determine dynamic env per-profile
  config_dictionary: dict[str, str] = {}
  parsed_bar_dict = parse_control(ctl_path)
  name = ctl_path.stem
  # generate profile blocks
  config_dictionary = bar_dict_update(config_dictionary, modules_dir, parsed_bar_dict, name)

  # generate header
  return generate_header(template_file, config_dictionary, should_add_comma)  

# endregion bar config

# region style

def generate_style(style_template_file: Path, dict: dict[str, str]) -> str:
    text = dict_substitute(style_template_file.read_text(), dict)
    text = dict_substitute(text, dict)

    return text

def get_modules(modules_dir: Path):
    pattern = re.compile(r'"(.*?)":\s*{')
    modules_ls: list[str] = []


    for path in sorted(modules_dir.iterdir()):
        if path.suffix != ".jsonc" or path.name in ("footer.jsonc"):
            continue
        with open(path) as f:
            for line in f:
                m = pattern.search(line)
                if not m:
                    continue

                parts = m.group(1).split('/')
                prefix = "#custom-" if parts[0] == "custom" else "#"

                if parts[0] == "custom" and len(parts) > 1:
                    name = parts[1].split('#')[0]
                else:
                    name = parts[-1]

                modules_ls.append(f".${{w_name}} {prefix}{name},\n")
                break

    return modules_ls

def style_dict_update(dict: dict[str, str], modules_dir: Path, parsed_bar_dict: dict[str, str], name: str) -> dict[str, str]:
    if not parsed_bar_dict['height']:
        res = subprocess.getoutput("cat /sys/class/drm/*/modes | head -1 | cut -dx -f2")
        parsed_bar_dict['height'] = str(int(int(res)*2/100))

    dict['b_height'] = parsed_bar_dict['height']

    dict['w_name'] = name

    dict['b_radius'] = str(int(int(dict['b_height']) * 70 / 100))
    dict['c_radius'] = str(int(int(dict['b_height']) * 25 / 100))
    dict['t_radius'] = str(int(int(dict['b_height']) * 25 / 100))
    dict['e_margin'] = str(int(int(dict['b_height']) * 30 / 100))
    dict['e_paddin'] = str(int(int(dict['b_height']) * 10 / 100))
    dict['g_margin'] = str(int(int(dict['b_height']) * 14 / 100))
    dict['g_paddin'] = str(int(int(dict['b_height']) * 15 / 100))
    dict['w_radius'] = str(int(int(dict['b_height']) * 30 / 100))
    dict['w_margin'] = str(int(int(dict['b_height']) * 10 / 100))
    dict['w_paddin'] = str(int(int(dict['b_height']) * 10 / 100))
    dict['w_padact'] = str(int(int(dict['b_height']) * 40 / 100))
    dict['s_fontpx'] = str(int(int(dict['b_height']) * 34 / 100))

    if int(dict['b_height']) <= 30:
        dict['e_paddin'] = '0'

    if int(dict['s_fontpx']) <= 10:
        dict['s_fontpx'] = '10'

    dict['w_position'] = parsed_bar_dict['position']
    if dict['w_position'] == 'top' or dict['w_position'] == 'bottom':
        dict['x1g_margin'] = dict['g_margin']
        dict['x2g_margin'] = '0'
        dict['x3g_margin'] = dict['g_margin']
        dict['x4g_margin'] = '0'
        dict['x1rb_radius'] = '0'
        dict['x2rb_radius'] = dict['b_radius']
        dict['x3rb_radius'] = dict['b_radius']
        dict['x4rb_radius'] = '0'
        dict['x1lb_radius'] = dict['b_radius']
        dict['x2lb_radius'] = '0'
        dict['x3lb_radius'] = '0'
        dict['x4lb_radius'] = dict['b_radius']
        dict['x1rc_radius'] = '0'
        dict['x2rc_radius'] = dict['c_radius']
        dict['x3rc_radius'] = dict['c_radius']
        dict['x4rc_radius'] = '0'
        dict['x1lc_radius'] = dict['c_radius']
        dict['x2lc_radius'] = '0'
        dict['x3lc_radius'] = '0'
        dict['x4lc_radius'] = dict['c_radius']
        dict['x1'] = 'top'
        dict['x2'] = 'bottom'
        dict['x3'] = 'left' 
        dict['x4'] = 'right'
    
    else:
        dict['x1g_margin'] = '0'
        dict['x2g_margin'] = dict['g_margin']
        dict['x3g_margin'] = '0'
        dict['x4g_margin'] = dict['g_margin']
        dict['x1rb_radius'] = '0'
        dict['x2rb_radius'] = '0'
        dict['x3rb_radius'] = dict['b_radius']
        dict['x4rb_radius'] = dict['b_radius']
        dict['x1lb_radius'] = dict['b_radius']
        dict['x2lb_radius'] = dict['b_radius']
        dict['x3lb_radius'] = '0'
        dict['x4lb_radius'] = '0'
        dict['x1rc_radius'] = '0'
        dict['x2rc_radius'] = dict['c_radius']
        dict['x3rc_radius'] = dict['c_radius']
        dict['x4rc_radius'] = '0'
        dict['x1lc_radius'] = dict['c_radius']
        dict['x2lc_radius'] = '0'
        dict['x3lc_radius'] = '0'
        dict['x4lc_radius'] = dict['c_radius']
        dict['x1'] = 'left'
        dict['x2'] = 'right'
        dict['x3'] = 'top' 
        dict['x4'] = 'bottom'

    dict['modules_ls'] = ''.join(get_modules(modules_dir))
    
    return dict

def build_style(ctl_path: Path, style_file: Path, modules_dir: Path) -> str:
    dictionary: dict[str, str] = {}
    parsed_bar_dict = parse_control(ctl_path)
    name = ctl_path.stem

    dictionary = style_dict_update(dictionary, modules_dir, parsed_bar_dict, name)

    return generate_style(style_file, dictionary)

# endregion style

def main():
    setup_logging()
    p = argparse.ArgumentParser(description="Generate and rotate Waybar config with support for multiple profiles")
    p.add_argument('--mode', nargs='?', choices=['n', 'p'], help="Mode: 'n' for next, 'p' for previous (only if single ctl)")
    args = p.parse_args()

    home = Path.home()
    base_cfg = home / '.config' / 'waybar'
    style_file = base_cfg / 'style.css'
    config_file = base_cfg / 'config.jsonc'
    modules_dir = base_cfg / 'modules'
    config_template_file = modules_dir / 'template.jsonc'
    style_template_file = modules_dir / 'style.css'
    bars_dir = base_cfg

    profiles: list[Path] = []
    # load each profile subdir
    for ctl in sorted(bars_dir.iterdir()):
        if ctl.is_file() and ctl.suffix == ".ctl":
            profiles.append(ctl)
    if not profiles:
      profiles.extend([base_cfg / 'config.ctl'])

    # start writing
    if config_file.exists():
        config_file.unlink()

    if style_file.exists():
        style_file.unlink()

    config_content = ''
    style_content = ''

    # process each profile sequentially
    for index, ctl_path in enumerate(profiles):
        rotate_index(ctl_path, args.mode)
        shouldAddComma = index >= 0 and index < len(profiles) - 1
        config_content += build_bar(ctl_path, modules_dir, config_template_file, shouldAddComma)
        style_content += build_style(ctl_path, style_template_file, modules_dir)

    config_file.write_text('[' + config_content + ']')
    style_file.write_text(style_content)

    # subprocess.run([str(scr_dir / 'wbarstylegen.sh')], check=False)
    # restart after all profiles
    restart_waybar(config_file, style_file)

if __name__ == '__main__':
    main()
