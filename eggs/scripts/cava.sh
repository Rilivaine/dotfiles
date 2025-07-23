#!/bin/env bash

scrDir="$(dirname "$(realpath "$0")")"

usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS]
Options:
  --bar <waybar_cava_bar>
  --width <waybar_cava_width>
  --range <waybar_cava_range>
  --help
  --restart
  --stb <waybar_cava_stbmode>
EOF
    exit 1
}

if ! ARGS=$(getopt -o hr -l help,bar:,width:,range:,restart,stb: -n "$0" -- "$@"); then
    usage
fi

eval set -- "$ARGS"
while true; do
    case "$1" in
        -h|--help) usage ;; 
        --bar) waybar_cava_bar="$2"; shift 2 ;; 
        --width) waybar_cava_width="$2"; shift 2 ;; 
        --range) waybar_cava_range="$2"; shift 2 ;; 
        --restart) pkill -f "cava -p /tmp/bar_cava_config"; exit 0 ;; 
        --stb) waybar_cava_stbmode="$2"; shift 2 ;; 
        --) shift; break ;; 
        *) usage ;; 
    esac
done

bar="${waybar_cava_bar:-▁▂▃▄▅▆▇█}"
bar_length=${#bar}
bar_width=${waybar_cava_width:-$bar_length}
bar_range=${waybar_cava_range:-$((bar_length-1))}

if ! [[ "$bar_width" =~ ^[0-9]+$ ]] || ((bar_width<1)); then usage; fi
if ! [[ "$bar_range" =~ ^[0-9]+$ ]] || ((bar_range<1)); then usage; fi

case ${waybar_cava_stbmode:-0} in
    0) stbBar="" ;; 
    1) stbBar=" " ;; 
    2) stbBar="${bar: -1}" ;; 
    3) stbBar="${bar:0:1}" ;; 
    *) asciiBar="$waybar_cava_stbmode" ;; 
esac

zero_pattern=$(printf '0%.0s' $(seq 1 "$bar_width"))
silence_output=${asciiBar:-${zero_pattern//0/$stbBar}}

dict="s/;//g"
dict+=";s/${zero_pattern}/${silence_output}/g"
for ((i=0; i<bar_length; i++)); do
    dict+=";s/$i/${bar:i:1}/g"
done

config_file="/tmp/bar_cava_config"
cat >"$config_file" <<EOF
[general]
bars = $bar_width
sleep_timer = 1
autosens = 1
[input]
method = pulse
source = auto
[output]
method = raw
raw_target = /dev/stdout
data_format = ascii
ascii_max_range = $bar_range
EOF

cava -p "$config_file" | \
while IFS= read -r line; do
    if [[ "$line" == "$zero_pattern" ]]; then
        echo "$silence_output"
    else
        echo "$line" | sed -u "$dict"
    fi
done

