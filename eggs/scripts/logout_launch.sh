#!/usr/bin/env sh


#// Check if wlogout is already running

if pgrep -x "wlogout" > /dev/null
then
    pkill -x "wlogout"
    exit 0
fi


#// set file variables
scrDir=`dirname "$(realpath "$0")"`
[ -z "${1}" ] || wlogoutStyle="${1}"
wLayout="${confDir:-$HOME/.config}/wlogout/layout_${wlogoutStyle}"
wlTmplt="${confDir:-$HOME/.config}/wlogout/style_${wlogoutStyle}.css"

if [ ! -f "${wLayout}" ] || [ ! -f "${wlTmplt}" ] ; then
    echo "ERROR: Config ${wlogoutStyle} not found..."
    wlogoutStyle=1
    wLayout="${confDir:-$HOME/.config}/wlogout/layout_${wlogoutStyle}"
    wlTmplt="${confDir:-$HOME/.config}/wlogout/style_${wlogoutStyle}.css"
fi


#// detect monitor res

x_mon=$(hyprctl -j monitors | jq '.[] | select(.focused==true) | .width')
y_mon=$(hyprctl -j monitors | jq '.[] | select(.focused==true) | .height')
hypr_scale=$(hyprctl -j monitors | jq '.[] | select (.focused == true) | .scale' | sed 's/\.//')


#// scale config layout and style

case "${wlogoutStyle}" in
    1)  wlColms=6
        export mgn=$(( y_mon * 28 / hypr_scale ))
        export hvr=$(( y_mon * 23 / hypr_scale )) ;;
    2)  wlColms=2
        export x_mgn=$(( x_mon * 35 / hypr_scale ))
        export y_mgn=$(( y_mon * 25 / hypr_scale ))
        export x_hvr=$(( x_mon * 32 / hypr_scale ))
        export y_hvr=$(( y_mon * 20 / hypr_scale )) ;;
esac


#// scale font size
export fntSize=$(( y_mon * 2 / 100 ))

#// eval hypr border radius
hypr_border=12

export active_rad=$(( hypr_border * 5 ))
export button_rad=$(( hypr_border * 8 ))


#// eval config files
wlStyle="$(envsubst < $wlTmplt)"


#// launch wlogout
wlogout -b "${wlColms}" -c 0 -r 0 -m 0 --layout "${wLayout}" --css <(echo "${wlStyle}") --protocol layer-shell

