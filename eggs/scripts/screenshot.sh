#!/usr/bin/env sh

# === CONFIG ===

# Default to XDG Pictures dir if not set
XDG_PICTURES_DIR="${XDG_PICTURES_DIR:-$HOME/Pictures}"
SAVE_DIR="${2:-${XDG_PICTURES_DIR}/Screenshots}"
SAVE_FILE="$(date +'%y%m%d_%Hh%Mm%Ss_screenshot.png')"
TEMP_SCREENSHOT="$(mktemp --suffix=.png)"
SWAPPY_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/swappy"

# === REQUIREMENTS CHECK ===

for cmd in grimblast swappy hyprshade notify-send; do
	if ! command -v "$cmd" >/dev/null 2>&1; then
		echo "Error: '$cmd' is required but not installed."
		exit 1
	fi
done

# === SHADER HANDLING ===

restore_shader() {
	[ -n "$shader" ] && hyprshade on "$shader"
}

save_shader() {
	shader=$(hyprshade current)
	hyprshade off
	trap restore_shader EXIT
}

# === SETUP ===

save_shader
mkdir -p "$SAVE_DIR" "$SWAPPY_DIR"

# Create temporary swappy config for this session
echo -e "[Default]\nsave_dir=$SAVE_DIR\nsave_filename_format=$SAVE_FILE" >"$SWAPPY_DIR/config"

# === ERROR DISPLAY ===

print_error() {
	cat <<EOF
Usage: ./screenshot.sh <action>

Valid actions:
  p   - screenshot all outputs
  s   - snip area manually
  sf  - snip area (frozen screen)
  m   - screenshot focused monitor
EOF
}

# === MAIN LOGIC ===

case "$1" in
	p)  grimblast copysave screen "$TEMP_SCREENSHOT" ;;
	s)  grimblast copysave area "$TEMP_SCREENSHOT" ;;
	sf) grimblast --freeze copysave area "$TEMP_SCREENSHOT" ;;
	m)  grimblast copysave output "$TEMP_SCREENSHOT" ;;
	*)  print_error; exit 1 ;;
esac

swappy -f "$TEMP_SCREENSHOT"
rm -f "$TEMP_SCREENSHOT"

# === NOTIFICATION ===

FINAL_PATH="$SAVE_DIR/$SAVE_FILE"
[ -f "$FINAL_PATH" ] && notify-send -a "Screenshot" -i "$FINAL_PATH" "Saved in $SAVE_DIR"

