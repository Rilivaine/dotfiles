#!/usr/bin/env bash
# ~/bin/xboxdrv.sh — run as user

# Prevent xpad from loading
sudo modprobe -r xpad

# Launch xboxdrv with all mappings
sudo xboxdrv \
  --evdev /dev/input/event30 \
  --mimic-xpad \
  --detach-kernel-driver \
  --force-feedback \
  --no-extra-events \
  --silent \
  --evdev-absmap ABS_X=x1,ABS_Y=y1,ABS_RX=x2,ABS_RY=y2,ABS_Z=lt,ABS_RZ=rt,ABS_HAT0X=dpad_x,ABS_HAT0Y=dpad_y \
  --evdev-keymap BTN_A=a,BTN_B=b,BTN_X=y,BTN_Y=x,BTN_TL=lb,BTN_TR=rb,BTN_SELECT=start,BTN_START=back,BTN_THUMBL=tl,BTN_THUMBR=tr \
  --axismap -Y1=Y1,-Y2=Y2

