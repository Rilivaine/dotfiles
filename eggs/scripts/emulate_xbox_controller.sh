#!/bin/bash

echo "=== Available input devices ==="
echo

# Print formatted device info with handler line highlighted
awk -v RS= '
/^I:/ {
    print "---------------------------------------"
    print $0
}
' /proc/bus/input/devices

echo
read -p "Enter event number (e.g. 19 for /dev/input/event19): " EVENTNUM
DEVICE="/dev/input/event$EVENTNUM"

# Check if device exists
if [[ ! -e "$DEVICE" ]]; then
  echo "Error: $DEVICE does not exist."
  exit 1
fi

echo "Using device: $DEVICE"
echo

# Unload kernel xpad driver (to avoid conflict)
sudo modprobe -r xpad

# Start xboxdrv with chosen event
sudo xboxdrv \
  --evdev "$DEVICE" \
  --mimic-xpad \
  --detach-kernel-driver \
  --force-feedback \
  --no-extra-events \
  --evdev-absmap ABS_X=x1,ABS_Y=y1,ABS_RX=x2,ABS_RY=y2,ABS_Z=lt,ABS_RZ=rt,ABS_HAT0X=dpad_x,ABS_HAT0Y=dpad_y \
  --evdev-keymap BTN_A=a,BTN_B=b,BTN_X=y,BTN_Y=x,BTN_TL=lb,BTN_TR=rb,BTN_SELECT=start,BTN_START=back,BTN_THUMBL=tl,BTN_THUMBR=tr \
  --axismap -Y1=Y1,-Y2=Y2
