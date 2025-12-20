import qs.services
import QtQuick
import qs.modules.ii.onScreenDisplay
import qs.modules.ii.bar

OsdValueIndicator {
    id: osdValues
    value: Media.activePlayer?.volume ?? 0
    icon: Media.activePlayer?.muted ? "volume_off" : "volume_up"
    name: Translation.tr("Volume")
}
