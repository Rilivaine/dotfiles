#!/usr/bin/env python3
import sys
import os
import json
import signal
import argparse
import logging

import gi
gi.require_version("Playerctl", "2.0")
from gi.repository import Playerctl, GLib


# -------- utils --------

def _write_output(text: str, player_name: str, tooltip: str = ""):
    payload = {
        "text": text,
        "class": f"custom-{player_name}",
        "alt": player_name,
        "tooltip": tooltip or text,
    }
    sys.stdout.write(json.dumps(payload) + "\n")
    sys.stdout.flush()


def _fmt_time(us: int) -> str:
    if not us or us <= 0:
        return ""
    s = us // 1_000_000
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    return f"{h:d}:{m:02d}:{s:02d}" if h else f"{m:d}:{s:02d}"


def signal_term_handler(*_):
    sys.stdout.write("\n")
    sys.stdout.flush()
    sys.exit(0)


# -------- main controller --------

class WaybarPlayerctl:
    def __init__(self, player_filter=None, show_time=True):
        self.filter = player_filter.lower() if player_filter else None
        self.show_time = show_time

        self.manager = Playerctl.PlayerManager()
        self.loop = GLib.MainLoop()

        self.manager.connect("name-appeared", self._on_name_appeared)
        self.manager.connect("player-vanished", self._on_player_vanished)

    # ---- lifecycle ----

    def start(self):
        signal.signal(signal.SIGINT, signal_term_handler)
        signal.signal(signal.SIGTERM, signal_term_handler)

        self._discover_players()
        GLib.idle_add(self._check_initial)
        self.loop.run()

    def _discover_players(self):
        for pname in self.manager.props.player_names:
            if self.filter and pname.name.lower() != self.filter:
                continue
            self._attach_player(pname)

    def _attach_player(self, pname):
        player = Playerctl.Player.new_from_name(pname)
        player.connect("playback-status", self._on_update)
        player.connect("metadata", self._on_update)
        self.manager.manage_player(player)

        # poll position every second (playerctl has no position signal)
        if self.show_time:
            GLib.timeout_add_seconds(1, self._tick, player)

    # ---- initial / fallback ----

    def _check_initial(self):
        names = [p.name.lower() for p in self.manager.props.player_names]
        if self.filter and self.filter not in names:
            _write_output(f"No {self.filter.title()} instance", self.filter)
        elif not names:
            _write_output("No media players found", "playerctl")
        else:
            self._show_active()
        return False

    def _show_active(self):
        players = self.manager.props.players[::-1]
        active = next((p for p in players if p.props.status.lower() == "playing"), None)
        target = active or (players[0] if players else None)
        if target:
            self._update_output(target)
        else:
            sys.stdout.write("\n")

    # ---- signals ----

    def _on_name_appeared(self, _, pname):
        if self.filter and pname.name.lower() != self.filter:
            return
        self._attach_player(pname)
        self._show_active()

    def _on_player_vanished(self, *_):
        names = [p.name.lower() for p in self.manager.props.player_names]
        if self.filter and self.filter not in names:
            _write_output(f"No {self.filter.title()} instance", self.filter)
        else:
            self._show_active()

    def _on_update(self, player, *_):
        # metadata / playback-status update
        self._update_output(player)

    def _tick(self, player):
        # keep updating only while player exists
        if player not in self.manager.props.players:
            return False
        if self.show_time:
            self._update_output(player)
        return True

    # ---- rendering ----

    def _update_output(self, player):
        name = player.props.player_name.lower()
        status = player.props.status.lower()

        artist = player.get_artist() or ""
        title = player.get_title() or ""

                # duration (µs) from metadata (player-dependent type)
        length_us = 0
        try:
            v = player.props.metadata.lookup_value("mpris:length", None)
            if v is not None:
                # can be int64 ('x') or uint64 ('t') depending on player
                length_us = int(v.unpack())
        except Exception:
            length_us = 0

        # current position (µs)
        try:
            pos_us = player.get_position()
        except Exception:
            pos_us = 0

        # spotify ads
        try:
            trackid_v = player.props.metadata.lookup_value(
                "mpris:trackid", GLib.VariantType.new("s")
            )
            trackid = trackid_v.get_string()
        except Exception:
            trackid = ""

        if name == "spotify" and ":ad:" in trackid:
            text = "Advertisement"
            time_part = ""
        else:
            text = f"{artist} - {title}" if artist and title else title
            time_part = (
                f"{_fmt_time(pos_us)}/{_fmt_time(length_us)}"
                if self.show_time and (pos_us or length_us)
                else ""
            )

        icon = "" if status == "playing" else ""
        display = f"{icon} {text} | {time_part}" if text else ""

        _write_output(display, name, tooltip=display)


# -------- cli --------

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--player", help="filter to a specific player")
    p.add_argument("--no-time", action="store_true", help="disable time display")
    p.add_argument("-v", "--verbose", action="count", default=0)
    p.add_argument("--enable-logging", action="store_true")
    return p.parse_args()


def main():
    args = parse_args()

    level = max((3 - args.verbose) * 10, logging.WARNING)
    if args.enable_logging:
        log_file = os.path.join(os.path.dirname(__file__), "media-player.log")
        logging.basicConfig(
            filename=log_file,
            level=logging.DEBUG,
            format="%(asctime)s %(levelname)s:%(message)s",
        )
    logging.getLogger().setLevel(level)

    controller = WaybarPlayerctl(
        player_filter=args.player,
        show_time=not args.no_time,
    )
    controller.start()


if __name__ == "__main__":
    main()
