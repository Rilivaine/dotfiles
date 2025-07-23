#!/usr/bin/env sh
set -eu

# Prevent multiple instances
if pidof -x "$(basename "$0")" | grep -v "^$$\$" > /dev/null 2>&1; then
  echo "An instance of the script is already running..."
  exit 1
fi

scr_dir=$(dirname "$(realpath "$0")")
source "$scr_dir/common.sh"

use_swayosd=false
if command -v swayosd-client >/dev/null 2>&1 && pgrep -x swayosd-server >/dev/null; then
  use_swayosd=true
fi

default_step=5
notify=${waybar_brightness_notification:-true}
action=""
step=$default_step

print_usage() {
  cat <<EOF
Usage: $(basename "$0") [-i | -d] [value] [-q]
  -i        increase brightness
  -d        decrease brightness
  -q        quiet (no notification)
  value     percentage step (default ${default_step}%)
EOF
}

while [ $# -gt 0 ]; do
  case $1 in
    -i|--increase)
      [ -n "$action" ] && { echo "Only one of -i or -d allowed"; print_usage; exit 1; }
      action=increase; shift ;;  
    -d|--decrease)
      [ -n "$action" ] && { echo "Only one of -i or -d allowed"; print_usage; exit 1; }
      action=decrease; shift ;;
    -q|--quiet)
      notify=false; shift ;;
    -h|--help)
      print_usage; exit 0 ;;
    [0-9]*)
      if echo "$1" | grep -Eq '^[0-9]+$'; then
        step=$1
        shift
      else
        print_usage; exit 1
      fi;;
    *)
      print_usage; exit 1;;
  esac
done

[ -n "$action" ] || { echo "Action (-i or -d) is required"; print_usage; exit 1; }

get_brightness() {
  brightnessctl -m | awk -F"," '{print $4}' | tr -d '%'
}

send_notification() {
  local b=$(get_brightness)
  local info=$(brightnessctl info | awk -F"'" '/Device/ {print $2}')
  local angle=$(( ((b + 2) / 5) * 5 ))
  local icon="$HOME/.config/dunst/icons/vol-${angle}.svg"
  [ ! -f "$icon" ] && icon="dialog-information"
  local bar
  bar=$(printf '%0.s.' $(seq 1 $((b / 15))))
  notify_single -a brightness -t 800 -i "$icon" "${b}%${bar}" "$info"
}

current=$(get_brightness)
[ "$current" -lt 10 ] && step=1

case "$action" in
increase)
  if $use_swayosd; then
    swayosd-client --brightness raise "$step"
    exit 0
  fi
  brightnessctl set +${step}%
  ;;
decrease)
  if [ "$current" -le 1 ]; then
    brightnessctl set ${step}%
  else
    if $use_swayosd; then
      swayosd-client --brightness lower "$step"
      exit 0
    fi
    brightnessctl set ${step}%-
  fi
  ;;
  esac

[ "$notify" = true ] && send_notification

